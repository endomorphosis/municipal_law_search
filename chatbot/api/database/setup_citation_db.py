from __future__ import annotations
import os
import sqlite3


from chatbot.configs import configs


citation_db_path = configs.AMERICAN_LAW_DATA_DIR / "american_law.db"


def setup_citation_db():
    # Create citation database
    if not citation_db_path.exists():
        # Connect to SQLite database
        conn = sqlite3.connect(citation_db_path)
        cursor = conn.cursor()
        
        # Create citations table based on the README specifications
        cursor.execute('''
        CREATE TABLE citations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bluebook_cid TEXT NOT NULL,
            cid TEXT NOT NULL,
            title TEXT NOT NULL,
            title_num TEXT,
            date TEXT,
            public_law_num TEXT,
            chapter TEXT,
            chapter_num TEXT,
            history_note TEXT,
            ordinance TEXT,
            section TEXT,
            enacted TEXT,
            year TEXT,
            place_name TEXT NOT NULL,
            state_name TEXT NOT NULL,
            state_code TEXT NOT NULL,
            bluebook_state_code TEXT NOT NULL,
            bluebook_citation TEXT NOT NULL,
            index_level_0 INTEGER
        )
        ''')
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        print("Citation database created successfully.")
    else:
        print("Citation database already exists. Testing to see if it is accessible.")
        # Test if the database is accessible
        try:
            # Connect to SQLite database
            conn = sqlite3.connect(citation_db_path)
            cursor = conn.cursor()
            
            # Perform a schema query to check accessibility
            cursor.execute("PRAGMA table_info(citations);")
            result = cursor.fetchone()
            print(result)
            
            if result:
                print("Citation database is accessible.")
            else:
                print("Citation database is not accessible.")
                
            # Close connection
            conn.close()
        except sqlite3.Error as e:
            print(f"Error accessing citation database: {e}")
            raise e