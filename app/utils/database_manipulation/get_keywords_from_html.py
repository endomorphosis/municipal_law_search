
COMMON_ENGLISH_WORDS: dict[set] = {
    # "adjective": set("all", "just", "good", "first", "even", "new"), # Keep all adjectives
    # "adverb": set("when", "then", "only", "also", "how", "well", "most", "not"), # Keep all adverbs
    "article": set("the", "a", "an"), # Remove
    "coordinator": set("and", "or"),
    "determiner": set("no", "this"),
    #"noun": set("time", "people", "year", "two", "day", "way"), # Keep all nouns
    "possessive_pronoun": set("his", "my", "their", "your", "its", "our", "her"),
    "preposition": set("to", "of", "in", "for", "on", "with", "at", "by", "from", "out", "if", "into", "than", "now", "after", "because"),
    "pronoun": set("I", "it", "he", "you", "they", "we", "she", "which", "me", "him", "them", "any", "these", "us"),
    #"subordinator": set(),
    # "verb": set("be", "have", "would", "get", "could", "see", "look", "come", "think", "want", "give"), # Keep all verbs
    # "multiple": set(
    #     "some", 
    #     "other",  # Adjective, pronoun
    #     "as",     # Adverb, preposition
    #     "up",     # Adverb, preposition, et al.
    #     "there",  # Adverb, pronoun, et al.
    #     "so",     # Coordinator, adverb, et al.
    #     "no",     # Determiner, adverb
    #     "one",    # Noun, adjective, et al.
    #     "back",   # Noun, adverb
    #     "but",    # Preposition, adverb, coordinator
    #     "about",  # Preposition, adverb, et al.
    #     "like",   # Preposition, verb
    #     "what",   # Pronoun, adverb, et al.
    #     "who",    # Pronoun, noun
    #     "that",   # Subordinator, determiner
    #     "say",    # Verb et al.
    #     "do",     # Verb, noun
    #     "will",   # Verb, noun
    #     "go",     # Verb, noun
    #     "make",   # Verb, noun
    #     "can",    # Verb, noun
    #     "know",   # Verb, noun
    #     "take",   # Verb, noun
    #     "use",    # Verb, noun
    #     "work"    # Verb, noun
    # ),
}


def get_keywords_from_html(html: str, language: str = "english") -> str:
    """
    TODO:
    Extracts keywords from the given HTML content.

    Args:
        html (str): The HTML content to extract keywords from.
        language (str): The language of the text. Default is "english".

    Returns:
        str: The extracted keywords.
    """
    from bs4 import BeautifulSoup
    from nltk.tokenize import word_tokenize, sent_tokenize

    separator = ","
    raw_text = BeautifulSoup(html, "html.parser").get_text(separator=separator, strip=True)
    unique_word_set = set(
        word for word in word_tokenize(raw_text, language=language) if word.isalnum()
    )
    for common_words in COMMON_ENGLISH_WORDS.values():
        unique_word_set -= common_words
