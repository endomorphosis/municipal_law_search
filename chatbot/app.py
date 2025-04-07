#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations
import asyncio
from datetime import datetime
import functools
import json
from dotenv import load_dotenv
import os
from pathlib import Path
import sqlite3
import time
import traceback
from typing import Annotated, Any, AsyncGenerator, Callable, Coroutine, Dict, List, NamedTuple, Never, Optional, Union


import duckdb
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AfterValidator as AV, BaseModel, BeforeValidator as BV, Field, field_validator
from sse_starlette.sse import EventSourceResponse


from configs import configs, Configs
from logger import logger
from chatbot.api.llm.async_interface import AsyncLLMInterface
from utils.app.search.format_initial_sql_return_from_search import format_initial_sql_return_from_search
from utils.app.search.get_embedding_cids_for_all_the_cids import get_embedding_cids_for_all_the_cids
from utils.app.search.turn_english_into_sql import (
    turn_english_into_sql
)
from utils.app.search.get_embedding_and_calculate_cosine_similarity import (
    get_embedding_and_calculate_cosine_similarity
)
from utils.app.search.make_search_query_table_if_it_doesnt_exist import (
    make_search_query_table_if_it_doesnt_exist
)
from utils.app.search.sort_and_save_search_query_results import sort_and_save_search_query_results
from utils.database.get_db import get_html_db, get_american_law_db
from utils.get_cid import get_cid
from utils.run_in_process_pool import run_in_process_pool, async_run_in_process_pool


# Load environment variables
load_dotenv()

# Create necessary databases
# setup_embeddings_db()
# setup_html_db()
# setup_citation_db()


app = FastAPI(title="American Law API", description="API for accessing American law database")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files correctly
app.mount("/src", StaticFiles(directory="chatbot/client/src"), name="src")
templates = Jinja2Templates(directory="chatbot/client/public")

# Serve favicon
favicon_path = configs.AMERICAN_LAW_DIR / 'chatbot' / 'client' / 'public'/ 'favicon.ico'

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)


# Initialize LLM interface if API key is available
llm = None
try:
    openai_api_key = os.environ.get("OPENAI_API_KEY") or configs.OPENAI_API_KEY.get_secret_value()
    data_path = os.environ.get("AMERICAN_LAW_DATA_DIR") or configs.AMERICAN_LAW_DATA_DIR
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")
    raise e

try:
    llm = AsyncLLMInterface(
        api_key=configs.OPENAI_API_KEY.get_secret_value(),
        configs=configs
    )
    logger.info("LLM interface initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize LLM interface: {e}")
    raise e


class HtmlRow(BaseModel):
    """
    A Pydantic model representing a row in the 'html' table in html.db and american_law.db.
    """
    cid: str = None
    doc_id: str = None
    doc_order: int = None
    html_title: str = None 
    html: str = None
    gnis: str | int  = None 


class CitationsRow(BaseModel):
    """
    A Pydantic model representing a row in the 'citations' table in citations.db and american_law.db.
    """
    cid: str = None
    bluebook_cid: str = None
    title: str = None
    public_law_num: Optional[str] = None
    chapter: Optional[str] = None
    ordinance: Optional[str] = None
    section: Optional[str] = None
    enacted: Optional[str] = None
    year: Optional[str] = None
    history_note: Optional[str] = None
    place_name: str
    state_code: str
    bluebook_state_code: str
    state_name: str
    chapter_num: Optional[str] = None
    title_num: Optional[str] = None
    date: Optional[str] = None
    bluebook_citation: str = None
    gnis: str | int  = None 


class EmbeddingsRow(BaseModel):
    """
    A Pydantic model representing a row in the 'embeddings' table in embeddings.db and american_law.db.
    """
    embedding_cid: str = None
    cid: Optional[int] = None
    embedding: Optional[str] = None
    text_chunk_order: Optional[str] = None
    gnis: str | int  = None 


# def validate_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     reworked_results = []
#     for row in results:
#         for validator in [HtmlRow, CitationsRow, EmbeddingsRow]:
#             validator: BaseModel
#             # Check how many keys there are.
#             if len(row.keys()) == 1:
#                 reworked_results.append({
#                     key: value for key, value in row.items()
#                 })
#             for key in row.keys():
#                 if key not in validator.model_json_schema()['properties']:
#                     reworked_results.append({
#                         key: value for key, value in row.items()
#                     })
#     return reworked_results if reworked_results else results


