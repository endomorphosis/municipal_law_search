from __future__ import annotations
import os
import sqlite3

from chatbot.configs import configs

embeddings_db_path = configs.AMERICAN_LAW_DATA_DIR / "american_law.db"


# Create embeddings database
def setup_embeddings_db():
    try:
        if not embeddings_db_path.exists():
            # Connect to SQLite database
            conn = sqlite3.connect(embeddings_db_path)
            cursor = conn.cursor()
            
            # Create embeddings table that stores filepath to parquet files instead of actual embeddings
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

            # Commit changes and close connection
            conn.commit()
            conn.close()
            print("Embeddings database created successfully.")
        else:
            print("Embeddings database already exists.")
    finally:
        pass