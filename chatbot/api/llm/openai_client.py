"""
OpenAI Client implementation for American Law database.
Provides integration with OpenAI APIs and RAG components for legal research.
"""
import os
import numpy as np
from typing import List, Dict, Any, Optional
from openai import OpenAI
from pathlib import Path
import sqlite3
from typing import Annotated, Callable, Literal, Never



import duckdb
import numpy as np
import pandas as pd
from pydantic import AfterValidator as AV, BaseModel, BeforeValidator as BV, computed_field, PrivateAttr, TypeAdapter, ValidationError
import tiktoken
import yaml


from logger import logger
from configs import configs, Configs
from utils.chatbot.clean_html import clean_html
from utils.safe_format import safe_format
from utils.llm.cosine_similarity import cosine_similarity 
#from ._test_db import test_html_db

#test_html_db()

def validate_prompt(prompt: str) -> Never:
    if "role" not in prompt:
        raise ValidationError("Prompt must contain 'role' key.")
    if "content" not in prompt:
        raise ValidationError("Prompt must contain 'content' key.")

class PromptFields(BaseModel):
    role: str
    content: str

class Prompt(BaseModel):
    client: Literal['openai']
    system_prompt: PromptFields
    user_prompt: PromptFields   

    def safe_format(self, **kwargs) -> None:
        if not kwargs:
            return self.model_dump()
        
        sys_kwargs = {k: v for k, v in kwargs.items() if k in self.system_prompt.content}
        user_kwargs = {k: v for k, v in kwargs.items() if k in self.user_prompt.content}

        self.system_prompt.content = safe_format(self.system_prompt.content, **sys_kwargs)
        self.user_prompt.content = safe_format(self.user_prompt.content, **user_kwargs)


def _load_prompt_from_yaml(name: str, configs: Configs, **kwargs) -> Prompt:
    prompt_dir = configs.PROMPTS_DIR
    prompt_path = prompt_dir / f"{name}.yaml"

    with open(prompt_path, 'r') as file:
        prompt = dict(yaml.safe_load(file))
        return Prompt.model_validate(prompt).safe_format(**kwargs)


# From: https://platform.openai.com/docs/pricing
MODEL_USAGE_COSTS_USD_PER_MILLION_TOKENS = {
    "gpt-4o": {
        "input": 2.50,
        "output": 10.00
    },
    "gpt-4.5-preview": {
        "input": 75.00,
        "output": 150.00
    },
    "gpt-4-turbo": {
        "input": 10.00,
        "output": 30.00
    },
    "gpt-4": {
        "input": 30.00,
        "output": 60.00
    },
    "gpt-4-32k": {
        "input": 60.00,
        "output": 120.00
    },
    "gpt-3.5-turbo": {
        "input": 0.50,
        "output": 1.50
    },
    "gpt-3.5-turbo-instruct": {
        "input": 1.50,
        "output": 2.00
    },
    "gpt-3.5-turbo-16k-0613": {
        "input": 3.00,
        "output": 4.00
    },
    "gpt-4o-mini": {
        "input": 0.15,
        "output": 0.60
    },
    "o1": {
        "input": 15.00,
        "output": 60.00
    },
    "o1-pro": {
        "input": 150.00,
        "output": 600.00
    },
    "o1-mini": {
        "input": 1.10,
        "output": 4.40
    },
    "o3-mini": {
        "input": 1.10,
        "output": 4.40
    },
    "chatgpt-4o-latest": {
        "input": 5.00,
        "output": 15.00
    },
    "text-embedding-3-small": {
        "input": 0.02,
        "output": None
    },
    "text-embedding-3-large": {
        "input": 0.13,
        "output": None
    },
    "text-embedding-ada-002": {
        "input": 0.10,
        "output": None
    },
    "davinci-002": {
        "input": 2.00,
        "output": 2.00
    },
    "babbage-002": {
        "input": 0.40,
        "output": 0.40
    }
}


