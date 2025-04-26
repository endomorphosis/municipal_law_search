"""
Use an LLM with GraphRAG to answer questions about American municipal law.
"""
from pathlib import Path
from typing import Callable


from configs import configs, Configs


from app.llm import LLM
from app.api.llm.async_interface import AsyncLLMInterface


class TalkWithLaw:
    """
    Use an LLM with GraphRAG to answer questions about American municipal law.
    
    This class provides methods to query the database and retrieve information
    about American municipal law using a language model.
    
    Attributes:
        db_path (str): Path to the American law database.
        model (str): Language model to use for processing.
    """
    
    def __init__(self, 
                 db_path: str, 
                 resources: dict[str, Callable] = None,
                 configs: Configs = None
                 ) -> None:
        self.configs = configs
        self.resources = resources

        self.db_path: Path = Path(db_path)
        self.llm: AsyncLLMInterface = self.resources['LLM']

resources = {
    'LLM': LLM,
}



async def function():
    pass