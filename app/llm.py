# -*- coding: utf-8 -*-
"""
Initialize singleton for LLM.
"""
import os
from typing import TypeVar


from app import configs
from app import logger
from app.api.llm.async_interface import AsyncLLMInterface
from app.api.llm.embeddings_utils import EmbeddingsManager
from app.api.llm.dependencies.async_openai_client import AsyncOpenAIClient

LlmClient = TypeVar("LlmClient")

# Initialize LLM interface if API key is available
LLM = None
try:
    openai_api_key = os.environ.get("OPENAI_API_KEY") or configs.OPENAI_API_KEY.get_secret_value()
    data_path = os.environ.get("AMERICAN_LAW_DATA_DIR") or configs.AMERICAN_LAW_DATA_DIR
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")
    raise e

resources = {
    "embeddings_manager": EmbeddingsManager(configs=configs),
    "async_client": AsyncOpenAIClient(
        api_key=configs.OPENAI_API_KEY.get_secret_value(),
        model=configs.OPENAI_MODEL,
        embedding_model=configs.OPENAI_EMBEDDING_MODEL,
        configs=configs
    )
}

try:
    LLM = AsyncLLMInterface(resources=resources, configs=configs)
    logger.info("LLM interface initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize LLM interface: {e}")
    raise e