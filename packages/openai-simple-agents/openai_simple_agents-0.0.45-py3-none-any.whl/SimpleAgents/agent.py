from typing import Optional, List  # Аннотации типов
from agents import Agent as BaseAgent, Runner, RunConfig  # Импорт базового агента и исполнительной среды
import asyncio
from .memory_manager import MemoryManager  # Импорт менеджера памяти
import uuid
import re
import unicodedata
import logging  # Логгирование
global_metadata = {}
# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Преобразование имени агента в безопасный ID
def normalize_agent_id(name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    cleaned = re.sub(r'[^a-zA-Z0-9._-]', '_', ascii_name)
    if not cleaned or not re.match(r'^[a-zA-Z0-9]', cleaned):
        cleaned = f"agent_{uuid.uuid4().hex[:8]}"
    return cleaned[:64]  # ограничение длины ID

# Основной класс агента, расширяющий базовый функционал
class Agent(BaseAgent):
    def __init__(
        self,
        name: str,
        *,
        openai_api_key: str = "...",
        ttl_seconds: Optional[int] = None,
        short_memory_max_pairs: int = 10,
        short_memory_ttl_minutes: int = 60,
        short_memory_cleanup_minutes: int = 10,
        max_turns: int = 5,
        **kwargs
    ):
        logger.debug(f"[Agent][__init__] получено имя агента: {name}")
        super().__init__(name=name, **kwargs)

        self.max_turns = max_turns  # Максимальное число reasoning-итераций
        normalized_id = normalize_agent_id(name)  # Преобразуем имя в безопасный ID

        logger.debug(f"[Agent][__init__] нормализованный ID агента: {normalized_id}")

        # Инициализация менеджера памяти
        self.memory_manager = MemoryManager(
            agent_id=normalized_id,
            openai_api_key=openai_api_key,
            long_memory_ttl=ttl_seconds,
            short_memory_max_pairs=short_memory_max_pairs,
            short_memory_ttl_minutes=short_memory_ttl_minutes,
            short_memory_cleanup_minutes=short_memory_cleanup_minutes,
        )

        self._initialized = False  # Флаг инициализации

    async def init(self):
        # Однократная инициализация менеджера памяти
        if self._initialized:
            logger.debug("[Agent][init] уже инициализирован")
            return
        logger.debug("[Agent][init] запускаем инициализацию MemoryManager")
        await self.memory_manager.init()
        self._initialized = True
        logger.debug("[Agent][init] инициализация завершена")

    async def message(
            self,
            input: str,
            *,
            context=None,
            tool_choice: Optional[str] = None,
            max_turns: Optional[int] = None,
            enable_tracing: bool = True,
            tags: Optional[List[str]] = None,
            user_id: Optional[str] = None,
            file_name: Optional[str] = None,
            file_path: Optional[str] = None,
    ):
        logger.debug(f"[Agent][message] получен ввод: {input}")
        await self.init()

        max_turns = max_turns or self.max_turns

        # Получаем память для данного запроса
        memory_context = await self.memory_manager.get_memory_context(user_id=user_id, input=input)

        # 🔍 Логгируем извлечённый memory_context
        if memory_context:
            logger.debug(f"[Agent][message] извлечён memory_context:\n{memory_context}")
        else:
            logger.debug("[Agent][message] память пуста или не извлечена")

        # Формируем prompt с учетом памяти
        if memory_context:
            augmented_input = (
                f"Ты — интеллектуальный агент, ведущий диалог с пользователем с ID: {user_id}.\n"
                f"У тебя есть доступ к двум типам памяти для этого пользователя:\n"
                f"1. 🧠 Краткосрочная память — содержит последние сообщения из диалога.\n"
                f"2. 📚 Долговременная память — содержит знания из прошлых взаимодействий.\n\n"
                f"Используй обе памяти, чтобы понять контекст и дать точный, персонализированный ответ.\n\n"
                f"{memory_context}\n\n"
                f"Теперь ответь на вопрос пользователя:\n{input}"
            )
            logger.debug("[Agent][message] сформирован prompt с памятью")
        else:
            augmented_input = input
            logger.debug("[Agent][message] памяти нет, используется сырой ввод")

        # 🔍 Логгируем финальный prompt
        logger.debug(f"[Agent][message] финальный prompt:\n{augmented_input}")

        # Собираем метаданные
        merged_metadata = {}
        if context and hasattr(context, "metadata") and context.metadata:
            merged_metadata.update(context.metadata)
        for k, v in (("user_id", user_id), ("file_name", file_name), ("file_path", file_path)):
            if v is not None:
                merged_metadata[k] = str(v)
                global_metadata[k] = str(v)

        if file_name is None or file_path is None:
            if global_metadata:
                for key_num, key in enumerate(global_metadata.keys()):
                    value = global_metadata[key]
                    merged_metadata[key] = str(value)
                global_metadata.clear()

        trace_meta = {}
        if tool_choice is not None:
            merged_metadata["tool_choice"] = tool_choice
            trace_meta["tool_choice"] = tool_choice
        if tags:
            merged_metadata["tags"] = tags
            trace_meta["tags"] = tags

        # Создаем временный объект контекста, если он не передан
        if context is None:
            context = type("Ctx", (), {})()
        context.metadata = merged_metadata or None

        logger.debug(f"[Agent][message] подготовлены метаданные: {merged_metadata}")

        # Конфигурация запуска reasoning-цепочки
        run_cfg = RunConfig(
            tracing_disabled=not enable_tracing,
            trace_metadata=trace_meta if trace_meta else None,
            workflow_name=f"Workflow_{str(user_id)}"
        )

        logger.debug(f"[Agent][message] запускаем Runner с max_turns={max_turns}")

        result = await Runner.run(
            starting_agent=self,
            input=augmented_input,
            context=context,
            max_turns=max_turns,
            run_config=run_cfg,
        )
        text_result = result.final_output

        logger.debug("[Agent][message] reasoning завершён, сохраняем результат в память")
        try:
            await self.memory_manager.record_interaction(user_id=user_id, input=input, output=text_result, file_name=file_name, file_path=file_path)
            logger.debug("[Agent][message] Результат успешно сохранён в память, возвращаю результат")
        except Exception as e:
            logger.debug(f"[Agent][message] Не удалось сохранить результат в память, ошибка: {e}")
        return text_result