CREATE TABLE IF NOT EXISTS embeddings (
    embedding_cid VARCHAR PRIMARY KEY,
    gnis VARCHAR NOT NULL,
    cid VARCHAR NOT NULL,
    text_chunk_order INTEGER NOT NULL,
    embedding DOUBLE[1536] NOT NULL
);