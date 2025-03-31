from pathlib import Path


from pydantic import BaseModel, SecretStr, DirectoryPath
import yaml


_ROOT_DIR = Path(__file__).parent.parent


class Configs(BaseModel):
    """
    Configuration class for the American Law dataset upload to Hugging Face.

    This class defines all the necessary configurations for the project,
    including API keys, file paths, model specifications, and other settings.

    Attributes:
        HUGGING_FACE_USER_ACCESS_TOKEN (SecretStr): Authentication token for Hugging Face API.
        OPENAI_API_KEY (SecretStr): Authentication key for OpenAI API.
        ROOT_DIR (DirectoryPath): Root directory of the project.
        AMERICAN_LAW_DIR (DirectoryPath): Directory containing the American Law project.
        AMERICAN_LAW_DATA_DIR (DirectoryPath): Directory containing the American Law data.
        HUGGING_FACE_REPO_ID (str): Repository ID on Hugging Face for uploading.
        OPENAI_MODEL (str): OpenAI model to use for processing.
        OPENAI_EMBEDDING_MODEL (str): OpenAI model to use for text embeddings.
        LOG_LEVEL (int): Logging level for the application (10 = DEBUG).
    """
    HUGGING_FACE_USER_ACCESS_TOKEN: SecretStr
    OPENAI_API_KEY: SecretStr
    ROOT_DIR: DirectoryPath = _ROOT_DIR
    AMERICAN_LAW_DIR: DirectoryPath = _ROOT_DIR / "american_law"
    AMERICAN_LAW_DATA_DIR: DirectoryPath = _ROOT_DIR / "american_law" / "data"
    HUGGING_FACE_REPO_ID: str = "the-ride-never-ends/american_law"
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    LOG_LEVEL: int = 10


# Load the configs from the yaml and create an instance of the Configs class
with open(_ROOT_DIR / "american_law" / "configs.yaml", "r") as config_file:
    config_dict = yaml.safe_load(config_file)

configs = Configs(**config_dict)