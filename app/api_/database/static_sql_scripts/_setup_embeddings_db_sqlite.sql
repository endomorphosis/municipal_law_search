CREATE TABLE embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    embedding_cid TEXT NOT NULL,
    gnis TEXT NOT NULL,
    cid TEXT NOT NULL,
    text_chunk_order INTEGER NOT NULL,
    embedding_filepath TEXT NOT NULL,
    index_level_0 INTEGER
)