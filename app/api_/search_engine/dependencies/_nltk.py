import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt', quiet=True)

def tokenize_text_into_words(text: str, language: str = "english") -> list[str]:
    """
    Tokenizes the input text into words using NLTK's word_tokenize function.

    Args:
        text (str): The input text to be tokenized.
        language (str): The language of the text. Default is "english".

    Returns:
        list[str]: A list of words extracted from the input text.
    """
    return word_tokenize(text,language=language)