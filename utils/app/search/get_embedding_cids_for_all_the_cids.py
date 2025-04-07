from itertools import batched
from typing import Generator


import duckdb
import tqdm
import psutil


from logger import logger
from configs import configs
from utils.database.get_db import get_embeddings_db



def get_embedding_cids_for_all_the_cids(
        initial_results: list[dict], 
        batch_size: int = 100
        ) -> Generator[None, None, list[dict]]:
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

    if initial_results:
        for batch in tqdm.tqdm(batched(initial_results, batch_size)):

            embedding_id_list: list[tuple] = []
            for i, row in enumerate(batch, start=1):
                if i == 1:
                    cid_string = f" cid = '{row['cid']}'"
                cid_string += f" OR cid = '{row['cid']}'"

            # Query the embeddings table using the current row's cid
            try: # TODO: Make it so I can select multiple rows at once.
                embedding_ids: list[tuple] = embeddings_cursor.execute(f'''
                    SELECT embedding_cid, cid
                    FROM embeddings 
                    WHERE
                    ''' + cid_string + ";", 
                ).fetchall()
                for row in embedding_ids:
                    embedding_id_list.append({'embedding_cid': row[0], 'cid': row[1]})
            except IndexError:
                #logger.debug(f"No embedding found for the given CID {row['cid']}.")
                continue
            yield embedding_id_list
    else:
        logger.debug("No initial results provided. Returning an empty list.")
        yield []

    embeddings_cursor.close()
    embeddings_conn.close()
    return embedding_id_list