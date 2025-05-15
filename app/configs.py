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
_APP_DIR = Path(__file__).parent

# Insert this file's directory to the system path
sys.path.insert(0, str(_ROOT_DIR))
try:
    sys.path.insert(0, str(_APP_DIR))
except ImportError:
    # If the import fails, it means the directory is not a package
    pass

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
        HUGGING_FACE_USER_ACCESS_TOKEN (SecretStr): Authentication token for Hugging Face.
        ROOT_DIR (DirectoryPath): Root directory of the project.
        APP_DIR (DirectoryPath): Application directory of the project.
        AMERICAN_LAW_DATA_DIR (DirectoryPath): Directory containing the American Law data.
        PARQUET_FILES_DIR (DirectoryPath): Directory containing parquet files.
        AMERICAN_LAW_DB_PATH (DirectoryPath): Path to the American Law database file.
        SEARCH_HISTORY_DB_PATH (DirectoryPath): Path to the search history database file.
        PROMPTS_DIR (DirectoryPath): Directory containing LLM prompt templates.
        HUGGING_FACE_REPO_ID (str): Repository ID on Hugging Face for uploading.
        OPENAI_MODEL (str): OpenAI model to use for processing.
        OPENAI_EMBEDDING_MODEL (str): OpenAI model to use for text embeddings.
        LOG_LEVEL (int): Logging level for the application (10 = DEBUG).
        SIMILARITY_SCORE_THRESHOLD (float): Threshold for cosine similarity scoring.
        SEARCH_EMBEDDING_BATCH_SIZE (int): Batch size for embedding searches.
        DATABASE_CONNECTION_POOL_SIZE (int): Maximum number of database connections in the pool.
        DATABASE_CONNECTION_TIMEOUT (int): Timeout in seconds for database connections.
        DATABASE_CONNECTION_MAX_OVERFLOW (int): Maximum number of connections that can be created beyond the pool size.
        DATABASE_CONNECTION_MAX_AGE (int): Maximum age in seconds for a database connection.
        TOP_K (int): Number of top results to return in searches.
        USE_GPU_FOR_COSINE_SIMILARITY (str): Whether to use GPU for cosine similarity calculations.
    """
    OPENAI_API_KEY:                   SecretStr = os.environ.get("OPENAI_API_KEY")
    HUGGING_FACE_USER_ACCESS_TOKEN:   SecretStr = None
    ROOT_DIR:                         DirectoryPath = _ROOT_DIR
    APP_DIR:                          DirectoryPath = _APP_DIR
    AMERICAN_LAW_DATA_DIR:            DirectoryPath = _ROOT_DIR / "data"
    PARQUET_FILES_DIR:                DirectoryPath = _ROOT_DIR / "data" / "parquet_files"
    AMERICAN_LAW_DB_PATH:             DirectoryPath = _ROOT_DIR / "data" / "american_law.db"
    SEARCH_HISTORY_DB_PATH:           DirectoryPath = _ROOT_DIR / "data" / "search_history.db"
    PROMPTS_DIR:                      DirectoryPath = _ROOT_DIR / "api" / "llm" / "prompts"
    HUGGING_FACE_REPO_ID:             str = "the-ride-never-ends/american_municipal_law"
    OPENAI_MODEL:                     str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL:           str = "text-embedding-3-small"
    LOG_LEVEL:                        int = 10
    SIMILARITY_SCORE_THRESHOLD:       float = 0.3
    SEARCH_EMBEDDING_BATCH_SIZE:      int = 10000
    DATABASE_CONNECTION_POOL_SIZE:    int = 10
    DATABASE_CONNECTION_TIMEOUT:      int = 30
    DATABASE_CONNECTION_MAX_OVERFLOW: int = 20
    DATABASE_CONNECTION_MAX_AGE:      int = 300
    TOP_K :                           int = 100

    @computed_field # type: ignore[prop-decorator]
    @property
    def USE_GPU_FOR_COSINE_SIMILARITY(self) -> str:
        """
        Determines if GPU is available for cosine similarity calculations.

        Returns:
            bool: True if GPU is available, False otherwise.
        """
        return _USE_GPU_FOR_COSINE_SIMILARITY()

    def __getitem__(self, key: str) -> str:
        """
        Allows dictionary-like access to the configuration attributes.

        Args:
            key (str): The name of the configuration attribute.

        Returns:
            str: The value of the requested configuration attribute.
        """
        try:
            return getattr(self, key)
        except AttributeError as e:
            raise KeyError(f"Configuration key '{key}' not found.") from e

    def __setitem__(self, key: str, value: str) -> None:
        """
        Allows dictionary-like setting of the configuration attributes.

        Args:
            key (str): The name of the configuration attribute.
            value (str): The value to set for the configuration attribute.

        Raises:
            AttributeError: If the attribute does not exist.
        """
        try:
            setattr(self, key, value)
            # Re-validate the new value
            self.model_validate()
        except ValidationError as e:
            raise ValidationError(f"Validation error setting '{key}' to '{value}': {e.errors()}")
        except AttributeError as e:
            raise KeyError(f"Configuration key '{key}' not found.") from e

    def get(self, key: str, default: str = None) -> str:
        """
        Retrieves the value of a configuration attribute.

        Args:
            key (str): The name of the configuration attribute.
            default (str): The default value to return if the key is not found.

        Returns:
            str: The value of the requested configuration attribute or the default value.
        """
        try:
            return getattr(self, key)
        except AttributeError:
            return default

# Load the configs from the yaml and create an instance of the Configs class
with open(_ROOT_DIR / 'app' / "configs.yaml", "r") as config_file:
    config_dict = yaml.safe_load(config_file)

try:
    configs = CONFIGS = Configs.model_validate(config_dict)
except ValidationError as e:
    raise ValidationError(
        f"Validation error in configs: {e.errors()}"
    ) from e
