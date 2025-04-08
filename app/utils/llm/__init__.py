
"""
Language Model utility functions for the American Law Search application.

This package provides utilities for working with language models, including
vector similarity calculations and prompt template management. These utilities
support the LLM integration components of the application.
"""
from .cosine_similarity import cosine_similarity
from .load_prompt_from_yaml import load_prompt_from_yaml


__all__ = [
    "cosine_similarity",
    "load_prompt_from_yaml",
]

