from typing import Optional


from pydantic import BaseModel


class EmbeddingsRow(BaseModel):
    """
    A Pydantic model representing a row in the 'embeddings' table in embeddings.db and american_law.db.
    """
    embedding_cid: str = None
    cid: Optional[int] = None
    embedding: Optional[str] = None
    text_chunk_order: Optional[str] = None
    gnis: str | int  = None 