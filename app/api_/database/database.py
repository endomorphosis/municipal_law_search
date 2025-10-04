"""
Database connection and session management for the FastAPI application.

This module provides a Database class that encapsulates database connection management,
connection pooling, and CRUD operations. It supports multiple database engines
through a dependency injection pattern.
"""
from contextlib import contextmanager
from functools import wraps
import logging
import os
from queue import Queue
from threading import Lock
import time
import traceback
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple, TypeVar


from api_.database.dependencies.duckdb_database import DuckDbDatabase
from configs import configs, Configs
from logger import logger as module_logger


C = TypeVar('C') # 'C' for connection type
S = TypeVar('S') # 'S' for session type

# try_except.py
import asyncio
import inspect


def try_except(func: Callable = lambda x: x, 
               raise_: bool = None,
               exception_type: Exception = Exception, 
               msg: str = "An unexpected exception occurred",
               default_return: Optional[Any] = None
               ) -> Callable:
    """
    Decorator to handle exceptions in a function.

    Args:
        raise_: Whether to re-raise the exception after logging.
            NOTE: This must be manually set to True or False. 
                This reduces the risk of accidentally raising or passing an exception.
        func: The function to decorate
        exceptiontype: The type of exception to catch
        msg: The message to log on exception
        default_return: The value to return if an exception occurs. Only returned if raise_ is False

    Returns:
        A wrapped function that handles exceptions
    """

    def decorator(func: Callable | Coroutine) -> Callable | Coroutine:

        # Check if the function is asynchronous
        async_ = inspect.iscoroutinefunction(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            if raise_ is None:
                raise ValueError("raise must be set to True or False")
            errored = None
            try:
                return func(*args, **kwargs)
            except exception_type as e:
                module_logger.exception(f"{msg}: {e}", stacklevel=2) # Raise the stack level up to the caller
                errored = e
            finally:
                if errored is None:
                    module_logger.debug(f"Function {func.__name__} completed successfully.")
                else:
                    module_logger.debug(f"Function {func.__name__} failed with error: {errored}")
                    if raise_:
                        raise errored
                    else:
                        if default_return is not None:
                            return default_return

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if raise_ is None:
                raise ValueError("raise_ must be set to True or False")
            errored = None
            try:
                return await func(*args, **kwargs)
            except exception_type as e:
                module_logger.exception(f"{msg}: {e}", stacklevel=2) # Raise the stack level up to the caller
                errored = e
            finally:
                if errored is None:
                    module_logger.debug(f"Function {func.__name__} completed successfully.")
                else:
                    module_logger.debug(f"Function {func.__name__} failed with error: {errored}")
                    if raise_:
                        raise errored
                    else:
                        if default_return is not None:
                            return default_return

        return async_wrapper if async_ else wrapper
    return decorator


class Database:
    """
    A class to manage database connections and operations.
    
    This class provides methods for database connection management,
    connection pooling, and CRUD operations. It's designed to work
    with multiple database engines through dependency injection.
    
    Attributes:
        configs: Configuration settings for the database
        resources: Dictionary of callable functions for database operations
        logger: Logger instance for logging database operations

    Methods:
        connect: Establish a connection to the database
        close: Close the current database connection
        execute: Execute a database query
        fetch: Fetch a specified number of results from a query
        fetch_all: Fetch all results from a query
        execute_script: Execute a multi-statement SQL script
        commit: Commit the current transaction
        rollback: Rollback the current transaction
        begin: Begin a new transaction
        connection_context_manager: Context manager for database connections
        transaction_context_manager: Context manager for database transactions
        exit: Close all database connections and end the session
        close_session: Close the current database session if it exists
        get_cursor: Get a cursor for the database connection
    """

    def __init__(self, *,
                 configs: Configs = None, 
                 resources: Dict[str, Callable] = None
                 ) -> None:
        """
        Initialize the database manager.
        
        Args:
            configs: Pydantic class of configuration settings for the database
            resources: Dictionary of callable functions for database operations
        """
        self.configs = configs
        self.resources = resources

        self.logger: logging.Logger = self.resources['logger']

        self._session: Optional[S] = None
        self._transaction_conn: Optional[C] = None
        self._db_type: Optional[str] = self.resources.get("db_type", "duckdb")
        self._read_only: Optional[bool] = self.resources.get("read_only", False)
        self._db_path: Optional[str] = self.resources.get("db_path", self.configs.AMERICAN_LAW_DATA_DIR)

        # Connection pool settings
        self._connection_pool_size: int = self.configs.DATABASE_CONNECTION_POOL_SIZE
        self._connection_timeout: float = self.configs.DATABASE_CONNECTION_TIMEOUT
        self._connection_max_age: float = self.configs.DATABASE_CONNECTION_MAX_AGE

        # Initialize connection pool
        self._connection_pool: Queue = Queue(maxsize=self._connection_pool_size)
        self._pool_lock: Lock = Lock()

        # Map resource functions if provided
        self._connect: Callable = self.resources["connect"]
        self._close: Callable = self.resources["close"]
        self._execute: Callable = self.resources["execute"]
        self._fetch_all: Callable = self.resources["fetch_all"]
        self._fetch: Callable = self.resources["fetch"]
        self._begin: Callable = self.resources["begin"]
        self._commit: Callable = self.resources["commit"]
        self._rollback: Callable = self.resources["rollback"]
        self._get_cursor: Callable = self.resources["get_cursor"]

        # Optional session management if database supports it
        self._close_session: Optional[Callable] = self.resources.get("close_session")

        # Initialize connection pool
        self._init_connection_pool()
        self.logger.info("Database initialized")

    def _flush_connection_pool(self) -> None:
        """
        Flush the connection pool by closing all connections.

        It should be called when the application
        is shutting down or when a new database engine is being used.
        """
        if self._connection_pool:
            # Clear existing connections in the pool
            while not self._connection_pool.empty():
                try:
                    conn_info = self._connection_pool.get(block=False)
                    self._close(conn_info['connection'])
                except Exception as e:
                    self.logger.exception(f"Error closing connection: {e}")
                    continue
        # self.logger.debug("Connection pool flushed")

    def _init_connection_pool(self) -> None:
        """
        Initialize the connection pool with a set of database connections.
        
        This method creates new connections and adds them to the connection pool
        up to the maximum pool size defined in configuration.
        """
        if self._connection_pool:
            # Flush existing connections in the pool
            self._flush_connection_pool()

        for _ in range(self._connection_pool_size):
            try:
                conn = self._connect()
                self._connection_pool.put({
                    'connection': conn,
                    'created_at': time.time(),
                    'last_used': time.time()
                })
            except Exception as e:
                self.logger.exception(f"Error initializing connection pool: {e}")
                raise e
        self.logger.debug("Connection pool initialized")

    def __enter__(self) -> 'Database':
        """
        Context manager entry method.
        
        Returns:
            self: The database instance
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context manager exit method.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        self.exit()
        return


    def exit(self) -> None:
        """
        Close all database connections and end the session, if present.
        
        This method should be called when the application is shutting down
        or when a new database engine is being used.
        """
        self._flush_connection_pool()
        self._session = None


    @try_except(msg="Error getting connection from pool", raise_=True)
    def _get_connection_from_pool(self) -> C:
        """
        Get a connection from the pool or create a new one if needed.

        Returns:
            A database connection
        """
        if self._connection_pool.empty():
            # If pool is empty, re-initialize the pool
            self._init_connection_pool()

        # Get a connection from the pool
        with self._pool_lock:
            conn_info = self._connection_pool.get(block=False)

            # Check if connection is too old
            if time.time() - conn_info['created_at'] > self._connection_max_age:
                try:
                    self._close(conn_info['connection'])
                except Exception as e:
                    self.logger.warning(f"Error closing aged connection: {e}")
                
                # Create a new connection
                conn_info = {
                    'connection': self._connect(),
                    'created_at': time.time(),
                    'last_used': time.time()
                }
                
            # Update last used time
            conn_info['last_used'] = time.time()
            if self._read_only:
                # If read-only, set the connection to read-only mode
                conn_info['connection'].execute("PRAGMA read_only = true")
            return conn_info['connection']


    def _return_connection_to_pool(self, conn: C) -> None:
        """
        Return a connection to the pool if space is available.
        
        Args:
            conn: The database connection to return to the pool
        """
        # self.logger.debug("Returning connection to pool...")
        try:
            # If pool is full, close the connection
            if self._connection_pool.full():
                # self.logger.debug("Connection pool is full, closing connection")
                self._close(conn)
                return
            # self.logger.debug("Returning connection to pool")

            # Add connection back to pool
            with self._pool_lock:
                # self.logger.debug("Acquired pool lock")
                self._connection_pool.put({
                    'connection': conn,
                    'created_at': time.time(),
                    'last_used': time.time()
                }, block=False)
                # self.logger.debug("Connection return to pool.")
            # self.logger.debug("Pool lock released") 
            return
        except Exception as e:
            self.logger.warning(f"Error returning connection to pool: {e}\n{traceback.format_exc()}")
            
            # Close connection if we couldn't return it
            try:
                self._close(conn)
            except Exception as e2:
                self.logger.warning(f"Error closing connection: {e2}\n{traceback.format_exc()}")


    @try_except(msg="Error connecting to database", raise_=True)
    def connect(self) -> C:
        """
        Establish a connection to the database.
        
        This method gets a connection from the pool or creates a new one.
        """
        # Do nothing if already connected.
        conn = self._get_connection_from_pool()
        self.logger.debug("Database connection established")
        return conn


    def close(self, conn: C) -> None:
        """
        Return the current database connection to the pool.
        Also closes an active session first, if one exists.

        Args:
            conn: The database connection to close
        """
        self.logger.debug("Closing database connection...")
        # First, close any active session
        self.close_session(conn)
        self.logger.debug("Session closed")

        # Return connection to pool
        self._return_connection_to_pool(conn)
        self.logger.debug("Database connection closed")


    @try_except(msg="Error closing session", raise_=False)
    def close_session(self, conn: C) -> None:
        """
        Close the current database session if it exists.
        """
        if self._session:
            self._close_session(conn)
            self._session = None
            self.logger.debug("Session closed")
        self.logger.debug("No session to close")
        return

    @try_except(msg="Error getting cursor", raise_=True)
    def get_cursor(self, conn: C) -> Any:
        """
        Get a cursor for the database connection.
        
        Returns:
            A database cursor
        
        Raises:
            Exception: If no database connection is established
        """
        return self._get_cursor(conn)

    def execute(self,
                query: str,
                params: Optional[ Tuple | Dict[str, Any]] = None
                ) -> Any:
        """
        Execute a database query.
        
        Args:
            query: The SQL query to execute
            params: Optional parameters for the query
            
        Returns:
            The result of the query execution
            
        Raises:
            Exception: If no database connection is established
        """
        with self.transaction_context_manager() as conn:
            try:
                if params:
                    return self._execute(conn, query, params)
                else:
                    return self._execute(conn, query)
            except Exception as e:
                self.logger.exception(f"Error executing query: {e}")
                self.logger.debug(f"Query: {query}")
                self.logger.debug(f"Params: {params}")
                raise

    def fetch(self, 
            query: str, 
            params: Optional[ Tuple | Dict[str, Any]] = None, 
            num_results: int = 1,
            return_format: Optional[str] = None,
            ) -> List[Dict[str, Any]] | None:
        """
        Fetch a specified number of results from a query.
        
        Args:
            query: The SQL query to execute
            params: Optional parameters for the query
            return_format: Optional format for the return value

        Returns:
            Any: The results of the query in the specified format

        Raises:
            Exception: If no database connection is established
        """ 
        if num_results is None or num_results <= 1:
            num_results = 1

        with self.connection_context_manager() as conn:
            try:
                return self._fetch(conn, query, params, num_results, return_format)
            except Exception as e:
                self.logger.exception(f"Error fetching results: {e}")
                self.logger.debug(f"Query: {query}")
                self.logger.debug(f"Params: {params}")
                return []


    def fetch_all(self, 
                  query: str, 
                  params: Optional[ Tuple | Dict[str, Any]] = None, 
                  return_format: Optional[str] = None
                  ) -> List[Dict[str, Any]] | None:
        """
        Fetch all results from a query.
        
        Args:
            query: The SQL query to execute
            params: Optional parameters for the query
            return_format: Optional format for the return value

        Returns:
            Any: The results of the query in the specified format

        Raises:
            Exception: If no database connection is established
        """
        with self.connection_context_manager() as conn:
            try:
                return self._fetch_all(conn, query, params, return_format)
            except Exception as e:
                self.logger.exception(f"Error fetching results: {e}")
                self.logger.debug(f"Query: {query}")
                self.logger.debug(f"Params: {params}")
                return []

    def execute_script(
        self, 
        script: Optional[str] = None,
        params: Optional[Tuple | Dict[str, Any]] = None,
        path: Optional[str] = None
        ) -> Any | None:
        """
        Execute a multi-statement SQL script, either from a string or a file.
        NOTE: Either script or path must be provided, not both.

        Args:
            script: Optional SQL script to execute
            params: Optional parameters for the script
            path: Optional path to a file containing the SQL script

        Returns:
            The result of the script execution.

        Raises:
            Exception: If script execution fails
        """
        if script is None and path is None:
            raise ValueError("Either script or path must be provided.")
        elif script is None and path is None:
            raise ValueError("Both script and path are set. Provide one or the other, but not both.")
        else:
            if not isinstance(script, str):
                raise TypeError("Script must be a string, got {type(script).__name__}.")
            if path is not None:
                # If a path is provided, read the script from the file.
                if os.path.exists(path):
                    try:
                        with open(path, 'r') as file:
                            script = file.read()
                    except Exception as e:
                        raise IOError(f"Error reading file {path}: {e}") from e
                else:
                    raise FileNotFoundError(f"File not found: {path}")
        try:
            return self.execute(script, params)
        except Exception as e:
            self.logger.exception(f"Error executing script: {e}")
            self.logger.debug(f"Script: {script}")
            self.logger.debug(f"Path: {path}")
            self.logger.debug(f"Params: {params}")
            raise e


    @try_except(msg="Error committing transaction", raise_=True)
    def commit(self, connection: C) -> None:
        """
        Commit the current transaction.

        Args:
            connection: The database connection used for the transaction

        Raises:
            Exception: If no database connection is established
        """
        self._commit(connection)


    @try_except(msg="Error rolling back transaction", raise_=True)
    def rollback(self, connection: C) -> None:
        """
        Rollback the current transaction.

        Args:
            connection: The database connection used for the transaction

        Raises:
            Exception: If an error occurs during rollback
        """
        self._rollback(connection)


    @try_except(msg="Error starting transaction", raise_=True)
    def begin(self, connection: C) -> C:
        """
        Begin a new transaction.

        Args:
            connection: The database connection to use for the transaction

        Returns:
            The database connection

        Raises:
            Exception: If an error occurs during transaction start
        """
        return self._begin(connection)

    @contextmanager
    def connection_context_manager(self) -> C:
        """
        Connection context manager.
        NOTE: Because this yields a connection, it directly accesses the functions of the dependency.

        Yields:
            A database connection

        Usage:
            with db.connection() as conn:
                conn.execute("SELECT * FROM ...")
        """
        errored = None
        conn = self._get_connection_from_pool()
        try:
            yield conn
        except Exception as e:
            self.logger.exception(f"Transaction error: {e}")
            errored = e
        finally:
            self.close(conn)
            if errored is not None:
                raise errored

    @contextmanager
    def transaction_context_manager(self) -> C:
        """
        Transaction context manager.
        NOTE: Because this yields a connection, it directly accesses the functions of the dependency.

        Yields:
            A context manager for transaction handling

        Usage:
            with db.transaction_context_manager() as trans:
                trans.execute("INSERT INTO ...")
                trans.execute("UPDATE ...")
        """
        errored = None
        conn = self._get_connection_from_pool()

        try:
            yield conn
        except Exception as e:
            self.logger.exception(f"Transaction error: {e}")
            self.rollback(conn)
            errored = e
        finally:
            if errored is None:
                self.commit(conn)

            # Return the connection to the pool
            self.close(conn)

            # If an error occurred, raise it.
            if errored is not None:
                raise errored
