import re


def page_has_more_javascript_than_html(file_content: str) -> bool:
    """
    Check if the page contains more JavaScript-like content than HTML.

    This function analyzes the content of the file and performs two checks:
        1. Counts the number of camelCase words (typical in JavaScript).
        2. Counts the number of HTML div tags.

    If there are more camelCase words than div tags, it considers the page
    to be more JavaScript-like than HTML.

    Args:
        file_content (str): Content of the HTML file.

    Returns:
        bool: True if the page seems to contain more JavaScript, False otherwise.
    """
    # Count camelCase words
    camel_case_pattern = r'\b[a-z]+[A-Z][a-zA-Z]*\b'
    camel_case_count = len(re.findall(camel_case_pattern, file_content))

    # Count <div> tags
    div_count = file_content.lower().count('<div>')

    # Compare counts
    return camel_case_count > div_count