def calculate_cost(prompt: str, data: str, out: str, model: str) -> Optional[int]:
    # Initialize the tokenizer for the GPT model
    if model not in MODEL_USAGE_COSTS_USD_PER_MILLION_TOKENS:
        logger.error(f"Model {model} not found in usage costs.")
        return

    if model not in tiktoken.model.MODEL_PREFIX_TO_ENCODING.keys() or model not in tiktoken.model.MODEL_TO_ENCODING.keys():
        logger.error(f"Model {model} not found in tiktoken.")
        return

    tokenizer = tiktoken.encoding_for_model(model)

    # request and response
    request = str(prompt) + str(data)
    response = str(out)

    # Tokenize 
    request_tokens = tokenizer.encode(request)
    response_tokens = tokenizer.encode(response)

    # Counting the total tokens for request and response separately
    input_tokens = len(request_tokens)
    output_tokens = len(response_tokens)

    # Actual costs per 1 million tokens
    cost_per_1M_input_tokens = MODEL_USAGE_COSTS_USD_PER_MILLION_TOKENS[model]["input"]
    cost_per_1M_output_tokens = MODEL_USAGE_COSTS_USD_PER_MILLION_TOKENS[model]["output"]

    if cost_per_1M_output_tokens is None:
        output_cost = 0
    else:
        output_cost = (output_tokens / 10**6) * cost_per_1M_output_tokens
        
    input_cost = (input_tokens / 10**6) * cost_per_1M_input_tokens
    total_cost = input_cost + output_cost
    return total_cost




class LLMInput(BaseModel):
    client: BaseModel
    user_message: str
    system_prompt: str = "You are a helpful assistant."
    use_rag: bool = False
    max_tokens: int = 4096
    temperature: float = 0 # Deterministic output
    response_parser: Callable = lambda x: x # This should be a partial function.
    formatting: Optional[str] = None

    _configs: Configs = PrivateAttr(default=configs)

    @computed_field # type: ignore[prop-decorator]
    @property
    def response(self) -> Optional[Any]:

        if self.use_rag:
            # Get an embedding of user_message.
            self.user_message

        try:
            _response = self.client.chat.completions.create(
                model=self._configs.OPENAI_MODEL,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": self.system_prompt.strip()},
                    {"role": "user", "content": self.user_message}
                ]
            )
        except Exception as e:
            logger.error(f"{type(e)} generating response: {e}")
            return "Error generating response. Please try again."

        if _response.choices[0].message.content:
            return LLMOutput(
                response=_response.choices[0].message.content.strip(),
                system_prompt=self.system_prompt.strip(),
                user_message=self.user_message,
                context_used=_response.usage.total_tokens,
                model=self._configs.OPENAI_MODEL,
                response_parser=self.response_parser,
            )
        else:
            return "No response generated. Please try again."

    @computed_field # type: ignore[prop-decorator]
    @property
    def embedding(self) -> List[float]:
        """
        Generate an embedding for a single text input.
        
        Args:
            text: Text string to generate an embedding for
            
        Returns:
            Embedding vector
        """
        try:
            embeddings = self.client.embeddings.create(
                input=self.user_message,
                model=self._configs.OPENAI_EMBEDDING_MODEL
            )
        except Exception as e:
            logger.error(f"{type(e)} generating embedding: {e}")
            return []

        if embeddings.data[0].embedding:
            return embeddings.data[0].embedding
        else:
            logger.error("No embedding generated. Please try again.")
            return []



class LLMOutput(BaseModel):
    response: str
    system_prompt: str
    user_message: str
    context_used: int
    response_parser: Callable

    _configs: Configs = PrivateAttr(default=configs)

    @computed_field # type: ignore[prop-decorator]
    @property
    def cost(self) -> float:
        if self.response is not None:
            return calculate_cost(self.system_prompt, self.user_message, self.response, self._configs.OPENAI_MODEL)
        else: 
            return 0

    def response(self) -> Any:
        return self.response_parser(self.response)


