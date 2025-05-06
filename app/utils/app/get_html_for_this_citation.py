from typing import Dict, NamedTuple


from app.utils.database.get_db import get_html_db


def get_html_for_this_citation(row: Dict | NamedTuple) -> str:
    """
    Retrieves the HTML content associated with a given citation ID (cid) from the database.

    Args:
        row (dict | NamedTuple): A data structure containing the citation ID (cid). 
                                    If `row` is a dictionary, the cid is accessed via `row['cid']`.
                                    If `row` is a NamedTuple, the cid is accessed via `row.cid`.
        read_only (bool): A flag indicating whether the database connection should be read-only.

    Returns:
        str: The HTML content corresponding to the provided citation ID. 
            If none is available, returns "Content not available".
    """
    html_conn = get_html_db()
    with html_conn.cursor() as html_cursor:
        if isinstance(row, dict):
            html_cursor.execute('SELECT html FROM html WHERE cid = ? LIMIT 1', (row['cid'],))
        else:
            html_cursor.execute('SELECT html FROM html WHERE cid = ? LIMIT 1', (row.cid,))
        html_result = html_cursor.fetchone()
    html_conn.close()
    return html_result[0] if html_result is not None else "Content not available"