# Pydantic models for request/response validation
class SearchResponse(BaseModel):
    """
    Attributes:
        results (List[Dict[str, Any]]): List of search results.
        total (int): Total number of results.
        page (int): Current page number.
        per_page (int): Number of items per page.
        total_pages (int): Total number of pages.
    """
    results: List[Dict[str, Any]]
    total: int
    page: int
    per_page: int
    total_pages: int


class LawItem(BaseModel):
    cid: str
    title: str
    chapter: Optional[str] = None
    place_name: Optional[str] = None
    state_name: Optional[str] = None
    date: Optional[str] = None
    bluebook_citation: Optional[str] = None
    html: str


class LLMAskRequest(BaseModel):
    query: str
    use_rag: bool = True
    use_embeddings: bool = True
    document_limit: int = 5
    system_prompt: Optional[str] = None


class LLMSearchEmbeddingsRequest(BaseModel):
    query: str
    file_id: Optional[str] = None
    top_k: int = 5


class LLMCitationAnswerRequest(BaseModel):
    query: str
    citation_codes: List[str]
    system_prompt: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str


class SqlQueryResponse(BaseModel):
    sql_query: str
    model_used: str
    total_tokens: int


# Routes
# Serve HTML pages correctly:
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Serve public assets directly:
@app.get("/public/{filename:path}")
async def serve_public_files(filename: str):
    return FileResponse(f"chatbot/client/public/{filename}")


def _get_html_for_this_citation(row: dict | NamedTuple) -> str:
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


async def _determine_user_intent(
    query: str,
) -> str:
    """
    Determine what a user wants to do with the search query asynchronously.
    This function will be used to determine if the user wants to search, ask a question, convert to SQL, etc.
    """


