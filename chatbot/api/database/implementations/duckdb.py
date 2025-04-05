from typing import List, Dict, Any


import duckdb


from configs import Configs
from logger import logger


class DuckDbClient:


    def __init__(self, resources=None, configs: Configs = None):
        """
        Initialize the DuckDB client.
        
        Args:
            db_path: Path to the DuckDB database file
        """
        self.configs = configs
        self.resources = resources

        self.db_path = configs.AMERICAN_LAW_DB_PATH


    def execute_sql_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query against the DuckDB database.
        
        Args:
            query: SQL query string
            
        Returns:
            List of dictionaries representing the query results
        """
        try:
            # Connect to the database
            with duckdb.connect(self.db_path, read_only=True) as conn:
                # Execute the query and fetch results
                results = conn.execute(query).fetchdf().to_dict('records')
                return results

        except Exception as e:
            logger.error(f"Error executing DuckDB query: {e}")
            return []