CREATE TABLE embeddings (
    id INTEGER PRIMARY KEY,
    embedding_cid VARCHAR NOT NULL,
    gnis VARCHAR NOT NULL,
    cid VARCHAR NOT NULL,
    text_chunk_order INTEGER NOT NULL,
    embedding_filepath VARCHAR NOT NULL,
    index_level_0 INTEGER
);