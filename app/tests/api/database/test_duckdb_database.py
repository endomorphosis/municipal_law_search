"""
Tests for DuckDbDatabase class.

This module contains unit tests for the DuckDB-specific implementation
of database operations in the DuckDbDatabase class.
"""
import os
import tempfile
from typing import Dict, List, Tuple, Any
import unittest
from unittest.mock import patch, MagicMock, call


import duckdb
import pandas as pd


# Import the class to be tested
try:
    from api_.database.dependencies.duckdb_database import DuckDbDatabase
except ImportError: # Damn import errors...
    from app.api_.database.dependencies.duckdb_database import DuckDbDatabase
from configs import configs


class TestDuckDbDatabase(unittest.TestCase):
    """Tests for the DuckDbDatabase class."""

    def setUp(self):
        """Set up test environment before each test."""
        self.db = DuckDbDatabase()
        self.test_table = "test_table"
        
        # Create a real connection for certain tests
        self.conn = DuckDbDatabase.connect(":memory:")

        self.temp_dir = tempfile.TemporaryDirectory(delete=False)
        self.temp_db_path = os.path.join(self.temp_dir.name, "test_duckdb.db")

        # Create a test table for various operations
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value DOUBLE
            )
        """)
        
        # Insert some test data
        self.conn.execute("""
            INSERT INTO test_table VALUES 
            (1, 'Item 1', 10.5),
            (2, 'Item 2', 20.75),
            (3, 'Item 3', 30.0)
        """)

    def tearDown(self):
        """Clean up after each test."""
        # Close the connection
        if hasattr(self, 'conn') and self.conn:
            DuckDbDatabase.close(self.conn)
        # Remove the temporary directory
        self.temp_dir.cleanup()

    def test_read_only_property(self):
        """Test the read_only property getter."""
        # Default should be False
        self.assertFalse(self.db.read_only)

    def test_connect_memory(self):
        """Test connecting to an in-memory database."""
        conn = DuckDbDatabase.connect()
        self.assertIsInstance(conn, duckdb.DuckDBPyConnection)
        DuckDbDatabase.close(conn)

    def test_connect_file(self):
        """Test connecting to a file-based database."""
        # Connect to file
        conn = DuckDbDatabase.connect(self.temp_db_path)
        self.assertIsInstance(conn, duckdb.DuckDBPyConnection)
        DuckDbDatabase.close(conn)
        
        # Verify file was created
        self.assertTrue(os.path.exists(self.temp_db_path))
        
        # Test connecting in read-only mode
        conn = DuckDbDatabase.connect(self.temp_db_path, read_only=True)
        self.assertIsInstance(conn, duckdb.DuckDBPyConnection)
        DuckDbDatabase.close(conn)


    def test_close(self):
        """Test closing a connection using behavior verification."""
        # Create a new connection to the temp file
        conn = DuckDbDatabase.connect(self.temp_db_path)
        
        # Execute a simple query to confirm connection works
        conn.execute("CREATE TABLE IF NOT EXISTS test_close (id INTEGER)")
        conn.execute("INSERT INTO test_close VALUES (1)")
        
        # Close the connection
        DuckDbDatabase.close(conn)
        
        # Verify connection is closed by attempting to use it (should raise an exception)
        with self.assertRaises(Exception):
            conn.execute("SELECT * FROM test_close")

    def test_close_exception(self):
        """Test exception handling when closing a connection."""
        # Create a fake connection object that raises an exception when close is called
        class MockConnection:
            def close(self):
                raise Exception("Test exception")
        
        conn = MockConnection()
        
        # Mock the logger to verify warning is logged
        with patch('logger.logger.warning') as mock_logger:
            # Should not raise an exception
            DuckDbDatabase.close(conn)
            # Should log a warning
            self.assertTrue(mock_logger.called)
            self.assertTrue("Error closing DuckDB connection" in str(mock_logger.call_args))

    def test_execute_without_params(self):
        """Test executing a query without parameters."""
        # Execute a simple query and immediately get results within the method
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM test_table WHERE id = 1")
            result = cursor.fetchdf()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['id'], 1)
        self.assertEqual(result.iloc[0]['name'], 'Item 1')
        self.assertEqual(result.iloc[0]['value'], 10.5)

    def test_execute_with_params_tuple(self):
        """Test executing a query with tuple parameters."""
        # Execute a parameterized query with tuple
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM test_table WHERE id = ?", (2,))
            result = cursor.fetchdf()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['id'], 2)
        self.assertEqual(result.iloc[0]['name'], 'Item 2')

    def test_execute_with_params_dict(self):
        """Test executing a query with dictionary parameters."""
        # Execute a parameterized query with dict
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM test_table WHERE id = $id", {"id": 3})
            result = cursor.fetchdf()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['id'], 3)
        self.assertEqual(result.iloc[0]['value'], 30.0)

    def test_execute_error(self):
        """Test error handling during query execution."""
        with patch('logger.logger.error') as mock_error_log:
            with patch('logger.logger.debug') as mock_debug_log:
                # Execute an invalid query
                with self.assertRaises(Exception):
                    DuckDbDatabase.execute(self.conn, "SELECT * FROM nonexistent_table")
                
                # Verify error was logged
                self.assertTrue(mock_error_log.called)
                self.assertEqual(mock_debug_log.call_count, 2)  # Query and params should be logged

    def test_fetch_records(self):
        """Test fetch method with 'records' format."""
        result = DuckDbDatabase.fetch(
            self.conn,
            "SELECT * FROM test_table ORDER BY id",
            return_format='records'
        )
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)  # Default num_results=1
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[0]['name'], 'Item 1')
    
    def test_fetch_dict(self):
        """Test fetch method with 'dict' format."""
        result = DuckDbDatabase.fetch(
            self.conn,
            "SELECT * FROM test_table ORDER BY id",
            return_format='dict'
        )
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result['id']), 1)  # Default num_results=1
        self.assertEqual(result['id'][0], 1)
        self.assertEqual(result['name'][0], 'Item 1')
    
    def test_fetch_tuple(self):
        """Test fetch method with 'tuple' format."""
        result = DuckDbDatabase.fetch(
            self.conn,
            "SELECT * FROM test_table ORDER BY id",
            return_format='tuple'
        )
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)  # Default num_results=1
        self.assertEqual(result[0][0], 1)  # id
        self.assertEqual(result[0][1], 'Item 1')  # name
    
    def test_fetch_dataframe(self):
        """Test fetch method with 'dataframe' format."""
        result = DuckDbDatabase.fetch(
            self.conn,
            "SELECT * FROM test_table ORDER BY id",
            return_format='dataframe'
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)  # Default num_results=1
        self.assertEqual(result.iloc[0]['id'], 1)
        self.assertEqual(result.iloc[0]['name'], 'Item 1')
    
    def test_fetch_multiple_rows(self):
        """Test fetch method with multiple results."""
        result = DuckDbDatabase.fetch(
            self.conn,
            "SELECT * FROM test_table ORDER BY id",
            num_results=2,
            return_format='records'
        )
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[1]['id'], 2)
    
    def test_fetch_invalid_format(self):
        """Test fetch method with invalid format."""
        with self.assertRaises(ValueError):
            DuckDbDatabase.fetch(
                self.conn,
                "SELECT * FROM test_table",
                return_format='invalid_format'
            )

    def test_fetch_error(self):
        """Test error handling in fetch method."""
        with patch('logger.logger.error') as mock_log:
            with self.assertRaises(Exception):
                # Force a SQL syntax error instead of a "table doesn't exist" error
                # SQL syntax errors are more reliable for testing error handling
                DuckDbDatabase.fetch(
                    self.conn,
                    "SELECT * FROM test_table WHERE;",  # Invalid SQL syntax
                    return_format='records'
                )
            
            # Verify error was logged
            self.assertTrue(mock_log.called)

    def test_fetch_all_records(self):
        """Test fetch_all method with 'records' format."""
        result = DuckDbDatabase.fetch_all(
            self.conn,
            "SELECT * FROM test_table ORDER BY id",
            return_format='records'
        )
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)  # All 3 rows
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[1]['id'], 2)
        self.assertEqual(result[2]['id'], 3)
    
    def test_fetch_all_dict(self):
        """Test fetch_all method with 'dict' format."""
        result = DuckDbDatabase.fetch_all(
            self.conn,
            "SELECT * FROM test_table ORDER BY id",
            return_format='dict'
        )
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result['id']), 3)  # All 3 rows
        self.assertEqual(result['id'][0], 1)
        self.assertEqual(result['id'][1], 2)
        self.assertEqual(result['id'][2], 3)
    
    def test_fetch_all_tuple(self):
        """Test fetch_all method with 'tuple' format."""
        result = DuckDbDatabase.fetch_all(
            self.conn,
            "SELECT * FROM test_table ORDER BY id",
            return_format='tuple'
        )
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)  # All 3 rows
        self.assertEqual(result[0][0], 1)  # First row, id column
        self.assertEqual(result[1][0], 2)  # Second row, id column
        self.assertEqual(result[2][0], 3)  # Third row, id column
    
    def test_fetch_all_dataframe(self):
        """Test fetch_all method with 'dataframe' format."""
        result = DuckDbDatabase.fetch_all(
            self.conn,
            "SELECT * FROM test_table ORDER BY id",
            return_format='dataframe'
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)  # All 3 rows
        self.assertEqual(result.iloc[0]['id'], 1)
        self.assertEqual(result.iloc[1]['id'], 2)
        self.assertEqual(result.iloc[2]['id'], 3)
    
    def test_fetch_all_invalid_format(self):
        """Test fetch_all method with invalid format."""
        with self.assertRaises(ValueError):
            DuckDbDatabase.fetch_all(
                self.conn,
                "SELECT * FROM test_table",
                return_format='invalid_format'
            )
    
    def test_fetch_all_error(self):
        """Test error handling in fetch_all method."""
        with patch('logger.logger.error') as mock_log:
            # Should return empty list on error
            result = DuckDbDatabase.fetch_all(
                self.conn,
                "SELECT * FROM nonexistent_table"
            )
            
            # Verify error was logged and empty list returned
            self.assertTrue(mock_log.called)
            self.assertEqual(result, [])


    def test_begin_transaction_error(self):
        """Test error handling when beginning a transaction."""
        conn = None
        try:
            # Force an exception by trying to begin a transaction on a closed connection
            conn = duckdb.connect(":memory:")
            conn.close()  # Close the connection to force an error
            
            # This should now raise an exception
            with patch('logger.logger.error') as mock_log:
                with self.assertRaises(Exception):
                    DuckDbDatabase.begin(conn)
                
                # Since we're forcing an actual error with the closed connection,
                # the error should be logged
                self.assertTrue(mock_log.called)
        finally:
            if conn:
                conn.close()

    def test_commit_transaction(self):
        """Test committing a transaction using behavior verification."""
        trans_conn = DuckDbDatabase.connect(self.temp_db_path)
        
        # Create a test table
        trans_conn.execute("CREATE TABLE test_commit (id INTEGER)")
        
        # Begin transaction
        DuckDbDatabase.begin(trans_conn)
        
        # Insert data
        trans_conn.execute("INSERT INTO test_commit VALUES (1)")

        # Commit the transaction
        DuckDbDatabase.commit(trans_conn)

        # Close the connection since duckdb doesn't concurrency with a writable database.
        DuckDbDatabase.close(trans_conn)

        # Verify data was committed by opening a new connection and checking
        new_conn = DuckDbDatabase.connect(self.temp_db_path)

        # Query the data
        result = new_conn.execute("SELECT * FROM test_commit").fetchdf()
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['id'], 1)
        
        # Close the new connection
        DuckDbDatabase.close(new_conn)

    def test_commit_transaction_error(self):
        """Test error handling when committing a transaction."""
        conn = None
        try:
            # Force an exception by trying to commit on a closed connection
            conn = duckdb.connect(":memory:")
            conn.close()  # Close the connection to force an error
            
            # This should now raise an exception
            with patch('logger.logger.error') as mock_log:
                with self.assertRaises(Exception):
                    DuckDbDatabase.commit(conn)
                
                # Since we're forcing an actual error with the closed connection,
                # the error should be logged
                self.assertTrue(mock_log.called)
        finally:
            if conn:
                conn.close()

    def test_rollback_transaction(self):
        """Test rolling back a transaction using behavior verification."""
        # Create a test table
        self.conn.execute("CREATE TABLE test_rollback (id INTEGER)")
        
        # Insert initial data
        self.conn.execute("INSERT INTO test_rollback VALUES (1)")
        
        # Begin transaction
        DuckDbDatabase.begin(self.conn)
        
        # Make changes in the transaction
        self.conn.execute("INSERT INTO test_rollback VALUES (2)")
        
        # Verify the change is visible within the transaction
        result = self.conn.execute("SELECT COUNT(*) AS count FROM test_rollback").fetchdf()
        self.assertEqual(result.iloc[0]['count'], 2)
        
        # Rollback the transaction
        DuckDbDatabase.rollback(self.conn)
        
        # Verify the change was rolled back
        result = self.conn.execute("SELECT COUNT(*) AS count FROM test_rollback").fetchdf()
        self.assertEqual(result.iloc[0]['count'], 1)
        
        # Verify only the original data remains
        result = self.conn.execute("SELECT id FROM test_rollback").fetchdf()
        self.assertEqual(result.iloc[0]['id'], 1)

    def test_rollback_transaction_error(self):
        """Test error handling when rolling back a transaction."""
        # Create a new connection to the temp file
        conn = DuckDbDatabase.connect(self.temp_db_path)
        
        # Without begin(), rollback() should fail
        with patch('logger.logger.error') as mock_log:
            with self.assertRaises(Exception):
                # Rollback without begin should fail
                DuckDbDatabase.rollback(conn)
            
            # Verify error was logged
            self.assertTrue(mock_log.called)
        
        # Clean up
        DuckDbDatabase.close(conn)

    def test_begin_and_commit_transaction(self):
        """Test beginning and committing a transaction using behavior verification."""
        # Create a new connection to the temp file
        conn = DuckDbDatabase.connect(self.temp_db_path)
        
        # Create test table
        conn.execute("CREATE TABLE IF NOT EXISTS test_transaction (id INTEGER)")
        
        # Begin transaction
        DuckDbDatabase.begin(conn)
        
        # Insert data
        conn.execute("INSERT INTO test_transaction VALUES (1)")
        
        # Commit transaction
        DuckDbDatabase.commit(conn)
        
        # Verify data was committed by querying it
        result = conn.execute("SELECT * FROM test_transaction").fetchdf()
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['id'], 1)
        
        # Clean up
        DuckDbDatabase.close(conn)

    def test_begin_and_rollback_transaction(self):
        """Test beginning and rolling back a transaction using behavior verification."""
        # Create a new connection to the temp file
        conn = DuckDbDatabase.connect(self.temp_db_path)
        
        # Create test table
        conn.execute("CREATE TABLE IF NOT EXISTS test_rollback (id INTEGER)")
        
        # Begin transaction
        DuckDbDatabase.begin(conn)
        
        # Insert data
        conn.execute("INSERT INTO test_rollback VALUES (2)")
        
        # Verify data is visible within transaction
        result = conn.execute("SELECT * FROM test_rollback").fetchdf()
        self.assertEqual(len(result), 1)
        
        # Rollback transaction
        DuckDbDatabase.rollback(conn)
        
        # Verify data was rolled back
        result = conn.execute("SELECT * FROM test_rollback").fetchdf()
        self.assertEqual(len(result), 0)
        
        # Clean up
        DuckDbDatabase.close(conn)

    def test_get_cursor(self):
        """Test getting a cursor from a connection."""
        cursor = DuckDbDatabase.get_cursor(self.conn)
        self.assertIsInstance(cursor, duckdb.DuckDBPyConnection)

    def test_get_session_not_implemented(self):
        """Test that get_session raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            DuckDbDatabase.get_session(self.conn)

    def test_close_session_not_implemented(self):
        """Test that close_session raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            DuckDbDatabase.close_session(self.conn)

    def test_create_function(self):
        """Test creating a custom function in DuckDB."""
        # Define a simple function to register
        def add_one(x):
            return x + 1
        
        # Register the function
        DuckDbDatabase.create_function(
            self.conn, "add_one", add_one, argument_types=["INTEGER"], return_type="INTEGER"
        )
        
        # Use the function in a query
        result = self.conn.execute("SELECT add_one(2) AS result").fetchdf()
        self.assertEqual(result.iloc[0]['result'], 3)

    def test_create_function_with_types(self):
        """Test creating a custom function with specified argument and return types."""
        # Define a simple function to register
        # NOTE DuckDB does not support overloading functions with the same name.
        def unique_multiply(x, y):
            return x * y

        # Register the function with types
        DuckDbDatabase.create_function(
            self.conn, 
            "unique_multiply", 
            unique_multiply, 
            argument_types=["DOUBLE", "DOUBLE"], 
            return_type="DOUBLE"
        )
        
        # Use the function in a query
        result = self.conn.execute("SELECT unique_multiply(2.5, 3.0) AS result").fetchdf()
        self.assertEqual(result.iloc[0]['result'], 7.5)

    def test_create_function_error(self):
        """Test error handling when creating a custom function."""
        # NOTE Instead of passing a function, let's just pass in None

        with patch('logger.logger.error') as mock_log:
            with self.assertRaises(Exception):
                # This should fail because DuckDB can't handle the complex return type
                # or because we've provided incompatible argument types
                DuckDbDatabase.create_function(
                    self.conn,
                    "this_is_literally_just_none", 
                    None,
                    argument_types=["INTEGER"],  # Invalid argument type
                    return_type="INTEGER"  # Invalid type
                )
            
            # Verify error was logged
            self.assertTrue(mock_log.called)

    def test_function_already_exists(self):
        """Test error handling when a function already exists."""
        # Define a simple function to register
        def duplicate_func(x):
            return x * 2
        
        # Register the function first time - should succeed
        DuckDbDatabase.create_function(
            self.conn, 
            "duplicate_func", 
            duplicate_func,
            argument_types=["INTEGER"],
            return_type="INTEGER"
        )
        
        # Try to register again with the same name - should fail
        with patch('logger.logger.error') as mock_log:
            try:
                DuckDbDatabase.create_function(
                    self.conn, 
                    "duplicate_func", 
                    duplicate_func,
                    argument_types=["INTEGER"],
                    return_type="INTEGER"
                )
                self.fail("Expected exception was not raised")
            except Exception:
                # Verify error was logged
                self.assertTrue(mock_log.called)

    def test_create_table_if_not_exists(self):
        """Test creating a table if it doesn't exist."""
        # Define table columns
        columns = [
            {'name': 'id', 'type': 'INTEGER PRIMARY KEY'},
            {'name': 'name', 'type': 'TEXT'},
            {'name': 'created_at', 'type': 'TIMESTAMP'}
        ]
        
        # Define constraints
        constraints = [
            'CONSTRAINT unique_name UNIQUE (name)'
        ]
        
        # Create the table
        DuckDbDatabase.create_table_if_not_exists(
            self.conn,
            'test_create_table',
            columns,
            constraints
        )
        
        # Verify the table was created
        result = self.conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='test_create_table'
        """).fetchdf()
        
        self.assertEqual(len(result), 1)
        
        # Test inserting data
        self.conn.execute("""
            INSERT INTO test_create_table (id, name, created_at)
            VALUES (1, 'Test Item', CURRENT_TIMESTAMP)
        """)
        
        # Verify unique constraint
        with self.assertRaises(Exception):
            self.conn.execute("""
                INSERT INTO test_create_table (id, name, created_at)
                VALUES (2, 'Test Item', CURRENT_TIMESTAMP)
            """)
    
    def test_create_table_if_not_exists_error(self):
        """Test error handling when creating a table."""
        # Define invalid columns (missing 'type')
        columns = [
            {'name': 'id', 'wrong_key': 'INTEGER PRIMARY KEY'},
        ]
        
        with patch('logger.logger.error') as mock_log:
            with self.assertRaises(Exception):
                DuckDbDatabase.create_table_if_not_exists(
                    self.conn,
                    'test_create_table_error',
                    columns
                )
            
            # Verify error was logged
            self.assertTrue(mock_log.called)

    def test_create_index_if_not_exists(self):
        """Test creating an index if it doesn't exist."""
        # Create a table for indexing
        self.conn.execute("""
            CREATE TABLE test_index_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                category TEXT
            )
        """)
        
        # Insert some test data
        self.conn.execute("""
            INSERT INTO test_index_table VALUES 
            (1, 'Item 1', 'Category A'),
            (2, 'Item 2', 'Category B'),
            (3, 'Item 3', 'Category A')
        """)
        
        # Create an index
        DuckDbDatabase.create_index_if_not_exists(
            self.conn,
            'test_index_table',
            'idx_category',
            ['category']
        )
        
        # Verify the index was created
        result = self.conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='idx_category'
        """).fetchdf()
        
        self.assertEqual(len(result), 1)
        
        # Create a unique index
        DuckDbDatabase.create_index_if_not_exists(
            self.conn,
            'test_index_table',
            'idx_name_unique',
            ['name'],
            unique=True
        )
        
        # Verify unique constraint is enforced
        with self.assertRaises(Exception):
            self.conn.execute("""
                INSERT INTO test_index_table VALUES 
                (4, 'Item 1', 'Category C')
            """)
    
    def test_create_index_if_not_exists_error(self):
        """Test error handling when creating an index."""
        with patch('logger.logger.error') as mock_log:
            with self.assertRaises(Exception):
                DuckDbDatabase.create_index_if_not_exists(
                    self.conn,
                    'nonexistent_table',
                    'idx_test',
                    ['column']
                )
            
            # Verify error was logged
            self.assertTrue(mock_log.called)


if __name__ == '__main__':
    unittest.main()
