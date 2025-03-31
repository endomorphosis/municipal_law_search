from __future__ import annotations
import os
import sqlite3
import duckdb
from typing import Union, Any

from chatbot.configs import configs

embeddings_db_path = configs.AMERICAN_LAW_DATA_DIR / "american_law.db"


def setup_embeddings_db(db_path=None, use_duckdb=True) -> Union[sqlite3.Connection, duckdb.DuckDBPyConnection]:
    """
    Set up the embeddings database schema.
    
    Args:
        db_path: Optional path to database file, defaults to embeddings_db_path
        use_duckdb: Whether to use DuckDB (True) or SQLite (False)
        
    Returns:
        Database connection object
    """
    # Use default path if none provided
    db_path = db_path or embeddings_db_path
    
    # Use DuckDB if requested, otherwise fallback to SQLite
    if use_duckdb:
        return _setup_embeddings_db_duckdb(db_path)
    else:
        return _setup_embeddings_db_sqlite(db_path)


def _setup_embeddings_db_sqlite(db_path: str) -> sqlite3.Connection:
    """Setup embeddings database with SQLite."""
    conn = None
    try:
        if not os.path.exists(db_path):
            # Connect to SQLite database
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Create embeddings table that stores filepath to parquet files
            cursor.execute('''
            CREATE TABLE embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                embedding_cid TEXT NOT NULL,
                gnis TEXT NOT NULL,
                cid TEXT NOT NULL,
                text_chunk_order INTEGER NOT NULL,
                embedding_filepath TEXT NOT NULL,
                index_level_0 INTEGER
            )
            ''')
            
            # Commit changes
            conn.commit()
            print("Embeddings database created successfully with SQLite.")
        else:
            # Connect to SQLite database if it exists
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            
            print("Embeddings database already exists in SQLite.")
    except Exception as e:
        print(f"Error setting up embeddings database with SQLite: {e}")
        if conn:
            conn.close()
        raise e
    
    return conn


def _setup_embeddings_db_duckdb(db_path: str) -> duckdb.DuckDBPyConnection:
    """Setup embeddings database with DuckDB."""
    # Connect to DuckDB database
    conn = duckdb.connect(db_path)
    
    try:
        # Check if table exists
        result = conn.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name='embeddings'
        ''').fetchone()
        
        if not result:
            # Create embeddings table that stores filepath to parquet files
            conn.execute('''
            CREATE TABLE embeddings (
                id INTEGER PRIMARY KEY,
                embedding_cid VARCHAR NOT NULL,
                gnis VARCHAR NOT NULL,
                cid VARCHAR NOT NULL,
                text_chunk_order INTEGER NOT NULL,
                embedding_filepath VARCHAR NOT NULL,
                index_level_0 INTEGER
            )
            ''')
            
            # Create a sequence for auto-incrementing IDs
            conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_embeddings_id")
            
            print("Embeddings database created successfully with DuckDB.")
        else:
            print("Embeddings database already exists in DuckDB.")
    except Exception as e:
        print(f"Error setting up embeddings database with DuckDB: {e}")
        if conn:
            conn.close()
        raise e
    
    return conn