# -*- coding: utf-8 -*-
"""
Initialize singleton for LLM.
"""
import os
from typing import TypeVar


from configs import configs
from logger import logger
from api.llm.async_interface import AsyncLLMInterface

LlmClient = TypeVar("LlmClient")

# Initialize LLM interface if API key is available
LLM = None
try:
    openai_api_key = os.environ.get("OPENAI_API_KEY") or configs.OPENAI_API_KEY.get_secret_value()
    data_path = os.environ.get("AMERICAN_LAW_DATA_DIR") or configs.AMERICAN_LAW_DATA_DIR
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")
    raise e

try:
    LLM = AsyncLLMInterface(
        api_key=openai_api_key,
        configs=configs
    )
    logger.info("LLM interface initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize LLM interface: {e}")
    raise e