import duckdb


from utils.database.get_db import get_embeddings_db



def get_embedding_cids_for_all_the_cids(initial_results: list[dict]) -> list[dict]:
    """
    Retrieves embedding CIDs for all the provided CIDs from the embeddings database.

    Args:
        initial_results (list[dict]): A list of dictionaries, where each dictionary contains 
                                      a 'cid' key representing the unique identifier.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary contains the 'embedding_cid' 
                    and 'cid' retrieved from the embeddings database.

    Notes:
        - The function establishes a read-only connection to the embeddings database.
        - For each CID in the input list, it queries the database to fetch the corresponding 
          embedding CIDs and appends the results to the output list.
        - The database connection and cursor are properly closed after the operation.
    """
    # Get embeddings_cids for all the CIDs,
    embeddings_conn: duckdb.DuckDBPyConnection = get_embeddings_db(read_only=True)
    embeddings_cursor = embeddings_conn.cursor()
    embedding_id_list: list[tuple] = []
    for row in initial_results:
        # Query the embeddings table using the current row's cid
        embedding_ids: list[dict] = embeddings_cursor.execute('''
            SELECT embedding_cid, cid
            FROM embeddings 
            WHERE cid = ?;
        ''', (row['cid'],)).fetchdf().to_dict('records')[0]
        embedding_id_list.append(embedding_ids)

    embeddings_cursor.close()
    embeddings_conn.close()
    return embedding_id_list