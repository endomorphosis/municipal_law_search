"""
OpenAI Client implementation for American Law database.
Provides integration with OpenAI APIs and RAG components for legal research.
"""
import os
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from openai import OpenAI
import logging
from pathlib import Path
import sqlite3


from chatbot.logger import logger


class OpenAIClient:
    """
    Client for OpenAI API integration with RAG capabilities for the American Law dataset.
    Handles embeddings integration and semantic search against the law database.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        embedding_model: str = "text-embedding-3-large",
        embedding_dimensions: int = 1536,
        temperature: float = 0.2,
        max_tokens: int = 1000,
        data_path: Optional[str] = None,
        db_path: Optional[str] = None
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
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided either as an argument or in the OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Set data paths
        self.data_path = data_path or os.environ.get("AMERICAN_LAW_DATA_DIR")
        self.db_path = db_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "american_law.db")
        
        logger.info(f"Initialized OpenAI client with model: {model}, embedding model: {embedding_model}")
    
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
    
    def vector_similarity(self, x: List[float], y: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            x: First vector
            y: Second vector
            
        Returns:
            Cosine similarity score
        """
        return np.dot(np.array(x), np.array(y)) / (
            np.linalg.norm(np.array(x)) * np.linalg.norm(np.array(y))
        )
    
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
        
        # If gnis is provided, search only in that file
        if gnis:
            embedding_file = os.path.join(self.data_path, f"{gnis}_embeddings.parquet")
            citation_file = os.path.join(self.data_path, f"{gnis}_citation.parquet")
            html_file = os.path.join(self.data_path, f"{gnis}_html.parquet")
            
            if not os.path.exists(embedding_file):
                logger.error(f"Embedding file not found: {embedding_file}")
                return []
            
            embedding_df = pd.read_parquet(embedding_file)
            citation_df = pd.read_parquet(citation_file)
            html_df = pd.read_parquet(html_file)
            
            # Calculate similarity scores
            for _, row in embedding_df.iterrows():
                similarity = self.vector_similarity(query_embedding, row['embedding'])
                
                # Get citation and HTML data
                citation_row = citation_df[citation_df['cid'] == row['cid']].iloc[0] if not citation_df[citation_df['cid'] == row['cid']].empty else None
                html_row = html_df[html_df['cid'] == row['cid']].iloc[0] if not html_df[html_df['cid'] == row['cid']].empty else None
                
                if citation_row is not None and html_row is not None:
                    results.append({
                        'cid': row['cid'],
                        'title': citation_row['title'],
                        'chapter': citation_row['chapter'],
                        'place_name': citation_row['place_name'],
                        'state_name': citation_row['state_name'],
                        'bluebook_citation': citation_row['bluebook_citation'],
                        'html_content': html_row['html'],
                        'similarity_score': float(similarity)
                    })
        else:
            # Without a specific gnis, we'll need to scan all embedding files
            # This could be slow for large datasets, so we'll limit to a sample
            embedding_files = list(Path(self.data_path).glob("*_embeddings.parquet"))[:10]  # Limiting to 10 files for performance
            
            for emb_file in embedding_files:
                gnis = os.path.basename(emb_file).split('_')[0]
                citation_file = os.path.join(self.data_path, f"{gnis}_citation.parquet")
                html_file = os.path.join(self.data_path, f"{gnis}_html.parquet")
                
                if not os.path.exists(citation_file) or not os.path.exists(html_file):
                    continue
                
                embedding_df = pd.read_parquet(emb_file)
                citation_df = pd.read_parquet(citation_file)
                html_df = pd.read_parquet(html_file)
                
                # Calculate similarity scores for this file
                for _, row in embedding_df.iterrows():
                    similarity = self.vector_similarity(query_embedding, row['embedding'])
                    
                    # Get citation and HTML data
                    citation_row = citation_df[citation_df['cid'] == row['cid']].iloc[0] if not citation_df[citation_df['cid'] == row['cid']].empty else None
                    html_row = html_df[html_df['cid'] == row['cid']].iloc[0] if not html_df[html_df['cid'] == row['cid']].empty else None
                    
                    if citation_row is not None and html_row is not None:
                        results.append({
                            'cid': row['cid'],
                            'title': citation_row['title'],
                            'chapter': citation_row['chapter'],
                            'place_name': citation_row['place_name'],
                            'state_name': citation_row['state_name'],
                            'bluebook_citation': citation_row['bluebook_citation'],
                            'html_content': html_row['html'],
                            'similarity_score': float(similarity)
                        })
        
        # Sort by similarity score and get top_k results
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:top_k]
    
    def query_database(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Query the SQLite database for relevant laws.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching law records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Simple text search
            cursor.execute('''
                SELECT id, cid, title, chapter, place_name, state_name, date, 
                       bluebook_citation, content
                FROM laws
                WHERE search_text LIKE ?
                ORDER BY place_name, title
                LIMIT ?
            ''', (f'%{query.lower()}%', limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'cid': row['cid'],
                    'title': row['title'],
                    'chapter': row['chapter'],
                    'place_name': row['place_name'],
                    'state_name': row['state_name'],
                    'date': row['date'],
                    'bluebook_citation': row['bluebook_citation'],
                    'content': row['content']
                })
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error querying database: {e}")
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
        for i, doc in enumerate(context_docs):
            context_text += f"[{i+1}] {doc.get('title', 'Untitled')} - {doc.get('place_name', 'Unknown location')}, {doc.get('state_name', 'Unknown state')}\n"
            context_text += f"Citation: {doc.get('bluebook_citation', 'No citation available')}\n"
            # Limit content to avoid excessively long prompts
            content = doc.get('content', '') or doc.get('html_content', '')
            if content:
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
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt.strip()},
                    {"role": "user", "content": f"Question: {query}\n\n{context_text}"}
                ]
            )
            
            return {
                "query": query,
                "response": response.choices[0].message.content,
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