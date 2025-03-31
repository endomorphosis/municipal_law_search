from __future__ import annotations
import os
import sqlite3

from chatbot.configs import configs

html_db_path = configs.AMERICAN_LAW_DATA_DIR / "american_law.db"


# Create HTML database
def setup_html_db(): 
    try:
        if not html_db_path.exists():
            # Connect to SQLite database
            conn = sqlite3.connect(html_db_path)
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
            
            # Commit changes and close connection
            conn.commit()
            conn.close()
            print("HTML database created successfully.")
        else:
            print("HTML database already exists.")
    finally:
        pass
