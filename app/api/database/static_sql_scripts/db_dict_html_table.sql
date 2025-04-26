CREATE TABLE IF NOT EXISTS html (
    cid VARCHAR PRIMARY KEY,
    doc_id VARCHAR NOT NULL,
    doc_order INTEGER NOT NULL,
    html_title TEXT NOT NULL,
    html TEXT NOT NULL,
    gnis VARCHAR NOT NULL
);