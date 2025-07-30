import chromadb
from chromadb.api.models.Collection import Collection
from openai import OpenAI
from typing import List, Optional, Dict
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import uuid
import time
import os
import asyncio
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ChromaClientFactory:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is not None:
            return cls._client
        env = os.getenv("APP_ENV", "production").lower()
        if env == "test":
            cls._client = chromadb.EphemeralClient()
        else:
            persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
            cls._client = chromadb.PersistentClient(path=persist_dir)
        return cls._client

class LongMemory:
    def __init__(self, collection_name: str = "long_term_memory", openai_api_key: str = "...", ttl_seconds: Optional[int] = None, client=None):
        self.openai = OpenAI(api_key=openai_api_key)
        self.embedding_fn = OpenAIEmbeddingFunction(api_key=openai_api_key, model_name="text-embedding-3-small")
        self.client = client or ChromaClientFactory.get_client()
        self.collection: Collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine", "hnsw:M": 32, "hnsw:construction_ef": 128},
            embedding_function=self.embedding_fn
        )
        self.ttl_seconds = ttl_seconds
        self._locks = defaultdict(asyncio.Lock)

    def _log_exception(self, message: str, exc: Exception):
        logger.exception(f"[LongMemory] {message}: {type(exc).__name__} - {exc}")

    def _adaptive_top_k(self, text: str, max_k: int = 5) -> int:
        length = len(text)
        if length < 100:
            return 1
        elif length < 300:
            return 3
        return max_k

    def _current_timestamp(self) -> float:
        return time.time()

    def _is_expired(self, last_used: float, threshold: float) -> bool:
        return last_used < threshold

    async def query_by_metadata(self, filter: Dict, text: str, top_k: int = 3) -> List[dict]:
        logger.debug(f"[LongMemory][query_by_metadata] получил аргументы: filter={filter}, text={text}, top_k={top_k}")
        try:
            adaptive_k = self._adaptive_top_k(text, top_k)
            results = self.collection.query(query_texts=[text], n_results=adaptive_k, where=filter)
            for i in range(len(results["ids"][0])):
                await self._touch_record(results["ids"][0][i])
            output = [
                {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
                for i in range(len(results["documents"][0]))
                if not self._is_expired(results["metadatas"][0][i].get("_last_used", 0), self._current_timestamp() - (self.ttl_seconds or 0))
            ]
            logger.debug(f"[LongMemory][query_by_metadata] вернул результат: {output}")
            return output
        except Exception as e:
            self._log_exception("query_by_metadata failed", e)
            return []

    async def _touch_record(self, record_id: str):
        logger.debug(f"[LongMemory][_touch_record] обновление _last_used для записи: {record_id}")
        lock = self._locks[record_id]
        async with lock:
            try:
                record = self.collection.get(ids=[record_id])
                if record["metadatas"]:
                    metadata = record["metadatas"][0]
                    metadata["_last_used"] = self._current_timestamp()
                    text = record["documents"][0]
                    self.collection.update(ids=[record_id], documents=[text], metadatas=[metadata])
            except Exception as e:
                self._log_exception(f"_touch_record failed for {record_id}", e)

    async def add_record(self, text: str, metadata: Optional[Dict] = None, record_id: Optional[str] = None) -> str:
        logger.debug(f"[LongMemory][add_record] получил аргументы: text={text}, record_id={record_id}, metadata={metadata}")
        record_id = record_id or str(uuid.uuid4())

        metadata = metadata or {}
        metadata["_created"] = self._current_timestamp()
        metadata["_last_used"] = metadata["_created"]
        try:
            self.collection.add(documents=[text], ids=[record_id], metadatas=[metadata])
            logger.debug(f"[LongMemory][add_record] вернул результат: {record_id}")
            logger.debug(f"[LongMemory][add_record] сохранён текст (первые 100 символов): {text[:100]}")
            logger.debug(f"[LongMemory][add_record] сохранённые метаданные: {metadata}")
            return record_id
        except Exception as e:
            self._log_exception("add_record failed", e)
            return ""

    async def get_all_records(self, filter: Optional[Dict] = None) -> List[dict]:
        logger.debug(f"[LongMemory][get_all_records] вызван")
        try:
            results = self.collection.get(where=filter) if filter else self.collection.get()
            output = [
                {
                    "id": results["ids"][i],
                    "text": results["documents"][i],
                    "metadata": results["metadatas"][i],
                }
                for i in range(len(results["documents"]))
            ]
            logger.debug(f"[LongMemory][get_all_records] вернул {len(output)} записей")
            for rec in output:
                logger.debug(f"[LongMemory][get_all_records] запись: id={rec['id']}, метаданные={rec['metadata']}, текст={rec['text'][:100]}")
            return output
        except Exception as e:
            self._log_exception("get_all_records failed", e)
            return []
