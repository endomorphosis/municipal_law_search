"""
Law item schema for the American Law Search API.

This module defines the data structure for law items returned by the
API's search and retrieval endpoints. It represents a single legal document
from the municipal and county law corpus.
"""
from pydantic import BaseModel


class LawItem(BaseModel):
    """
    Represents a single legal document item from municipal or county law.
    
    This model encapsulates all the information about a legal document, including
    its metadata (citation information, jurisdiction, date) and the actual content
    in HTML format. It's used as the primary response type for law search and 
    retrieval endpoints.
    
    Attributes:
        cid: String content identifier that uniquely identifies this legal document.
        title: The title of the legal document.
        chapter: The chapter designation within the legal code.
        place_name: The municipality or county name where this law is in effect.
        state_name: The state in which the place_name is located.
        date: The date of the law's enactment or last revision.
        bluebook_citation: Formal citation in Bluebook format for legal references.
        html: The full HTML content of the legal document.
    
    Example:
        ```python
        law = LawItem(
            cid="bafkreicglt4bhrs4wfmeyln2bflfekecfgdcyzuty3ke7t2qokndmb766y",
            title="Zoning Code",
            chapter="Chapter 4",
            place_name="Springfield",
            state_name="Illinois", 
            date="2021-05-15",
            bluebook_citation="Springfield Zoning Code ch. 4 (2021)",
            html="<div>Full content here...</div>"
        )
        ```
    """
    cid: str
    title: str
    chapter: str
    place_name: str
    state_name: str
    date: str
    bluebook_citation: str
    html: str