class OpenAIClient:
    """
    Client for OpenAI API integration with RAG capabilities for the American Law dataset.
    Handles embeddings integration and semantic search against the law database.
    """
    
    def __init__(
        self, 
        api_key: str = None,
        model: str = "gpt-4o",
        embedding_model: str = "text-embedding-3-small",
        embedding_dimensions: int = 1536,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        configs: Optional[Configs] = None
    ):
        """
        Initialize the OpenAI client for American Law dataset RAG.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env variable)
            model: OpenAI model to use for completion/chat
            embedding_model: OpenAI model to use for embeddings
            embedding_dimensions: Dimensions of the embedding vectors
            temperature: Temperature setting for LLM responses
            max_tokens: Maximum tokens for LLM responses
            data_path: Path to the American Law dataset files
            db_path: Path to the SQLite database
        """
        self.configs = configs

        self.api_key = api_key
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided either as an argument or in the OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Set data paths
        self.data_path = configs.AMERICAN_LAW_DATA_DIR
        self.db_path = configs.AMERICAN_LAW_DB_PATH

        logger.info(f"Initialized OpenAI client: LLM model: {model}, embedding model: {embedding_model}")


    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text inputs using OpenAI's embedding model.
        
        Args:
            texts: List of text strings to generate embeddings for
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        try:
            # Prepare texts by stripping whitespace and handling empty strings
            processed_texts = [text.strip() for text in texts]
            processed_texts = [text if text else " " for text in processed_texts]

            response = self.client.embeddings.create(
                input=processed_texts,
                model=self.embedding_model
            )
            
            # Extract the embedding vectors from the response
            embeddings = [data.embedding for data in response.data]
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    

    def get_single_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for a single text input.
        
        Args:
            text: Text string to generate an embedding for
            
        Returns:
            Embedding vector
        """
        embeddings = self.get_embeddings([text])
        if embeddings:
            return embeddings[0]
        return []

    def search_embeddings(
        self, 
        query: str, 
        gnis: Optional[str] = None, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using embeddings.
        
        Args:
            query: Search query
            gnis: Optional file ID to limit search to
            top_k: Number of top results to return
            
        Returns:
            List of relevant documents with similarity scores
        """
        # Generate embedding for the query
        query_embedding = self.get_single_embedding(query)
        
        results = []

        try:
            # Connect to the database
            conn = duckdb.connect(self.db_path, read_only=True)
            
            # Create the SQL query
            sql_query = """
            WITH query_embedding AS (
                SELECT UNNEST($1) as vec
            ), 
            similarity_scores AS (
                SELECT 
                c.id, 
                c.cid, 
                c.title, 
                c.chapter, 
                c.place_name, 
                c.state_name, 
                c.date, 
                c.bluebook_citation, 
                c.content, 
                DOT_PRODUCT(e.embedding, ARRAY(SELECT vec FROM query_embedding)) / 
                (SQRT(DOT_PRODUCT(e.embedding, e.embedding)) * 
                 SQRT(DOT_PRODUCT(ARRAY(SELECT vec FROM query_embedding), 
                          ARRAY(SELECT vec FROM query_embedding)))) as similarity_score 
                FROM 
                citations c 
                JOIN 
                embeddings e ON c.id = e.citation_id 
                WHERE 
                1=1
            """
            
            # Add GNIS filter if provided
            if gnis:
                sql_query += f" AND c.gnis = '{gnis}'"
                
                sql_query += """
                )
                SELECT * FROM similarity_scores
                ORDER BY similarity_score DESC
                LIMIT {top_k}
                """
                
            # Execute the query with the embedding as parameter
            result_df = conn.execute(sql_query, [query_embedding]).fetchdf()
            
            # Convert to list of dictionaries
            results = []
            for _, row in result_df.iterrows():
                results.append({
                    'id': row['id'],
                    'cid': row['cid'],
                    'title': row['title'],
                    'chapter': row['chapter'],
                    'place_name': row['place_name'],
                    'state_name': row['state_name'],
                    'date': row['date'],
                    'bluebook_citation': row['bluebook_citation'],
                    'content': row['content'],
                    'similarity_score': float(row['similarity_score'])
                })

            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error searching embeddings with DuckDB: {e}")
            return []
        
    def query_database(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Query the database for relevant laws using DuckDB.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching law records
        """
        try:
            
            # Connect to the database - DuckDB can also connect to SQLite files
            conn = duckdb.connect(self.db_path, read_only=True)
            
            # Simple text search
            sql_query = f"""
                SELECT id, cid, title, chapter, place_name, state_name, date, 
                       bluebook_citation, content
                FROM citations
                WHERE lower(search_text) LIKE '%{query.lower()}%'
                ORDER BY place_name, title
                LIMIT {limit}
            """
            # Execute query and fetch results
            result_df = conn.execute(sql_query).fetchdf()
            
            # Convert DataFrame to list of dictionaries
            results = result_df.to_dict('records')
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error querying database with DuckDB: {e}")
            return []
        

    def generate_rag_response(
        self, 
        query: str, 
        use_embeddings: bool = True,
        context_limit: int = 5,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using RAG (Retrieval Augmented Generation).
        
        Args:
            query: User query
            use_embeddings: Whether to use embeddings for search
            context_limit: Number of context documents to include
            system_prompt: Custom system prompt
            
        Returns:
            Dictionary with the generated response and context used
        """
        # Retrieve relevant context
        context_docs = []
        
        if use_embeddings:
            # Use embedding-based semantic search
            context_docs = self.search_embeddings(query, top_k=context_limit)
        else:
            # Use database text search as fallback
            context_docs = self.query_database(query, limit=context_limit)

        # Build context for the prompt
        context_text = "Relevant legal information:\n\n"
        references = "Citation(s):\n\n"

        for i, doc in enumerate(context_docs):
            context_text += f"[{i+1}] {doc.get('title', 'Untitled')} - {doc.get('place_name', 'Unknown location')}, {doc.get('state_name', 'Unknown state')}\n"
            references += f"{i+1}. {doc.get('bluebook_citation', 'No citation available')}\n"
            context_text += f"Citation: {doc.get('bluebook_citation', 'No citation available')}\n"
            # Limit html to avoid excessively long prompts
            html = doc.get('html', '')
            if html:
                # Turn the HTML into a string.
                content = clean_html(html)
                content = content[:1000] + "..." if len(content) > 1000 else content
                context_text += f"Content: {content}\n\n"
        
        # Default system prompt if none provided
        if system_prompt is None:
            system_prompt = """
    You are a legal research assistant specializing in American municipal and county laws. 
    Answer questions based on the provided legal context information. 
    If the provided context doesn't contain enough information to answer the question confidently, 
    acknowledge the limitations of the available information and suggest what additional 
    information might be helpful.
    For legal citations, use Bluebook format when available. Be concise but thorough.
        """
        # Generate response using OpenAI
        prompt = _load_prompt_from_yaml("generate_rag_response", self.configs, query=query, context=context_text)
        try:
            response = LLMInput(
                client=self.client,
                user_message=f"Question: {query}\n\n{context_text}",
                system_prompt=system_prompt.strip(),
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            output = response.response
            if output is not None:
                # Append the citations
                generated_response += f"\n\n{references.strip()}"
            else:
                generated_response = "No response generated. Please try again."

            return {
                "query": query,
                "response": generated_response,
                "context_used": [doc.get('bluebook_citation', 'No citation') for doc in context_docs],
                "model_used": self.model,
                "total_tokens": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            return {
                "query": query,
                "response": f"Error generating response: {str(e)}",
                "context_used": [],
                "model_used": self.model,
                "error": str(e)
            }