import os
import sys
import pytest
import tempfile
import sqlite3
import duckdb
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Test SQLite implementation directly
def setup_citation_db_sqlite(db_path):
    """Setup citation database with SQLite."""
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Create citations table based on the README specifications
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS citations (
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
    
    # Commit changes
    conn.commit()
    
    return conn

def setup_html_db_sqlite(db_path):
    """Setup HTML database with SQLite."""
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Create html table based on the README specifications
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS html (
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
    
    return conn

def setup_embeddings_db_sqlite(db_path):
    """Setup embeddings database with SQLite."""
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Create embeddings table that stores filepath to parquet files
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS embeddings (
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
    
    return conn

# Test DuckDB implementation
def setup_citation_db_duckdb(db_path):
    """Setup citation database with DuckDB."""
    # Connect to DuckDB database
    conn = duckdb.connect(db_path)
    
    # Create citations table based on the README specifications
    conn.execute('''
    CREATE TABLE IF NOT EXISTS citations (
        id INTEGER PRIMARY KEY,
        bluebook_cid VARCHAR NOT NULL,
        cid VARCHAR NOT NULL,
        title VARCHAR NOT NULL,
        title_num VARCHAR,
        date VARCHAR,
        public_law_num VARCHAR,
        chapter VARCHAR,
        chapter_num VARCHAR,
        history_note VARCHAR,
        ordinance VARCHAR,
        section VARCHAR,
        enacted VARCHAR,
        year VARCHAR,
        place_name VARCHAR NOT NULL,
        state_name VARCHAR NOT NULL,
        state_code VARCHAR NOT NULL,
        bluebook_state_code VARCHAR NOT NULL,
        bluebook_citation VARCHAR NOT NULL,
        index_level_0 INTEGER
    )
    ''')
    
    # Create a sequence for auto-incrementing IDs
    conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_citations_id")
    
    return conn

def setup_html_db_duckdb(db_path):
    """Setup HTML database with DuckDB."""
    # Connect to DuckDB database
    conn = duckdb.connect(db_path)
    
    # Create html table based on the README specifications
    conn.execute('''
    CREATE TABLE IF NOT EXISTS html (
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
    
    return conn

def setup_embeddings_db_duckdb(db_path):
    """Setup embeddings database with DuckDB."""
    # Connect to DuckDB database
    conn = duckdb.connect(db_path)
    
    # Create embeddings table that stores filepath to parquet files
    conn.execute('''
    CREATE TABLE IF NOT EXISTS embeddings (
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
    
    return conn

class TestDatabaseMigration:
    """Tests for database migration from SQLite to DuckDB."""
    
    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory for test databases."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_sqlite_citation_db_setup(self, temp_db_dir):
        """Test creating and querying the SQLite citation database."""
        # Set up the database in the temp directory
        db_path = str(temp_db_dir / "american_law.db")
        
        # Setup the citation database
        conn = setup_citation_db_sqlite(db_path)
        
        try:
            # Verify table exists
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='citations'")
            table_exists = cursor.fetchone()
            assert table_exists is not None
            
            # Insert test data
            test_data = {
                "bluebook_cid": "test_cid1",
                "cid": "test_cid2",
                "title": "Test Citation",
                "title_num": "123",
                "date": "2023-01-01",
                "place_name": "Test City",
                "state_name": "Test State",
                "state_code": "TS",
                "bluebook_state_code": "T.S.",
                "bluebook_citation": "Test Citation 123"
            }
            
            # Create insert statement
            columns = ", ".join(test_data.keys())
            placeholders = ", ".join(["?" for _ in test_data])
            insert_query = f"INSERT INTO citations ({columns}) VALUES ({placeholders})"
            
            cursor.execute(insert_query, list(test_data.values()))
            conn.commit()
            
            # Verify inserted data
            cursor.execute("SELECT * FROM citations WHERE bluebook_cid=?", ("test_cid1",))
            result = cursor.fetchone()
            assert result is not None
            assert result["title"] == "Test Citation"
        finally:
            conn.close()
    
    def test_duckdb_citation_db_setup(self, temp_db_dir):
        """Test creating and querying the DuckDB citation database."""
        # Set up the database in the temp directory
        db_path = str(temp_db_dir / "american_law_duck.db")
        
        # Setup the citation database
        conn = setup_citation_db_duckdb(db_path)
        
        try:
            # Verify table exists
            result = conn.execute("SELECT * FROM information_schema.tables WHERE table_name='citations'").fetchone()
            assert result is not None
            
            # Insert test data
            test_data = {
                "id": "nextval('seq_citations_id')",  # Use sequence for ID
                "bluebook_cid": "test_cid1",
                "cid": "test_cid2",
                "title": "Test Citation",
                "title_num": "123",
                "date": "2023-01-01",
                "place_name": "Test City",
                "state_name": "Test State",
                "state_code": "TS",
                "bluebook_state_code": "T.S.",
                "bluebook_citation": "Test Citation 123"
            }
            
            # Create insert statement
            columns = ", ".join(test_data.keys())
            values = []
            for k, v in test_data.items():
                if k == "id":
                    values.append(v)
                elif isinstance(v, str):
                    values.append(f"'{v}'")
                elif isinstance(v, int):
                    values.append(str(v))
                else:
                    values.append("NULL")
            
            placeholders = ", ".join(values)
            insert_query = f"INSERT INTO citations ({columns}) VALUES ({placeholders})"
            
            conn.execute(insert_query)
            
            # Verify inserted data
            result = conn.execute("SELECT * FROM citations WHERE bluebook_cid='test_cid1'").fetchone()
            assert result is not None
            assert result[2] == "test_cid2"  # cid field
            assert result[3] == "Test Citation"  # title field
        finally:
            conn.close()
    
    def test_sqlite_html_db_setup(self, temp_db_dir):
        """Test creating and querying the SQLite HTML database."""
        # Set up the database in the temp directory
        db_path = str(temp_db_dir / "american_law.db")
        
        # Setup the HTML database
        conn = setup_html_db_sqlite(db_path)
        
        try:
            # Verify table exists
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='html'")
            table_exists = cursor.fetchone()
            assert table_exists is not None
            
            # Insert test data
            test_data = {
                "cid": "test_html_cid",
                "doc_id": "test_doc_id",
                "doc_order": 1,
                "html_title": "<h1>Test Title</h1>",
                "html": "<div>Test HTML content</div>",
                "index_level_0": 0
            }
            
            # Create insert statement
            columns = ", ".join(test_data.keys())
            placeholders = ", ".join(["?" for _ in test_data])
            insert_query = f"INSERT INTO html ({columns}) VALUES ({placeholders})"
            
            cursor.execute(insert_query, list(test_data.values()))
            conn.commit()
            
            # Verify inserted data
            cursor.execute("SELECT * FROM html WHERE cid=?", ("test_html_cid",))
            result = cursor.fetchone()
            assert result is not None
            assert result["html_title"] == "<h1>Test Title</h1>"
        finally:
            conn.close()
    
    def test_duckdb_html_db_setup(self, temp_db_dir):
        """Test creating and querying the DuckDB HTML database."""
        # Set up the database in the temp directory
        db_path = str(temp_db_dir / "american_law_duck.db")
        
        # Setup the HTML database
        conn = setup_html_db_duckdb(db_path)
        
        try:
            # Verify table exists
            result = conn.execute("SELECT * FROM information_schema.tables WHERE table_name='html'").fetchone()
            assert result is not None
            
            # Insert test data
            test_data = {
                "id": "nextval('seq_html_id')",  # Use sequence for ID
                "cid": "test_html_cid",
                "doc_id": "test_doc_id",
                "doc_order": 1,
                "html_title": "<h1>Test Title</h1>",
                "html": "<div>Test HTML content</div>",
                "index_level_0": 0
            }
            
            # Create insert statement with proper SQL formatting for strings
            columns = ", ".join(test_data.keys())
            values = []
            for k, v in test_data.items():
                if k == "id":
                    values.append(v)
                elif isinstance(v, str):
                    values.append(f"'{v}'")
                elif isinstance(v, int):
                    values.append(str(v))
                else:
                    values.append("NULL")
            
            placeholders = ", ".join(values)
            insert_query = f"INSERT INTO html ({columns}) VALUES ({placeholders})"
            
            conn.execute(insert_query)
            
            # Verify inserted data
            result = conn.execute("SELECT * FROM html WHERE cid='test_html_cid'").fetchone()
            assert result is not None
            assert result[4] == "<h1>Test Title</h1>"  # html_title field
        finally:
            conn.close()

    def test_sqlite_embeddings_db_setup(self, temp_db_dir):
        """Test creating and querying the SQLite embeddings database."""
        # Set up the database in the temp directory
        db_path = str(temp_db_dir / "american_law.db")
        
        # Setup the embeddings database
        conn = setup_embeddings_db_sqlite(db_path)
        
        try:
            # Verify table exists
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='embeddings'")
            table_exists = cursor.fetchone()
            assert table_exists is not None
            
            # Insert test data
            test_data = {
                "embedding_cid": "test_embedding_cid",
                "gnis": "test_gnis",
                "cid": "test_cid",
                "text_chunk_order": 1,
                "embedding_filepath": "test_filepath.parquet",
                "index_level_0": 0
            }
            
            # Create insert statement
            columns = ", ".join(test_data.keys())
            placeholders = ", ".join(["?" for _ in test_data])
            insert_query = f"INSERT INTO embeddings ({columns}) VALUES ({placeholders})"
            
            cursor.execute(insert_query, list(test_data.values()))
            conn.commit()
            
            # Verify inserted data
            cursor.execute("SELECT * FROM embeddings WHERE embedding_cid=?", ("test_embedding_cid",))
            result = cursor.fetchone()
            assert result is not None
            assert result["gnis"] == "test_gnis"
        finally:
            conn.close()

    def test_duckdb_embeddings_db_setup(self, temp_db_dir):
        """Test creating and querying the DuckDB embeddings database."""
        # Set up the database in the temp directory
        db_path = str(temp_db_dir / "american_law_duck.db")
        
        # Setup the embeddings database
        conn = setup_embeddings_db_duckdb(db_path)
        
        try:
            # Verify table exists
            result = conn.execute("SELECT * FROM information_schema.tables WHERE table_name='embeddings'").fetchone()
            assert result is not None
            
            # Insert test data
            test_data = {
                "id": "nextval('seq_embeddings_id')",  # Use sequence for ID
                "embedding_cid": "test_embedding_cid",
                "gnis": "test_gnis",
                "cid": "test_cid",
                "text_chunk_order": 1,
                "embedding_filepath": "test_filepath.parquet",
                "index_level_0": 0
            }
            
            # Create insert statement
            columns = ", ".join(test_data.keys())
            values = []
            for k, v in test_data.items():
                if k == "id":
                    values.append(v)
                elif isinstance(v, str):
                    values.append(f"'{v}'")
                elif isinstance(v, int):
                    values.append(str(v))
                else:
                    values.append("NULL")
            
            placeholders = ", ".join(values)
            insert_query = f"INSERT INTO embeddings ({columns}) VALUES ({placeholders})"
            
            conn.execute(insert_query)
            
            # Verify inserted data
            result = conn.execute("SELECT * FROM embeddings WHERE embedding_cid='test_embedding_cid'").fetchone()
            assert result is not None
            assert result[2] == "test_gnis"  # gnis field
        finally:
            conn.close()