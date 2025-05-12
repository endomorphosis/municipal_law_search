from functools import cached_property, partialmethod
from threading import Lock
from typing import Any, Callable, Generator, Optional, TypeVar, Union
from contextlib import contextmanager

from asyncio import (
    Lock as AsyncLock,
    Queue as AsyncQueue,
)

import duckdb


from logger import logger
from configs import configs, Configs
from api_.database import Database
from api_.database.dependencies.duckdb_database import DuckDbDatabase
from utils.common.run_in_process_pool import run_in_process_pool, async_run_in_process_pool
from utils.llm.cosine_similarity import cosine_similarity

C = TypeVar("C")


class GetDBFromParquetFiles:
    """
    This class is used to get a database from parquet files.
    """

    def __init__(self, resources: dict[str, Callable], configs: Configs = None):
        """
        Initialize the class with the path to the parquet files.

        """
        self.configs = configs
        self.resources = resources

        self._parquet_dir = self.configs.PARQUET_FILES_DIR
        
        self._cosine_similarity = self.resources["cosine_similarity"]

        self._temp_db = self.resources["db"]

        # Initialize gnis file pool
        self._gnis_dict: dict[str, str] = {}
        self._lock: Lock = Lock()

    def _make_gnis_set(self):
        for file in self._parquet_dir.glob("*_embeddings.parquet"):
            gnis = file.stem.split("_")[-1]
            if gnis not in self._gnis_dict.keys():
                self._gnis_dict.update({gnis: file})
            else:
                continue

    def embedding_search(self, gnis_list: list[str], query_embedding: list[float]) -> Generator[None, None, list[tuple[str, str]]]:

        gnis_dict = {gnis: gnis for gnis in gnis_list}

        while gnis_dict:
            if gnis not in self._gnis_dict.keys():
                continue
            else:
                with self._lock:
                    gnis = self._gnis_dict.pop(gnis)
                    _ = gnis_dict.pop(gnis)
            try:
                # run the embedding search on the gnis
                yield self._run_embedding_search(gnis, query_embedding)
            finally:
                # release the gnis by adding it back to the pool
                self._gnis_dict[gnis] = gnis


    def _run_embedding_search(self, gnis: str, query_embedding: list[str], top_k: int = 100) -> list[tuple[str, str]]:
        """
        Run the embedding search on the embeddings parquet.
        """
        duckdb.create_function(
            'cosine_similarity',
            partialmethod(
                self._cosine_similarity,
                query_embedding=query_embedding,
            ),
            ['DOUBLE[1536]', 'DOUBLE[1536]'],
        )
        duckdb.sql(f"""
            SELECT 
                embedding_cid, cid 
            FROM '{gnis}_embeddings.parquet' 
            ORDER BY cosine_similarity(embedding, query_embedding) DESC
            LIMIT {top_k}
        """).fetch_arrow_table


# Export resources dictionary for use with Database class
duckdb_resources = {
    "begin": DuckDbDatabase.begin,
    "close": DuckDbDatabase.close,
    "commit": DuckDbDatabase.commit,
    "connect": DuckDbDatabase.connect,
    "create_function": DuckDbDatabase.create_function,
    "create_index_if_not_exists": DuckDbDatabase.create_index_if_not_exists,
    "create_table_if_not_exists": DuckDbDatabase.create_table_if_not_exists,
    "execute": DuckDbDatabase.execute,
    "execute_script": DuckDbDatabase.execute_script,
    "fetch": DuckDbDatabase.fetch,
    "fetch_all": DuckDbDatabase.fetch_all,
    "fetch_one": DuckDbDatabase.fetch,
    "get_cursor": DuckDbDatabase.get_cursor,
    "rollback": DuckDbDatabase.rollback,
    "read_only": False,  # Set read_only to True for read-only access
}



resources = {
    "cosine_similarity": cosine_similarity,
    "db": Database(configs=configs, resources=duckdb_resources)
}