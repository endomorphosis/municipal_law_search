from typing import Literal


from pydantic import BaseModel
import yaml


from configs import configs
from logger import logger
from utils.common import safe_format


class PromptFields(BaseModel):
    """
    A Pydantic model for a prompt field structure for LLM interactions.
    Attributes:
        role (Literal['system', 'user']): The role of the message sender, 
            either 'system' for system instructions or 'user' for user messages.
        content (str): The actual content of the prompt message.
    """
    role: Literal['system', 'user']
    content: str


class LLMSettings(BaseModel):
    """
    A Pydantic model for LLM settings.

    Attributes:
        temperature (float): The temperature setting for the LLM.
        max_tokens (int): The maximum number of tokens for the LLM response.
        top_p (float): The top-p setting for the LLM.
        frequency_penalty (float): The frequency penalty setting for the LLM.
        presence_penalty (float): The presence penalty setting for the LLM.
    """
    temperature: float = 0.0
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


class Prompt(BaseModel):
    """
    A pydantic class for a prompt for LLM interactions.

    Attributes:
        client (Literal['openai']): The LLM client type to use. Currently only OpenAI is supported.
        system_prompt (PromptFields): The system prompt fields.
        user_prompt (PromptFields): The user prompt fields.

    Methods:
        safe_format(**kwargs): Safely formats the system and user prompts with
            the provided keyword arguments. Only keys that exist in the
            respective prompt templates will be used for formatting.

    Example:
        ```python
        prompt = Prompt(
            client="openai",
            system_prompt=PromptFields(content="You are {role}."),
            user_prompt=PromptFields(content="Please {action} about {topic}.")
        )
        prompt.safe_format(role="an expert", action="explain", topic="AI")
        ```
    """
    client: Literal['openai']
    system_prompt: PromptFields
    user_prompt: PromptFields
    settings: LLMSettings = None

    def safe_format(self, **kwargs) -> None:
        if kwargs:
            # Filter the keyword arguments based on the prompt content
            sys_kwargs = {k: v for k, v in kwargs.items() if k in self.system_prompt.content}
            user_kwargs = {k: v for k, v in kwargs.items() if k in self.user_prompt.content}

            self.system_prompt.content = safe_format(self.system_prompt.content, **sys_kwargs).strip()
            self.user_prompt.content = safe_format(self.user_prompt.content, **user_kwargs).strip()

    @property
    def messages(self) -> dict:
        """
        Converts the prompt to OpenAI API format.
        
        Returns:
            dict: A dictionary formatted for OpenAI API.
        """
        return {
            "messages": [
                {"role": self.system_prompt.role,
                 "content": self.system_prompt.content},
                {"role": self.user_prompt.role,
                 "content": self.user_prompt.content}
            ]
        }


def load_prompt_from_yaml(prompt_name: str, override: dict = None, **kwargs) -> Prompt:
    """
    Load a prompt from a YAML file and format it with provided values.

    This function reads a prompt template from a YAML file located in the configured
    prompts directory, validates it against the Prompt model, and formats it using
    the provided keyword arguments.

    Args:
        prompt_name (str): Name of the prompt file without the .yaml extension
        **kwargs: Variable keyword arguments used to format the prompt template

    Returns:
        Prompt: A validated and formatted Prompt object ready for use

    Raises:
        FileNotFoundError: If the specified prompt file doesn't exist
        ValidationError: If the YAML content doesn't match the Prompt model structure
        
    Example:
        >>> system_prompt = load_prompt_from_yaml("system_prompt", model_name="gpt-4")
    """
    prompt_path = configs.PROMPTS_DIR / f"{prompt_name}.yaml"

    with open(prompt_path, 'r') as file:
        prompt = dict(yaml.safe_load(file))
        formatted_prompt = Prompt.model_validate(prompt).safe_format(**kwargs)

    if override:
        for key, value in override.items():
            if hasattr(formatted_prompt, key):
                setattr(formatted_prompt, key, value)

    return formatted_prompt

