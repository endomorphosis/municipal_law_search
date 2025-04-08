from .type_vars import SqlConnection, SqlCursor


def get_database_cursor(connection: SqlConnection) -> SqlCursor:
    return connection.cursor()