
# Importing them should cause the database to be initialized and the tables to be created.
from .setup_citation_db import setup_citation_db
from .setup_embeddings_db import setup_embeddings_db
from .setup_html_db  import setup_html_db

__all__ = [
    "setup_citation_db",
    "setup_embeddings_db",
    "setup_html_db"
]