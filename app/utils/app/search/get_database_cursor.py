from .type_vars import SqlConnection, SqlCursor


def get_database_cursor(connection: SqlConnection) -> SqlCursor:
    """Get a cursor from the provided database connection."""
    return connection.cursor()
