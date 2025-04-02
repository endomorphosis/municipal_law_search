
import re

from bs4 import BeautifulSoup


def clean_html(html_content: str) -> str:
    """Clean HTML content for better display"""
    soup = BeautifulSoup(html_content, 'html.parser')
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    # Get text and clean it
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    return text


def preview_clean_html(html_content: str) -> str:
    """Preview cleaned HTML content for better display"""
    # Clean up HTML for display (show just a preview)
    clean_html = re.sub(r'<[^>]+>', ' ', html_content)
    clean_html = re.sub(r'\s+', ' ', clean_html).strip()
    preview = clean_html[:500] + "..." if len(clean_html) > 500 else clean_html
    return preview