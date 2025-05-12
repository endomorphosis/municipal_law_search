from typing import Any


import duckdb


from configs import configs 
from logger import logger
from schemas.search_response import SearchResponse
from .format_initial_sql_return_from_search import format_initial_sql_return_from_search


def _calc_total_pages(total: int, per_page: int) -> int:
    return (total + per_page - 1) // per_page


def get_cached_query_results(
    search_query_cid: str = None,
    page: int = None,
    per_page: int = None
) -> dict[str, Any]:

    html_set = set()
    cid_set = set()

    with duckdb.connect(configs.AMERICAN_LAW_DB_PATH, read_only=True) as conn:
        with conn.cursor() as cursor:
            # Check if the query already exists in the search_query table
            cursor.execute('''
            SELECT COUNT(*) FROM search_query WHERE search_query_cid = ?
            ''', (search_query_cid,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                # If the query already exists, fetch the results from the search_query table
                logger.debug(f"Query already performed. Getting cached results.")
                cursor.execute('''
                SELECT cids_for_top_100 FROM search_query WHERE search_query_cid = ?
                ''', (search_query_cid,))
                cids_for_top_100: str = cursor.fetchone()[0] # -> comma-separated string
                logger.debug(f"cids_for_top_100: {cids_for_top_100}")

                # Convert the comma-separated string to a list of CIDs
                # Then convert it to a list of strings for a SQL query.
                cids_for_top_100: list[str] = cids_for_top_100.split(',')
                cid_list = [
                    f" c.cid = '{cid.strip()}'" if i == 1 else f" OR c.cid = '{cid.strip()}'"
                    for i, cid in enumerate(cids_for_top_100, start=1)
                ]
                cid_list = ''.join(cid_list)
                logger.debug(f"cid_list: {cid_list}")

                cursor.execute(f'''
                SELECT c.cid, 
                    c.bluebook_cid,
                    c.title,
                    c.chapter,
                    c.place_name,
                    c.state_name,
                    c.bluebook_citation,
                    h.html
                FROM citations c
                JOIN html h ON c.cid = h.cid
                WHERE
                ''' + cid_list )
                df_dict = cursor.fetchdf().to_dict('records')
                total = len(df_dict)
                logger.debug(f"Returned {total} rows from the cached query.")

                # Format the results for the response.
                results: list[dict] = []
                for row in df_dict:
                    if row['cid'] in cid_set:
                        continue
                    else:
                        cid_set.add(row['cid'])

                    row_dict = format_initial_sql_return_from_search(row)
                    if row_dict['html'] in html_set:
                        continue
                    else:
                        html_set.add(row_dict['html'])
                        results.append(row_dict)

                # Return the cached results
                search_response = SearchResponse(
                    results=results,
                    total=total,
                    page=page,
                    per_page=per_page,
                    total_pages=_calc_total_pages(total, per_page)
                )
                return search_response.model_dump()
            else:
                return None
