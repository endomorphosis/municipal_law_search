import re
from typing import Optional


from app import logger


async def validate_and_correct_sql_query_string(sql_query: str, fix_broken_queries: bool = True) -> Optional[str]:
    """
    Validate and correct a SQL query string.
    
    Args:
        sql_query: The SQL query string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    logger.debug(f"Validating SQL query: {sql_query}")

    # Check if it's an empty string
    if not sql_query.strip():
        logger.warning("Empty SQL query string provided.")
        return None
    
    # Check if it any markdown patterns.
    if "```sql" in sql_query or "```" in sql_query:
        logger.warning("SQL query contains markdown code blocks.")
        if fix_broken_queries:
            # Remove markdown code blocks
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            logger.info("Removed markdown code blocks from SQL query.")
            logger.debug(f"Cleaned SQL query after markdown removal: {sql_query}")
        else:
            logger.error("SQL query contains markdown code blocks and fix_broken_queries is False.")
            return None

    # Check if it's got SELECT in it
    if not re.search(r'^\s*SELECT\s', sql_query, re.IGNORECASE):
        logger.warning("SQL query does not start with SELECT.")
        return None

    # Check if it's got doubled elements like SELECT SELECT or LIMIT 10 LIMIT 20
    sql_query = re.sub(r'\b(SELECT|LIMIT)\s+\1', r'\1', sql_query, flags=re.IGNORECASE).strip()
    logger.debug(f"Cleaned SQL query after doubled elements removal: {sql_query}")
    return sql_query if sql_query else None