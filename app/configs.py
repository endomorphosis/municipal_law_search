import os
from pathlib import Path
import sys

import torch
from pydantic import (
    BaseModel, 
    computed_field, 
    DirectoryPath, 
    Field, 
    SecretStr, 
    ValidationError
)
import yaml


_ROOT_DIR = Path(__file__).parent.parent

# Insert this file's directory to the system path
sys.path.insert(0, str(_ROOT_DIR))


def _USE_GPU_FOR_COSINE_SIMILARITY() -> str:
    """
    Determines if GPU is available for cosine similarity calculations.

    Returns:
        str: "cuda" if GPU is available, "cpu" otherwise.
    """
    return "cuda" if torch.cuda.is_available() else "cpu"


class Configs(BaseModel):
    """
    Configuration class for the American Law dataset upload to Hugging Face.

    This class defines all the necessary configurations for the project,
    including API keys, file paths, model specifications, and other settings.

    Attributes:
        OPENAI_API_KEY (SecretStr): Authentication key for OpenAI API.
        ROOT_DIR (DirectoryPath): Root directory of the project.
        AMERICAN_LAW_DATA_DIR (DirectoryPath): Directory containing the American Law data.
        PARQUET_FILES_DIR (DirectoryPath): Directory containing parquet files.
        AMERICAN_LAW_DB_PATH (DirectoryPath): Path to the American Law database file.
        PROMPTS_DIR (DirectoryPath): Directory containing LLM prompt templates.
        HUGGING_FACE_REPO_ID (str): Repository ID on Hugging Face for uploading.
        OPENAI_MODEL (str): OpenAI model to use for processing.
        OPENAI_EMBEDDING_MODEL (str): OpenAI model to use for text embeddings.
        LOG_LEVEL (int): Logging level for the application (10 = DEBUG).
        SIMILARITY_SCORE_THRESHOLD (float): Threshold for cosine similarity scoring.
    """
    OPENAI_API_KEY:                 SecretStr = os.environ.get("OPENAI_API_KEY")
    HUGGING_FACE_USER_ACCESS_TOKEN: SecretStr = None
    ROOT_DIR:                       DirectoryPath = _ROOT_DIR
    AMERICAN_LAW_DATA_DIR:          DirectoryPath = _ROOT_DIR / "data"
    PARQUET_FILES_DIR:              DirectoryPath = _ROOT_DIR / "data" / "parquet_files"
    AMERICAN_LAW_DB_PATH:           DirectoryPath = _ROOT_DIR / "data" / "american_law.db"
    PROMPTS_DIR:                    DirectoryPath = _ROOT_DIR / "api" / "llm" / "prompts"
    HUGGING_FACE_REPO_ID:           str = "the-ride-never-ends/american_municipal_law"
    OPENAI_MODEL:                   str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL:         str = "text-embedding-3-small"
    LOG_LEVEL:                      int = 10
    SIMILARITY_SCORE_THRESHOLD:     float = 0.3
    SEARCH_EMBEDDING_BATCH_SIZE:    int = 10000

    @computed_field # type: ignore[prop-decorator]
    @property
    def USE_GPU_FOR_COSINE_SIMILARITY(self) -> str:
        """
        Determines if GPU is available for cosine similarity calculations.

        Returns:
            bool: True if GPU is available, False otherwise.
        """
        return _USE_GPU_FOR_COSINE_SIMILARITY()

# Load the configs from the yaml and create an instance of the Configs class
with open(_ROOT_DIR / 'app' / "configs.yaml", "r") as config_file:
    config_dict = yaml.safe_load(config_file)

try:
    configs = Configs.model_validate(config_dict)
except ValidationError as e:
    raise ValidationError(
        f"Validation error in configs: {e.errors()}"
    ) from e
