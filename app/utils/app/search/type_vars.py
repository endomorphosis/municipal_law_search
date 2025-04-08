"""
Type variable definitions for the American Law Search application.

This module defines TypeVar definitions for SQL connections, cursors,
and language models to enable consistent type hinting throughout the application.
"""
import sqlite3
from typing import TypeVar


import duckdb


# Type variables for SQL connections and LLM
SqlCursor = TypeVar('SqlCursor', duckdb.DuckDBPyConnection, sqlite3.Cursor)
"""
Type variable for SQL cursors, supporting both DuckDB and SQLite cursors.

This type variable is used for function parameters and return types that can
be either a DuckDB cursor or a SQLite cursor, allowing for database engine
abstraction throughout the codebase.
"""

SqlConnection = TypeVar('SqlConnection', duckdb.DuckDBPyConnection, sqlite3.Connection)
"""
Type variable for SQL connections, supporting both DuckDB and SQLite connections.

This type variable is used for function parameters and return types that can
be either a DuckDB connection or a SQLite connection, allowing for database engine
abstraction throughout the codebase.
"""

LLM = TypeVar('LLM')
"""
Type variable for language model implementations.

This generic type variable is used for function parameters and return types
related to language model functionality, allowing for abstraction of specific
LLM implementations.
"""