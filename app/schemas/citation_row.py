from typing import Optional


from pydantic import BaseModel


class CitationRow(BaseModel):
    """
    A Pydantic model representing a row in the 'citations' table in citations.db and american_law.db.
    """
    cid: str = None
    bluebook_cid: str = None
    title: str = None
    public_law_num: Optional[str] = None
    chapter: Optional[str] = None
    ordinance: Optional[str] = None
    section: Optional[str] = None
    enacted: Optional[str] = None
    year: Optional[str] = None
    history_note: Optional[str] = None
    place_name: str
    state_code: str
    bluebook_state_code: str
    state_name: str
    chapter_num: Optional[str] = None
    title_num: Optional[str] = None
    date: Optional[str] = None
    bluebook_citation: str = None
    gnis: str | int  = None 