async def get_cached_query_results(
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


async def figure_out_what_the_user_wants(q: str) -> Never:

    try:
        intent = await llm.determine_user_intent(q.lower())
    except Exception as e:
        logger.error(f"Error determining user intent: {e}")
        raise HTTPException(status_code=400, detail="Unable to determine user intent")

    if intent is None:
        raise ValueError("LLM produced None as the intent.")

    if "FLAGGED" in intent:
        logger.error(f"Query flagged as inappropriate: {q.lower()}")
        raise HTTPException(status_code=400, detail="Query flagged as inappropriate")
    
    if "SEARCH" not in intent:
        logger.error(f"Query not flagged as a search: {q.lower()}")
        raise HTTPException(status_code=400, detail="Query not flagged as a search")


@app.get("/api/search/sse")
async def search_sse_response(
    q: str = Query("", description="Search query"),
    page: int = Query(1, description="Page number"),
    per_page: int = Query(20, description="Items per page"),
):
    """
    Server-Sent Events endpoint that streams search results incrementally.
    """
    async def _event_generator():
        try:
            # Initial event to indicate the search has started
            yield {
                "event": "search_started",
                "data": json.dumps({
                    "message": "Search started",
                    "query": q
                })
            }
            
            # Process search results
            async for result in search(q=q, page=page, per_page=per_page):
                # Send each result chunk as it becomes available
                yield {
                    "event": "results_update",
                    "data": json.dumps(result)
                }
                
            # Final event to indicate the search is complete
            yield {
                "event": "search_complete",
                "data": json.dumps({
                    "message": "Search completed",
                    "query": q
                })
            }
                
        except Exception as e:
            logger.error(f"Error in SSE stream: {e}")
            # Send error event
            yield {
                "event": "error",
                "data": json.dumps({
                    "message": str(e)
                })
            }
    
    return EventSourceResponse(_event_generator())


def format_initial_sql_query_from_llm(sql_query: str) -> str:
    if "```sql" in sql_query:
        # Strip out any markdown formatting if present
        sql_query = sql_query.replace("```sql","").replace("```","").strip()

    if "LIMIT" in sql_query:
        # Get rid of any LIMIT, if there is any.
        logger.debug(f"sql_query: {sql_query}")
        sql_query = sql_query.split("LIMIT")[0].strip()
    
    return sql_query


class LLMSqlOutput(BaseModel):
    sql_query: Annotated[str, AV(format_initial_sql_query_from_llm)]


def get_a_data_base_connection() -> duckdb.DuckDBPyConnection:
    db_conn = get_american_law_db()
    if db_conn is None:
        logger.error("Failed to get a database connection")
        raise HTTPException(status_code=500, detail="Database connection failed")
    return db_conn.cursor()


resources = {
    'make_search_query_table_if_it_doesnt_exist': make_search_query_table_if_it_doesnt_exist,
    'get_a_database_connection': get_a_data_base_connection,
    'get_cached_query_results': get_cached_query_results,
    'get_cid': get_cid,
    'get_single_embedding': llm.openai_client.get_single_embedding,
    'LLMSqlOutput': LLMSqlOutput
}

class SearchFunction:
    # TODO Abstract-out duckdb

    def __init__(self, search_query: str = None, resources: dict[str, Callable] = None, configs: Configs = None):
        self.resources = resources
        self.configs = configs
        self.search_query: str = search_query.lower()


        self.query_table_embedding_cids: list = []
        self.cid_set:      set = set()
        self.html_set:     set = set()
        self.total:        int  = 0

        self.class_cursor: duckdb.DuckDBPyConnection = None
        self.search_query_cid: str = None
        self.search_query_embedding: list[float] = None
        self.llm = None
        self.offset: int = None

        # Get the classes functions.
        ## Sync
        self._make_search_query_table_if_it_doesnt_exist:     Callable  = self.resources['make_search_query_table_if_it_doesnt_exist']
        self._get_a_database_connection:                      Callable  = self.resources['get_a_database_connection']
        self._get_cached_query_results:                       Callable  = self.resources['get_cached_query_results']
        self._get_cid:                                        Callable  = self.resources['get_cid']
        self._turn_english_into_sql:                          Callable  = self.resources['turn_english_into_sql']
        self._get_embedding_and_calculate_cosine_similarity: Callable  = self.resources['get_embedding_and_calculate_cosine_similarity']
        self._sort_and_save_search_query_results:            Callable  = self.resources['sort_and_save_search_query_results']
        self._format_initial_sql_return_from_search:         Callable  = self.resources['format_initial_sql_return_from_search']
        # Async
        self._async_run_in_process_pool:                     Coroutine  = self.resources['async_run_in_process_pool']
        self._figure_out_what_the_user_wants:                Coroutine  = self.resources['figure_out_what_the_user_wants']
        self._get_single_embedding:                          Coroutine  = self.resources['get_single_embedding']
        # Schemas
        self._LLMSqlOutput:                                  BaseModel  = self.resources['LLMSqlOutput'] 

        # Run these start up functions
        self.class_cursor = self.get_a_database_connection()
        self.make_search_query_table_if_it_doesnt_exist()

        self.search_query_cid: str = self.get_cid(search_query)
        self.search_query_embedding: list[float] = self.get_single_embedding(search_query)

        self.func: Callable = functools.partial(
            self._get_embedding_and_calculate_cosine_similarity,
            query_embedding=self.search_query_embedding,
        )


    def estimate_the_total_count_without_pagination(self, sql_query: str) -> None:
        # First, estimate the total count without pagination
        count_query = f"SELECT COUNT(*) as total FROM ({sql_query}) as subquery"
        self.class_cursor.execute(count_query)
        total: int = self.class_cursor.fetchone()[0]
        logger.debug(f"Total results from SQL query: {total}")


    def execute_the_actual_query_with_pagination(self, sql_query: str) -> list[dict[str, Any]]:
        self.class_cursor.execute(sql_query)
        df_dict = self.class_cursor.fetchdf().to_dict('records')
        for row in df_dict:
            # If the CID isn't there or if it's already in the set, continue.
            if "cid" not in row.keys() or row['cid'] in self.cid_set:
                    continue
            else:
                logger.debug(f"Adding cid {row['cid']} to cid_set")
                self.cid_set.add(row['cid'])

                initial_results: list[dict] = [
                    self._format_initial_sql_return_from_search(row) 
                    for row in df_dict if "bluebook_cid" in row.keys()
                ]
                return initial_results


    async def execute_embedding_search(self, initial_results: list[str]) -> None:
        cumulative_results = []
        for embedding_id_list in get_embedding_cids_for_all_the_cids(initial_results):
            pull_list = []
            async for _, embedding_id in async_run_in_process_pool(self.func, embedding_id_list):
                if embedding_id is not None:
                    pull_list.append(embedding_id)

            # Order the pull list by their cosine similarity score.
            pull_list = sorted(pull_list, key=lambda x: x[1], reverse=True)
            #logger.debug(f"pull_list: {pull_list}: pull_list") 
            self.query_table_embedding_cids.extend(pull_list)

            for cid, _ in pull_list:
                # Find the corresponding row in the initial results
                for row_dict in initial_results:
                    if row_dict['cid'] == cid:
                        # Get the HTML content for this citation
                        html: str = _get_html_for_this_citation(row_dict)
                        if html in self.html_set:
                            continue
                        else:
                            self.html_set.add(html)
                            row_dict['html'] = html
                            cumulative_results.append(row_dict)
                            break
        return cumulative_results


    def sort_and_save_search_query_results(self):
        if self.query_table_embedding_cids:
            self._sort_and_save_search_query_results(
                search_query_cid=self.search_query_cid,
                search_query=self.search_query,
                search_query_embedding=self.search_query_embedding,
                query_table_embedding_cids=self.query_table_embedding_cids,
                total=self.total
            )



    @staticmethod
    def _calc_total_pages(total: int, per_page: int) -> int:
        return (total + per_page - 1) // per_page


    async def search(self, search_query: str = "", page: int = 1, per_page: int = 20) -> AsyncGenerator:
        """
        Search for citations in the database using a natural language query.
        """
        logger.info(f"Received request for search at {datetime.now()}")
 
        # Check if the query already exists in the search_query table
        # If they do, yield the cached results and return.
        cached_results = await self.get_cached_query_results(
            search_query_cid=self.search_query_cid, 
            page=page, 
            per_page=per_page
        )
        if cached_results is not None and len(cached_results) > 0:
            logger.info(f"Cached results found for query '{self.search_query}'.\nReturning cached results...")
            yield cached_results
            return # Return to prevent a full embedding search.
        else:
            logger.debug(f"No cached results found for query: {self.search_query}")

        await self.figure_out_what_the_user_wants(self.search_query)

        self.offset = (page - 1) * per_page
        sql_query = await self.turn_english_into_sql(
            search_query=search_query,
            per_page=per_page,
            offset=self.offset,
            llm=self.llm,
            parser=self.LLMSqlOutput
        )

        if sql_query is None:
            raise HTTPException(status_code=500, detail="LLM did not generate a proper SQL query.")

        self.total = self.estimate_the_total_count_without_pagination(sql_query)

        if self.total != 0:
            initial_results = self.execute_the_actual_query_with_pagination(sql_query)
            if initial_results:
                await self.execute_embedding_search(initial_results)

        # TODO Finis the rest of the goddamn owl.


def _calc_total_pages(total: int, per_page: int) -> int:
    return (total + per_page - 1) // per_page


async def search(
    q: str = "",
    page: int = Query(1, description="Page number"),
    per_page: int = Query(20, description="Items per page"),
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Search for citations in the database using a natural language query.
    This endpoint uses the LLM to convert the query into SQL and execute it.
    """
    logger.debug("Received request for search")
    search_query = q.lower()
    logger.debug(f"Received search query: {search_query}")

    # Initial variable states
    html_set = set()
    total = 0

    search_query_cid = get_cid(search_query)

    make_search_query_table_if_it_doesnt_exist()

    # Check if the query already exists in the search_query table
    # If they do, return the cached results.
    cached_results = await get_cached_query_results(
        search_query_cid=search_query_cid, 
        page=page, 
        per_page=per_page
    )
    if cached_results is not None and len(cached_results) > 0:
        logger.debug(f"Returning cached results for query: {search_query}")
        yield cached_results
        return # Return to prevent a full embedding search.
    else:
        logger.debug(f"No cached results found for query: {search_query}")

    await figure_out_what_the_user_wants(search_query)

    search_query_embedding: list[float] = await llm.openai_client.get_single_embedding(search_query)

    offset = (page - 1) * per_page
    sql_query = await turn_english_into_sql(
        search_query=search_query,
        per_page=per_page,
        offset=offset,
        llm=llm,
        parser=LLMSqlOutput
    )

    if sql_query is None:
        raise HTTPException(status_code=500, detail="LLM did not generate a proper SQL query.")

    try:
        # Get a database connection
        db_conn = get_american_law_db()
        if db_conn is None:
            logger.error("Failed to get a database connection")
            raise HTTPException(status_code=500, detail="Database connection failed")
        cursor = db_conn.cursor()

        # Execute the generated SQL query
        try:
            html_set = set()
            cid_set = set()
            query_table_embedding_cids = []
            cumulative_results = []

            # First, estimate the total count without pagination
            count_query = f"SELECT COUNT(*) as total FROM ({sql_query}) as subquery"
            cursor.execute(count_query)
            total: int = cursor.fetchone()[0]
            logger.debug(f"Total results from SQL query: {total}")

            # If total is not zero, execute the actual query
            if total != 0:

                # Then execute the actual query with pagination
                cursor.execute(sql_query)
                df_dict = cursor.fetchdf().to_dict('records')

                for row in df_dict:
                    # If the CID isn't there or if it's already in the set, continue.
                    if "cid" not in row.keys() or row['cid'] in cid_set:
                        continue
                    else:
                        logger.debug(f"Adding cid {row['cid']} to cid_set")
                        cid_set.add(row['cid'])

                initial_results: list[dict] = [
                    format_initial_sql_return_from_search(row) 
                    for row in df_dict if "bluebook_cid" in row.keys()
                ]

                func: Callable = functools.partial(
                    get_embedding_and_calculate_cosine_similarity,
                    query_embedding=search_query_embedding,
                )

                for embedding_id_list in get_embedding_cids_for_all_the_cids(initial_results):
                    pull_list = []
                    async for _, embedding_id in async_run_in_process_pool(func, embedding_id_list):
                        if embedding_id is not None:
                            pull_list.append(embedding_id)

                    # Order the pull list by their cosine similarity score.
                    pull_list = sorted(pull_list, key=lambda x: x[1], reverse=True)
                    #logger.debug(f"pull_list: {pull_list}: pull_list") 
                    query_table_embedding_cids.extend(pull_list)

                    for cid, _ in pull_list:
                        # Find the corresponding row in the initial results
                        for row_dict in initial_results:
                            if row_dict['cid'] == cid:
                                # Get the HTML content for this citation
                                html: str = _get_html_for_this_citation(row_dict)
                                if html in html_set:
                                    continue
                                else:
                                    html_set.add(html)
                                    row_dict['html'] = html
                                    cumulative_results.append(row_dict)
                                    break

                    search_response: SearchResponse = SearchResponse(
                        results=cumulative_results.copy(),
                        total=total,
                        page=page,
                        per_page=per_page,
                        total_pages=_calc_total_pages(total, per_page)
                    )
                    logger.debug(f"Yielding search response...")
                    yield search_response.model_dump()

        except duckdb.BinderException as e:
            logger.error(f"duckdby.BinderException error: {e}")
        finally:
            db_conn.close()

            if query_table_embedding_cids:
                sort_and_save_search_query_results(
                    search_query_cid=search_query_cid,
                    search_query=search_query,
                    search_query_embedding=search_query_embedding,
                    query_table_embedding_cids=query_table_embedding_cids,
                    total=total
                )

            # Final yield with complete results
            yield {
                'results': cumulative_results,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': _calc_total_pages(total, per_page)
            }

    except Exception as e:
        logger.error(f"Error in search: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def make_stats_table():
    """
    Create a stats table for the citation database.
    """
    with duckdb.connect(configs.AMERICAN_LAW_DB_PATH, read_only=True) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                run_cid VARCHAR PRIMARY KEY,
                search_query_cid VARCHAR NOT NULL,
                run_time DOUBLE NOT NULL,
            )
            ''')


@app.get("/api/law/{cid}", response_model=Union[LawItem, ErrorResponse])
async def get_law(cid: str) -> dict:
    html_conn = get_html_db(read_only=True)
    html_cursor = html_conn.cursor()
    
    html_cursor.execute('''
    SELECT *
    FROM citations c
    JOIN html h ON c.cid = h.cid
    WHERE c.cid = ?
    ''', (cid,))
    
    law = html_cursor.fetchdf().to_dict('records')[0]
    html_conn.close()
    logger.debug(f"law: {law}")
    
    if law:
        return {
            'cid': law['cid'],
            'title': law['title'],
            'chapter': law['chapter'],
            'place_name': law['place_name'],
            'state_name': law['state_name'],
            'date': law['date'],
            'bluebook_citation': law['bluebook_citation'],
            'html': law['html']
        }
    else:
        raise HTTPException(status_code=404, detail="Law not found")


# LLM API routes
@app.post("/api/llm/ask")
async def ask_question(request: LLMAskRequest) -> str:
    """
    Ask a question to the LLM with RAG capabilities.
    """
    if not llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM features are not available. Please set OPENAI_API_KEY."
        )
    
    try:
        query = request.query
        
        response = await llm.ask_question(
            query=query,
            use_rag=request.use_rag,
            use_embeddings=request.use_embeddings,
            document_limit=request.document_limit,
            custom_system_prompt=request.system_prompt
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in ask_question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/llm/search-embeddings")
async def search_embeddings(request: LLMSearchEmbeddingsRequest):
    """
    Search for relevant documents using embeddings.
    """
    logger.debug("Received request for search_embeddings")
    if not llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM features are not available. Please set OPENAI_API_KEY."
        )
    
    try:
        query = request.query
        
        results = await llm.search_embeddings(
            query=query,
            file_id=request.file_id,
            top_k=request.top_k
        )
        
        return {
            'query': query,
            'results': results,
            'count': len(results)
        }
        
    except Exception as e:
        logger.error(f"Error in search_embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/llm/citation-answer")
async def generate_citation_answer(request: LLMCitationAnswerRequest):
    """
    Generate an answer based on specific citation references.
    """
    logger.debug("Received request for generate_citation_answer")
    if not llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM features are not available. Please set OPENAI_API_KEY."
        )
    
    try:
        if not request.citation_codes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No citation codes provided"
            )
        
        response = await llm.generate_citation_answer(
            query=request.query,
            citation_codes=request.citation_codes,
            system_prompt=request.system_prompt
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in generate_citation_answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/llm/status")
async def llm_status():
    """
    Check if LLM capabilities are available
    """
    if llm:
        return {
            'status': 'available',
            'model': llm.openai_client.model,
            'embedding_model': llm.openai_client.embedding_model
        }
    else:
        return {
            'status': 'unavailable',
            'reason': 'OpenAI API key not configured'
        }


@app.get("/api/llm/sql")
async def convert_to_sql(
    q: str = Query(..., description="Natural language query to convert to SQL"),
    execute: bool = Query(False, description="Whether to execute the generated SQL")
):
    """
    Convert a natural language query to SQL and optionally execute it
    """
    logger.debug("Received request for convert_to_sql")
    if not llm:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM features are not available. Please set OPENAI_API_KEY."
        )
    
    try:
        # Generate SQL query
        sql_result = await llm.query_to_sql(q)
        sql_query = sql_result.get("sql_query")
        
        if not execute:
            # Return only the SQL query
            return {
                'original_query': q,
                'sql_query': sql_query,
                'model_used': sql_result.get("model_used"),
                'total_tokens': sql_result.get("total_tokens")
            }
        
        # Execute the SQL query if requested
        if not sql_query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to generate SQL query"
            )
        
        # Determine which database to use based on the SQL query
        db_conn = get_american_law_db(read_only=True) or None
        cursor = db_conn.cursor()
        
        # Limit results for safety
        if " LIMIT " not in sql_query.upper():
            if ";" in sql_query:
                sql_query = sql_query.replace(";", " LIMIT 100;")
            else:
                sql_query = f"{sql_query} LIMIT 100"
        
        # Execute the SQL query
        try:
            cursor.execute(sql_query)
            results = [dict(row) for row in cursor.fetchall()]
            
            return {
                'original_query': q,
                'sql_query': sql_query,
                'results': results,
                'total_results': len(results),
                'model_used': sql_result.get("model_used"),
                'total_tokens': sql_result.get("total_tokens")
            }
        except sqlite3.Error as e:
            logger.error(f"SQL execution error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SQL execution error: {str(e)}"
            )
        finally:
            db_conn.close()
    
    except Exception as e:
        logger.error(f"Error in convert_to_sql: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("chatbot.app:app", host="0.0.0.0", port=8080, reload=True)