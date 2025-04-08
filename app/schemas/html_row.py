from pydantic import BaseModel


class HtmlRow(BaseModel):
    """
    A Pydantic model representing a row in the 'html' table in html.db and american_law.db.
    """
    cid: str = None
    doc_id: str = None
    doc_order: int = None
    html_title: str = None 
    html: str = None
    gnis: str | int  = None 