import os
import sqlite3
import duckdb
from typing import Union, Any


from configs import configs


def setup_html_db(db_path=None, use_duckdb=True) -> Union[sqlite3.Connection, duckdb.DuckDBPyConnection]:
    """
    Set up the HTML database schema.
    
    Args:
        db_path: Optional path to database file, defaults to html_db_path
        use_duckdb: Whether to use DuckDB (True) or SQLite (False)
        
    Returns:
        Database connection object
    """
    # Use default path if none provided
    db_path = db_path or configs.AMERICAN_LAW_DATA_DIR / "american_law.db"
    
    # Use DuckDB if requested, otherwise fallback to SQLite
    return _setup_html_db_duckdb(db_path) if use_duckdb else _setup_html_db_sqlite(db_path)


def _setup_html_db_sqlite(db_path: str) -> sqlite3.Connection:
    """Setup HTML database with SQLite."""
    conn = None
    try:
        if not os.path.exists(db_path):
            # Connect to SQLite database
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Create html table based on the README specifications
            cursor.execute('''
            CREATE TABLE html (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cid TEXT NOT NULL,
                doc_id TEXT NOT NULL,
                doc_order INTEGER NOT NULL,
                html_title TEXT NOT NULL,
                html TEXT NOT NULL,
                index_level_0 INTEGER
            )
            ''')
            
            # Commit changes
            conn.commit()
            print("HTML database created successfully with SQLite.")
        else:
            # Connect to SQLite database if it exists
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            
            print("HTML database already exists in SQLite.")
    except Exception as e:
        print(f"Error setting up HTML database with SQLite: {e}")
        if conn:
            conn.close()
        raise e
    
    return conn


def _setup_html_db_duckdb(db_path: str) -> duckdb.DuckDBPyConnection:
    """Setup HTML database with DuckDB."""
    # Connect to DuckDB database
    conn = duckdb.connect(db_path)
    
    try:
        # Check if html table exists
        result = conn.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name='html'
        ''').fetchone()
        
        if not result:
            # Create html table based on the README specifications
            conn.execute('''
            CREATE TABLE html (
                id INTEGER PRIMARY KEY,
                cid VARCHAR NOT NULL,
                doc_id VARCHAR NOT NULL,
                doc_order INTEGER NOT NULL,
                html_title VARCHAR NOT NULL,
                html VARCHAR NOT NULL,
                index_level_0 INTEGER
            )
            ''')
            
            # Create a sequence for auto-incrementing IDs
            conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_html_id")
            
            print("HTML database created successfully with DuckDB.")
        else:
            print("HTML database already exists in DuckDB.")
    except Exception as e:
        print(f"Error setting up HTML database with DuckDB: {e}")
        if conn:
            conn.close()
        raise e
    
    return conn