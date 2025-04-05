#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations
import asyncio
import functools
from dotenv import load_dotenv
import os
from pathlib import Path
import sqlite3
import time
import traceback
from typing import Annotated, Any, Callable, Dict, List, NamedTuple, Optional, Union


import duckdb
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AfterValidator as AV, BaseModel, BeforeValidator as BV, Field, field_validator



from configs import configs
from logger import logger
from chatbot.api.llm.async_interface import AsyncLLMInterface
from utils.app.search.format_initial_sql_return_from_search import format_initial_sql_return_from_search
from utils.app.search.get_embedding_cids_for_all_the_cids import get_embedding_cids_for_all_the_cids
from utils.app.search.get_the_llm_to_parse_the_plaintext_query_into_a_sql_command import (
    get_the_llm_to_parse_the_plaintext_query_into_a_sql_command
)
from utils.app.search.get_embedding_and_calculate_cosine_similarity import (
    get_embedding_and_calculate_cosine_similarity
)
from utils.database.get_db import get_citation_db, get_html_db, get_embeddings_db
from utils.llm.cosine_similarity import cosine_similarity
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
llm_interface = None
try:
    openai_api_key = os.environ.get("OPENAI_API_KEY") or configs.OPENAI_API_KEY.get_secret_value()
    data_path = os.environ.get("AMERICAN_LAW_DATA_DIR") or configs.AMERICAN_LAW_DATA_DIR
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")
    raise e

