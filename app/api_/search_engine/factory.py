
from unittest.mock import MagicMock, AsyncMock

from configs import configs
from logger import logger
from .search_engine import SearchEngine

def make_search_engine() -> SearchEngine:
    """Factory function to create a SearchEngine instance with necessary resources."""

    resources = {
        "ranking_algorithm": AsyncMock(),
        "text_search": AsyncMock(),
        "image_search": AsyncMock(),
        "voice_search": AsyncMock(),
        "exact_match": AsyncMock(),
        "fuzzy_match": AsyncMock(),
        "string_exclusion": AsyncMock(),
        "filter_criteria": AsyncMock(),
        "multi_field_search": AsyncMock(),
        "query_parser": AsyncMock(),
        "word_piece_tokenizer": AsyncMock(),
        "db": AsyncMock(),
        "llm": AsyncMock(),
        "logger": logger, # Use module level logger.
    }

    return SearchEngine(resources=resources, configs=configs)

