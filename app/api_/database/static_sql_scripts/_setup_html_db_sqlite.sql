CREATE TABLE html (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cid TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    doc_order INTEGER NOT NULL,
    html_title TEXT NOT NULL,
    html TEXT NOT NULL,
    index_level_0 INTEGER
);