import asyncio
import aiosqlite
import logging
from typing import Optional
from datetime import datetime, timedelta

# Настраиваем логгер
logger = logging.getLogger("ShortMemory")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(name)s][%(funcName)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class ShortMemory:
    def __init__(
        self,
        db_path: str = "short_memory.db",        # Путь к SQLite-файлу
        max_pairs: int = 10,                     # Максимум пар user/agent в истории
        ttl_minutes: int = 60,                   # Время хранения записей
        cleanup_interval_minutes: int = 5,       # Частота автоочистки
        start_auto_cleanup: bool = True,
    ):
        self.db_path = db_path
        self.max_pairs = max_pairs
        self.ttl_minutes = ttl_minutes
        self.cleanup_interval_minutes = cleanup_interval_minutes
        self.start_auto_cleanup = start_auto_cleanup
        self._db: Optional[aiosqlite.Connection] = None
        self._initialization_lock = asyncio.Lock()
        logger.debug(f"Инициализирован с db_path={db_path}, max_pairs={max_pairs}, ttl_minutes={ttl_minutes}, cleanup_interval_minutes={cleanup_interval_minutes}, start_auto_cleanup={start_auto_cleanup}")

    def _log_exception(self, message: str, exc: Exception):
        logger.error(f"{message}: {type(exc).__name__} - {exc}")

    async def init(self):
        logger.debug("Вход в init()")
        async with self._initialization_lock:
            if self._db:
                logger.debug("Подключение к БД уже существует, выходим из init")
                return
            try:
                self._db = await aiosqlite.connect(self.db_path)
                logger.debug("Успешное подключение к БД")

                await self._db.execute("""
                    CREATE TABLE IF NOT EXISTS memory (
                        id INTEGER PRIMARY KEY,
                        user_id TEXT,
                        agent_id TEXT,
                        message TEXT,
                        role TEXT,
                        timestamp TEXT
                    );
                """)
                logger.debug("Таблица memory создана или уже существует")

                await self._db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user_agent_timestamp
                    ON memory (user_id, agent_id, timestamp);
                """)
                logger.debug("Индекс создан или уже существует")

                await self._db.commit()
                logger.debug("Коммит после инициализации выполнен")
            except Exception as e:
                self._log_exception("init failed", e)
                self._db = None

    async def _ensure_db(self):
        logger.debug("Проверка подключения к БД")
        if self._db is None:
            await self.init()
        if self._db is None:
            logger.error("Подключение к базе данных не удалось")
            raise RuntimeError("ShortMemory database is not available.")

    async def close(self):
        logger.debug("Закрытие соединения с БД")
        try:
            if self._db:
                await self._db.close()
                self._db = None
                logger.debug("БД успешно закрыта")
        except Exception as e:
            self._log_exception("close failed", e)

    async def add_message(self, user_id: str, agent_id: str, message: str, role: str):
        logger.debug(f"Добавление сообщения: user_id={user_id}, agent_id={agent_id}, role={role}")
        try:
            await self._ensure_db()
            timestamp = datetime.utcnow().isoformat()
            await self._db.execute(
                "INSERT INTO memory (user_id, agent_id, message, role, timestamp) VALUES (?, ?, ?, ?, ?)",
                (user_id, agent_id, message, role, timestamp)
            )
            logger.debug("Сообщение вставлено")
            await self._db.commit()
            logger.debug("Коммит выполнен")
            await self._enforce_max_pairs(user_id, agent_id)
        except Exception as e:
            self._log_exception("add_message failed", e)

    async def _enforce_max_pairs(self, user_id: str, agent_id: str):
        logger.debug(f"Проверка количества сообщений для user_id={user_id}, agent_id={agent_id}")
        try:
            await self._ensure_db()
            async with self._db.execute("""
                SELECT id FROM memory WHERE user_id = ? AND agent_id = ?
                ORDER BY timestamp DESC
            """, (user_id, agent_id)) as cursor:
                ids = [row[0] async for row in cursor]
            logger.debug(f"Получено {len(ids)} сообщений")
            if len(ids) > self.max_pairs * 2:
                to_delete = ids[self.max_pairs * 2:]
                await self._db.executemany("DELETE FROM memory WHERE id = ?", [(i,) for i in to_delete])
                await self._db.commit()
                logger.debug(f"Удалено {len(to_delete)} старых сообщений")
        except Exception as e:
            self._log_exception("_enforce_max_pairs failed", e)

    async def get_history(self, user_id: str, agent_id: str):
        logger.debug(f"Получение истории сообщений: user_id={user_id}, agent_id={agent_id}")
        try:
            await self._ensure_db()
            async with self._db.execute("""
                SELECT message, role FROM memory
                WHERE user_id = ? AND agent_id = ?
                ORDER BY timestamp ASC
            """, (user_id, agent_id)) as cursor:
                messages = await cursor.fetchall()
            logger.debug(f"Получено {len(messages)} записей")
            pairs = []
            pair = {}
            for msg, role in messages:
                pair[role] = msg
                if "user" in pair and "agent" in pair:
                    pairs.append(pair)
                    pair = {}
            logger.debug(f"Возвращено {len(pairs)} пар сообщений")
            return pairs
        except Exception as e:
            self._log_exception("get_history failed", e)
            return []

    async def cleanup_expired_dialogs(self):
        logger.debug("Очистка устаревших сообщений")
        try:
            await self._ensure_db()
            expiration_threshold = (datetime.utcnow() - timedelta(minutes=self.ttl_minutes)).isoformat()
            await self._db.execute("DELETE FROM memory WHERE timestamp < ?", (expiration_threshold,))
            await self._db.commit()
            logger.debug("Очистка завершена успешно")
        except Exception as e:
            self._log_exception("cleanup_expired_dialogs failed", e)

