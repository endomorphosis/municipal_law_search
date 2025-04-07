import duckdb


from configs import configs


def make_search_query_table_if_it_doesnt_exist() -> None:
    """
    Create a hash table for the citation database.
    NOTE: query_cid is made from the hash of the query string.
    """
    with duckdb.connect(configs.AMERICAN_LAW_DB_PATH, read_only=False) as conn:
        with conn.cursor() as cursor:
            # NOTE cids_for_top_100 is a string of 100 comma-separate CIDs.
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_query (
                search_query_cid VARCHAR PRIMARY KEY,
                search_query TEXT NOT NULL,
                embedding DOUBLE[1536] NOT NULL,
                total_results INTEGER NOT NULL,
                cids_for_top_100 TEXT NOT NULL,
            )
            ''')
