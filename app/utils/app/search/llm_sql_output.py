from typing import Annotated as Annot


from pydantic import BaseModel, AfterValidator as AV


from logger import logger


def _format_initial_sql_query_from_llm(sql_query: str) -> str:
    if "```sql" in sql_query:
        # Strip out any markdown formatting if present
        sql_query = sql_query.replace("```sql","").replace("```","").strip()

    if "LIMIT" in sql_query:
        # Get rid of any LIMIT, if there is any.
        logger.debug(f"sql_query: {sql_query}")
        sql_query = sql_query.split("LIMIT")[0].strip()
    
    return sql_query


class LLMSqlOutput(BaseModel):
    sql_query: Annot[str, AV(_format_initial_sql_query_from_llm)]
