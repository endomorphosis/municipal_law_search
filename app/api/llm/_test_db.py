"""
OpenAI Client implementation for American Law database.
Provides integration with OpenAI APIs and RAG components for legal research.
"""
import duckdb


from configs import configs



TEST_QUERY_1 = """
SELECT c.bluebook_cid, c.title, c.chapter, c.place_name, c.state_name, c.bluebook_citation 
FROM citations c 
JOIN html h ON c.cid = h.cid 
WHERE c.state_name = 'California' AND h.html LIKE '%pets%' 
LIMIT 10;
"""

TEST_QUERY_2 = """
SELECT COUNT(c.bluebook_cid) FROM citations c JOIN html h ON c.cid = h.cid WHERE html LIKE '%pets%' LIMIT 10;
"""

TEST_QUERY_3 = """
SELECT * FROM citations LIMIT 1;
"""

TEST_QUERY_4 = """
SELECT DISTINCT * FROM html LIMIT 2;
"""

TEST_QUERY_5 = """
SELECT DISTINCT * FROM embeddings LIMIT 2;
"""

embeddings_db_path = configs.AMERICAN_LAW_DATA_DIR / "embeddings.db"
citations_db_path = configs.AMERICAN_LAW_DATA_DIR / "citations.db"
html_db_path = configs.AMERICAN_LAW_DATA_DIR / "html.db"
american_law_db_path = configs.AMERICAN_LAW_DB_PATH

def test_html_db():
    queries = [TEST_QUERY_3]
    conn = duckdb.connect(american_law_db_path, read_only=True)
    for query in queries:
        query = query.strip()
        conn.execute(query)
        results = conn.fetchdf().iterrows()
        for row in results:
            print(row)
        print(f"Query result: {results}")
    conn.close()