try:
    llm_interface = AsyncLLMInterface(
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


def _fallback_search(query: str, per_page: int, offset: int) -> tuple[list[dict], int]:
    """
    Fallback to standard search if LLM not used or SQL failed
    """
    citation_conn = get_citation_db(True)
    citation_cursor = citation_conn.cursor()
    
    # Count total results
    citation_cursor.execute('''
    SELECT COUNT(*) as total
    FROM citations
    WHERE title LIKE ? OR chapter LIKE ? OR place_name LIKE ?
    ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
    total = citation_cursor.fetchone()[0]
    logger.debug(f"Total results: {total}")
    
    # Get paginated results
    citation_cursor.execute('''
    SELECT bluebook_cid, title, chapter, place_name, state_name, date, 
            bluebook_citation, cid
    FROM citations
    WHERE title LIKE ? OR chapter LIKE ? OR place_name LIKE ?
    ORDER BY place_name, title
    LIMIT ? OFFSET ?
    ''', (f'%{query}%', f'%{query}%', f'%{query}%', per_page, offset))
    
    results = []
    html_set = set()
    for row in citation_cursor.fetchdf().itertuples(index=False):

        html: str = _get_html_for_this_citation(row)
        if html in html_set:
            continue
        else:
            html_set.add(html)

        results.append({
            'cid': row.cid,
            'title': row.title,
            'chapter': row.chapter,
            'place_name': row.place_name,
            'state_name': row.state_name,
            #'date': row.date,
            'bluebook_citation': row.bluebook_citation,
            'html': html
        })

    citation_conn.close()
    return results, total


class SqlQueryResponse(BaseModel):
    sql_query: str
    model_used: str
    total_tokens: int


async def _determine_user_intent(
    query: str,
) -> str:
    """
    Determine what a user wants to do with the search query asynchronously.
    This function will be used to determine if the user wants to search, ask a question, convert to SQL, etc.
    """
    intent = await llm_interface.determine_user_intent(query.lower())
    if intent is not None:
        logger.debug(f"User intent: {intent}")
        return intent
    else:
        raise ValueError("LLM was unable to determine user intent")



@app.get("/api/search", response_model=SearchResponse)
async def search(
    q: str = Query("", description="Search query"),
    page: int = Query(1, description="Page number"),
    per_page: int = Query(20, description="Items per page"),
    use_llm: bool = Query(True, description="Use LLM to parse query into SQL")
) -> None:
    """
    Search for citations in the database using a natural language query.
    This endpoint uses the LLM to convert the query into SQL and execute it.
    """
    logger.debug("Received request for search")
    query = q.lower()
    offset = (page - 1) * per_page
    logger.debug(f"Received search query: {query}")

    try:
        await _determine_user_intent(q)
    except Exception as e:
        logger.error(f"Error determining user intent: {e}")
        raise HTTPException(status_code=400, detail="Unable to determine user intent")

    # Get an embedding of the query.
    query_embedding: list[float] = await llm_interface.openai_client.get_single_embedding(query)

    try:
        sql_query = await get_the_llm_to_parse_the_plaintext_query_into_a_sql_command(
            search_query=query,
            use_llm=use_llm,
            per_page=per_page,
            offset=offset,
            llm_interface=llm_interface
        )
        results = []
        total = 0
        read_only = True
        db_conn: duckdb.DuckDBPyConnection = None

        if sql_query:
            if "```sql" in sql_query:
                # Strip out any markdown formatting if present
                sql_query = sql_query.replace("```sql","").replace("```","").strip()

            # Determine which database to use based on the SQL query
            if "citations" in sql_query.lower():
                db_conn = get_citation_db(read_only)
            elif "html" in sql_query.lower():
                db_conn = get_html_db(read_only)
            elif "embeddings" in sql_query.lower():
                db_conn = get_embeddings_db(read_only)
            else:
                # Default to citation database
                db_conn = get_citation_db(read_only)

            cursor = db_conn.cursor()

            #sql_result = llm_interface.query_to_sql(q)

            # Execute the generated SQL query
            logger.debug(f"sql_query: {sql_query}")
            try:
                html_set = set()
                cid_set = set()

                # First, estimate the total count without pagination
                count_query = f"SELECT COUNT(*) as total FROM ({sql_query.split('LIMIT')[0]}) as subquery"
                cursor.execute(count_query)
                total: tuple[tuple] = cursor.fetchone()[0]
                logger.debug(f"Total results from SQL query: {total}")

                # If total is not zero, execute the actual query
                if total != 0:

                    # Then execute the actual query with pagination
                    cursor.execute(sql_query)
                    df_dict = cursor.fetchdf().to_dict('records')

                    initial_results: list[dict] = []
                    for row in df_dict:
                        #logger.debug(f"type(row): {type(row)}\nRow: {row}")

                        # If the CID isn't there or if it's already in the set, continue.
                        if "cid" not in row.keys() or row['cid'] in cid_set:
                            continue
                        else:
                            logger.debug(f"Adding cid {row['cid']} to cid_set")
                            cid_set.add(row['cid'])

                        if "bluebook_cid" in row.keys():
                            row_dict = format_initial_sql_return_from_search(row)
                            initial_results.append(row_dict)

                    embedding_id_list: list[dict] = get_embedding_cids_for_all_the_cids(initial_results)
                    if not isinstance(embedding_id_list[0], dict):
                        logger.debug(f"type(embedding_id_list[0]): {type(embedding_id_list[0])}")
                        logger.debug(f"embedding_id_list: {embedding_id_list}")

                    func: Callable = functools.partial(
                        get_embedding_and_calculate_cosine_similarity,
                        query_embedding=query_embedding,
                    )

                    # Use a process pool to calculate cosine similarity for each embedding
                    pull_list = []
                    async for _, embedding_id in async_run_in_process_pool(func, embedding_id_list):
                        if embedding_id is not None:
                            pull_list.append(embedding_id)

                    # Order the pull list by their cosine similarity score.
                    pull_list = sorted(pull_list, key=lambda x: x[1], reverse=True)
                    logger.debug(f"pull_list: {pull_list}") 

                    results = []
                    for cid, _ in pull_list:
                        # Find the corresponding row in the initial results
                        for row_dict in initial_results:
                            if row_dict['cid'] == cid:
                                # Get the HTML content for this citation
                                html: str = _get_html_for_this_citation(row_dict)
                                if html in html_set:
                                    break
                                else:
                                    html_set.add(html)
                                    row_dict['html'] = html
                                    results.append(row_dict)
                                    break

            except duckdb.BinderException as e:
                logger.error(f"duckdby.BinderException error: {e}")
            finally:
                db_conn.close()
        else:
            # Fallback to standard search if LLM not used or SQL failed
            results, total = _fallback_search(query, per_page, offset)

        total_pages = total + per_page - 1
        total_pages //= per_page 
        output = {
            'results': results,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }
        logger.debug(f"Search results: {output}")
        return output

    except Exception as e:
        logger.error(f"Error in search: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def make_query_hash_table():
    """
    Create a hash table for the citation database.
    NOTE: query_cid is made from the hash of the query string.
    """
    with duckdb.connect(configs.AMERICAN_LAW_DB_PATH, read_only=True) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_hash (
                query_cid VARCHAR PRIMARY KEY,
                user_query TEXT NOT NULL,
                embedding DOUBLE[1536] NOT NULL
            )
            ''')


def make_stats_table():
    """
    Create a stats table for the citation database.
    """
    with duckdb.connect(configs.AMERICAN_LAW_DB_PATH, read_only=True) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                run_cid VARCHAR PRIMARY KEY,
                query_cid VARCHAR NOT NULL,
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
    if not llm_interface:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM features are not available. Please set OPENAI_API_KEY."
        )
    
    try:
        query = request.query
        
        response = await llm_interface.ask_question(
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
    if not llm_interface:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM features are not available. Please set OPENAI_API_KEY."
        )
    
    try:
        query = request.query
        
        results = await llm_interface.search_embeddings(
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
    if not llm_interface:
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
        
        response = await llm_interface.generate_citation_answer(
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
    if llm_interface:
        return {
            'status': 'available',
            'model': llm_interface.openai_client.model,
            'embedding_model': llm_interface.openai_client.embedding_model
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
    if not llm_interface:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM features are not available. Please set OPENAI_API_KEY."
        )
    
    try:
        # Generate SQL query
        sql_result = await llm_interface.query_to_sql(q)
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
        db_conn = None
        if "citations" in sql_query.lower():
            db_conn = get_citation_db()
        elif "html" in sql_query.lower():
            db_conn = get_html_db()
        elif "embeddings" in sql_query.lower():
            db_conn = get_embeddings_db()
        else:
            # Default to citation database
            db_conn = get_citation_db()
        
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