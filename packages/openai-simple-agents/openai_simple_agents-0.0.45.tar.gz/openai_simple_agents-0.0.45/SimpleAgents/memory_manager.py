import asyncio  # Модуль для асинхронного программирования
import uuid  # Генератор уникальных идентификаторов
from typing import Optional, List, Dict  # Аннотации типов

import logging  # Модуль логгирования

from .short_memory import ShortMemory  # Импорт модуля кратковременной памяти
from .long_memory import LongMemory  # Импорт модуля долговременной памяти

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Класс, инкапсулирующий работу с кратковременной и долговременной памятью
class MemoryManager:
    def __init__(
            self,
            agent_id: str,  # Уникальный идентификатор агента
            openai_api_key: str,  # API-ключ для OpenAI
            *,
            long_memory_ttl: Optional[int] = None,  # TTL для долговременной памяти (в секундах)
            short_memory_max_pairs: int = 10,  # Макс. число пар user/agent в кратковременной памяти
            short_memory_ttl_minutes: int = 60,  # TTL кратковременной памяти (в минутах)
            short_memory_cleanup_minutes: int = 10,  # Интервал очистки кратковременной памяти
    ):
        logger.debug(
            f"[MemoryManager][__init__] получил аргументы: agent_id={agent_id}, long_memory_ttl={long_memory_ttl}, short_memory_max_pairs={short_memory_max_pairs}, short_memory_ttl_minutes={short_memory_ttl_minutes}, short_memory_cleanup_minutes={short_memory_cleanup_minutes}")
        self.agent_id = agent_id  # Сохраняем идентификатор агента

        # Инициализация долговременной памяти (ChromaDB)
        self.long_memory = LongMemory(
            collection_name=f"long_memory_{agent_id}",
            openai_api_key=openai_api_key,
            ttl_seconds=long_memory_ttl,
        )

        # Инициализация кратковременной памяти (SQLite)
        self.short_memory = ShortMemory(
            max_pairs=short_memory_max_pairs,
            ttl_minutes=short_memory_ttl_minutes,
            cleanup_interval_minutes=short_memory_cleanup_minutes,
            start_auto_cleanup=False  # автоочистку запускаем вручную
        )

        self._cleanup_task = None  # Задача фоновой очистки
        self._cleanup_interval = short_memory_cleanup_minutes * 60  # интервал в секундах
        logger.debug(f"[MemoryManager][__init__] инициализация завершена")

    async def init(self):
        # Инициализация кратковременной памяти и запуск фоновой задачи очистки
        logger.debug(f"[MemoryManager][init] инициализация кратковременной памяти")
        await self.short_memory.init()
        self._start_auto_cleanup()

    def _start_auto_cleanup(self):
        # Запускаем фоновую задачу очистки, если она ещё не активна
        logger.debug(f"[MemoryManager][_start_auto_cleanup] запуск фоновой задачи")
        if self._cleanup_task is not None:
            logger.debug(f"[MemoryManager][_start_auto_cleanup] задача уже запущена")
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        self._cleanup_task = loop.create_task(self._auto_cleanup_loop())

    async def _auto_cleanup_loop(self):
        # Бесконечный цикл: через указанный интервал вызывается очистка памяти
        logger.debug(f"[MemoryManager][_auto_cleanup_loop] старт цикла автоочистки")
        while True:
            await asyncio.sleep(self._cleanup_interval)
            await self.cleanup()

    async def shutdown(self):
        # Корректная остановка фоновой задачи
        logger.debug(f"[MemoryManager][shutdown] остановка фоновой задачи очистки")
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
                logger.debug(f"[MemoryManager][shutdown] фоновая задача остановлена")
            except asyncio.CancelledError:
                logger.debug(f"[MemoryManager][shutdown] задача была отменена")

    async def cleanup(self):
        # Очистка устаревших данных как в краткосрочной, так и в долговременной памяти
        logger.debug(f"[MemoryManager][cleanup] старт очистки")
        await self.short_memory.cleanup_expired_dialogs()
        await self.long_memory.cleanup_expired()
        logger.debug(f"[MemoryManager][cleanup] очистка завершена")

    async def get_memory_context(self, user_id: Optional[str], input: str) -> str:
        """
        Получает срез памяти для текущего пользователя и запроса.
        Объединяет записи из кратковременной и долговременной памяти
        """
        logger.debug(f"[MemoryManager][get_memory_context] получил аргументы: user_id={user_id}, input={input}")
        memory_context_parts = []  # Список частей контекста

        # Получаем релевантные записи из долговременной памяти
        if user_id:
            memory_records = await self.long_memory.query_by_metadata(
                filter={"user_id": user_id},
                text=input,
                top_k=3,
            )
        else:
            memory_records = await self.long_memory.query_similar(text=input, top_k=3)

        # Формируем текстовый блок из долговременной памяти
        if memory_records:
            long_context = "\n".join([f"- {r['text']}" for r in memory_records])
            memory_context_parts.append(f"[Долговременная память (user_id={user_id})]\n{long_context}")

        # Получаем историю диалога из кратковременной памяти
        if user_id:
            short_history = await self.short_memory.get_history(user_id=user_id, agent_id=self.agent_id)
            if short_history:
                short_context = "\n".join(
                    [f"Пользователь: {pair['user']}\nАгент: {pair.get('agent', '')}" for pair in short_history]
                )
                memory_context_parts.append(f"[Краткосрочная память (user_id={user_id})]\n{short_context}")

        result = "\n\n".join(memory_context_parts)
        logger.debug(f"[MemoryManager][get_memory_context] вернул контекст длиной {len(result)} символов")
        return result

    async def record_interaction(self, *, user_id: Optional[str], input: str, output: str, file_name=None,
                                 file_path=None):
        """
        Сохраняет факт взаимодействия с пользователем:
        - в кратковременную память добавляются пары запрос/ответ
        - в долговременную память сохраняются те же фразы с метаданными
        """
        logger.debug(
            f"[MemoryManager][record_interaction] получил аргументы: user_id={user_id}, input={input}, output={output}, file_name={file_name}, file_path={file_path}")

        if user_id:
            # Сохраняем запрос и ответ в краткосрочную память
            await self.short_memory.add_message(user_id=user_id, agent_id=self.agent_id, message=input, role="user")
            await self.short_memory.add_message(user_id=user_id, agent_id=self.agent_id, message=output, role="agent")

        # Формируем метаданные, если значения не None
        common_md = {k: v for k, v in (("user_id", user_id), ("file_name", file_name), ("file_path", file_path)) if
                     v is not None}

        # Добавляем запрос и ответ в долговременную память по отдельности
        await self.long_memory.add_record(text=input, metadata={**common_md, "role": "user"})
        await self.long_memory.add_record(text=output, metadata={**common_md, "role": "assistant"})
        logger.debug(f"[MemoryManager][record_interaction] запись завершена")
