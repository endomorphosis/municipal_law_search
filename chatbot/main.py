


from dotenv import load_dotenv
import os
from pathlib import Path
import sqlite3
from typing import Optional, List, Dict, Any, Union


import duckdb
from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


from api.llm.interface import LLMInterface
from configs import configs
from logger import logger
from api.database.setup_citation_db import setup_citation_db
from api.database.setup_html_db import setup_html_db
from api.database.setup_embeddings_db import setup_embeddings_db

# Load environment variables
load_dotenv()

# Create necessary databases
setup_embeddings_db()
setup_html_db()
setup_citation_db()


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
app.mount("/src", StaticFiles(directory="client/src"), name="src")
templates = Jinja2Templates(directory="client/public")


# Initialize LLM interface if API key is available
llm_interface = None
try:
    openai_api_key = os.environ.get("OPENAI_API_KEY") or configs.OPENAI_API_KEY.get_secret_value()
    data_path = os.environ.get("AMERICAN_LAW_DATA_DIR") or configs.AMERICAN_LAW_DATA_DIR
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")
    raise e

try:
    llm_interface = LLMInterface(
        api_key=configs.OPENAI_API_KEY.get_secret_value(),
        model=configs.OPENAI_MODEL,
        data_path=data_path
    )
    logger.info("LLM interface initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize LLM interface: {e}")
    raise e

citation_db = configs.AMERICAN_LAW_DATA_DIR / "citation.db"
html_db = configs.AMERICAN_LAW_DATA_DIR / "html.db"
embeddings_db = configs.AMERICAN_LAW_DATA_DIR / "embeddings.db"

def _get_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Database connections
def get_citation_db():
    return _get_db(citation_db)

def get_html_db():
    return _get_db(html_db)

def get_embeddings_db():
    return _get_db(embeddings_db)


# Pydantic models for request/response validation
class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    page: int
    per_page: int
    total_pages: int

class LawItem(BaseModel):
    id: int
    title: str
    chapter: Optional[str] = None
    place_name: Optional[str] = None
    state_name: Optional[str] = None
    date: Optional[str] = None
    bluebook_citation: Optional[str] = None
    content: str

class LLMAskRequest(BaseModel):
    query: str
    use_rag: bool = True
    use_embeddings: bool = True
    context_limit: int = 5
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
    return FileResponse(f"client/public/{filename}")

@app.get("/api/search", response_model=SearchResponse)
async def search(
    q: str = Query("", description="Search query"),
    page: int = Query(1, description="Page number"),
    per_page: int = Query(20, description="Items per page"),
    use_llm: bool = Query(True, description="Use LLM to parse query into SQL")
):
    query = q.lower()
    offset = (page - 1) * per_page
    
    try:
        # Get the LLM to parse the plaintext query into a SQL command if requested
        sql_query = None
        if use_llm and llm_interface and q.strip():
            logger.info(f"Converting query to SQL: {q}")
            sql_result = llm_interface.query_to_sql(q)
            sql_query = sql_result.get("sql_query")
            
            # Add pagination to the generated SQL if it doesn't already have it
            if sql_query and " LIMIT " not in sql_query.upper():
                if ";" in sql_query:
                    sql_query = sql_query.replace(";", f" LIMIT {per_page} OFFSET {offset};")
                else:
                    sql_query = f"{sql_query} LIMIT {per_page} OFFSET {offset}"
            
            logger.info(f"Generated SQL query: {sql_query}")
        
        results = []
        total = 0

        if sql_query:
            if "```sql" in sql_query:
                # Strip out any markdown formatting if present
                sql_query = sql_query.replace("```sql","").replace("```","").strip()

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
            
            # Execute the generated SQL query
            logger.debug(f"sql_query: {sql_query}")
            try:
                # First, estimate the total count without pagination
                count_query = f"SELECT COUNT(*) as total FROM ({sql_query.split('LIMIT')[0]}) as subquery"
                cursor.execute(count_query)
                total = cursor.fetchone()['total']
                
                # Then execute the actual query with pagination
                cursor.execute(sql_query)
                
                for row in cursor.fetchall():
                    row_dict = dict(row)
                    # Check if content exists and truncate if too long
                    if 'content' in row_dict:
                        row_dict['content'] = row_dict['content'][:500] + '...' if len(row_dict['content']) > 500 else row_dict['content']
                    results.append(row_dict)
                
            except sqlite3.Error as e:
                logger.error(f"SQL execution error: {e}")
                # Fallback to standard search if SQL fails
                sql_query = None
            finally:
                db_conn.close()
        
        # Fallback to standard search if LLM not used or SQL failed
        if not sql_query:
            citation_conn = get_citation_db()
            citation_cursor = citation_conn.cursor()
            
            # Count total results
            citation_cursor.execute('''
            SELECT COUNT(*) as total
            FROM citations
            WHERE title LIKE ? OR chapter LIKE ? OR place_name LIKE ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            total = citation_cursor.fetchone()['total']
            
            # Get paginated results
            citation_cursor.execute('''
            SELECT id, title, chapter, place_name, state_name, date, 
                   bluebook_citation, cid
            FROM citations
            WHERE title LIKE ? OR chapter LIKE ? OR place_name LIKE ?
            ORDER BY place_name, title
            LIMIT ? OFFSET ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', per_page, offset))
            
            results = []
            for row in citation_cursor.fetchall():
                # Get HTML content for this citation
                html_conn = get_html_db()
                html_cursor = html_conn.cursor()
                html_cursor.execute('SELECT html FROM html WHERE cid = ? LIMIT 1', (row['cid'],))
                html_result = html_cursor.fetchone()
                html_conn.close()
                
                content = html_result['html'] if html_result else "Content not available"
                
                results.append({
                    'id': row['id'],
                    'title': row['title'],
                    'chapter': row['chapter'],
                    'place_name': row['place_name'],
                    'state_name': row['state_name'],
                    'date': row['date'],
                    'bluebook_citation': row['bluebook_citation'],
                    'content': content[:500] + '...' if len(content) > 500 else content
                })
            
            citation_conn.close()
        
        return {
            'results': results,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/law/{law_id}", response_model=Union[LawItem, ErrorResponse])
async def get_law(law_id: int):
    html_conn = get_html_db()
    html_cursor = html_conn.cursor()
    
    html_cursor.execute('''
    SELECT *
    FROM laws
    WHERE id = ?
    ''', (law_id,))
    
    law = html_cursor.fetchone()
    html_conn.close()
    
    if law:
        return {
            'id': law['id'],
            'title': law['title'],
            'chapter': law['chapter'],
            'place_name': law['place_name'],
            'state_name': law['state_name'],
            'date': law['date'],
            'bluebook_citation': law['bluebook_citation'],
            'content': law['content']
        }
    else:
        raise HTTPException(status_code=404, detail="Law not found")

# LLM API routes
@app.post("/api/llm/ask")
async def ask_question(request: LLMAskRequest):
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
        
        response = llm_interface.ask_question(
            query=query,
            use_rag=request.use_rag,
            use_embeddings=request.use_embeddings,
            context_limit=request.context_limit,
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
    if not llm_interface:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM features are not available. Please set OPENAI_API_KEY."
        )
    
    try:
        query = request.query
        
        results = llm_interface.search_embeddings(
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
        
        response = llm_interface.generate_citation_answer(
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
    if not llm_interface:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM features are not available. Please set OPENAI_API_KEY."
        )
    
    try:
        # Generate SQL query
        sql_result = llm_interface.query_to_sql(q)
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
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)