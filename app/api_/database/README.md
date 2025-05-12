---
license: mit
language:
- en
tags:
- legal
pretty_name: American Law
---

## Description
Municipal and County Laws from across the United States, in parquet format.
Files are named after a location's [GNIS id](https://en.wikipedia.org/wiki/Geographic_Names_Information_System) and what they contain.
Unless specified otherwise, each row is one sub-section of a law. 
It is the one of the smallest units of law that can be cited under the [Bluebook Citation method](https://owl.purdue.edu/owl/research_and_citation/chicago_manual_17th_edition/cmos_formatting_and_style_guide/bluebook_citation_for_legal_materials.html).
For convenience's sake, these will be referred to as "law" for the rest of this document. All types are from Python.
Unless specified otherwise, each embedding was created using OpenAI's "text-embedding-3-small" model.

## Parquet Contents
### HTML
Files that end in '_html' consist of rows with the following attributes:
- cid (str): A unique CID for the law. It is created from the string "{gnis}_{doc_title}.json". Ex: "bafkreifzhmfladwvggsjdrc32npt6exucvrl3xe2omkgyfkqpo35ufaope"
- doc_id (str): A unique ID based on the law's plaintext title. Ex: "CO_CH27HOSPVI"
- doc_order (int): The relative location of a law in a corpus, in ascending order.
- html_title (str): The raw HTML of the law's title. Ex: ""<div class=\"chunk-title\">Chapter 46 - MASTER ROAD PLAN AND SPECIFICATIONS<a href=..."
- html (str): The raw HTML of the law itself. This can include footnotes, citations, tables, etc.
- __index_level_0__ (int): Artifact of the parquet conversion process. Will likely be removed in future updates.

### Citation
Files that end in '_citation' consist of rows with the following attributes:
- bluebook_cid (str): A unique CID for the given citation. It is created from the string f"{place_name}{bluebook_state_code}{title}{history_note}". A law may have multiple citations linked to it, as parts of a law can be modified without changing other parts.
- cid (str): The CID for the citation's associated law. This functions as a foreign key.
- title (str): A plaintext version of the law's title. Ex: "Sec. 44. - Civic center and municipal building"
- title_num (str): The number in the law's title. As title numbers can also use letters (e.g. A,B,C,etc.), specially-formatted numbers (e.g. 17-35), or none at all, title_num should be treated as a string for search and processing purposes. 
- date (str): The date when an ordinance was passed/changed. Ex: "10-22-85".
- public_law_num (str): An "NA" place holder for Public Law number, A Public Law number, like "P.L. 107-101," identifies a law passed by the US Congress, indicating the US Congress number (107) and the law's sequential number within that Congress (101). As municipal and county citations are not federal laws, they do not have such a number. However, this is left in as this dataset might include federal law in the future.
- chapter (str): The plaintext title of a chapter in the law corpus that contains the law. Chapters are broadly defined to be any macro-grouping in a corpus, and include appendices, tables, and other errata. Ex: "Chapter 16 - PARKS AND OTHER RECREATIONAL AND PUBLIC FACILITIES".
- chapter_num (str): The number of the chapter. As chapter numbers can also use letters (e.g. A,B,C,etc.), specially-formatted numbers (e.g. 17-35), or none at all, chapter_num should be treated as a string for search and processing purposes. 
- history_note (str): The plaintext version of a single footnote for a law. They document the law's history. Ex: "Ord. No. 1985-19, § 1, 10-22-85"
- ordinance (str): Which ordinance the law was passed/changed under. Ex: "Ord. No. 1985-19".  Will be updated when history note parsing is more robust.
- section (str): Which section in the law was passed/changed under. Ex: "§ 1". Will be updated when history note parsing is more robust.
- enacted (str). The date when a specific law came into effect. Ex: "1985". Will be updated when history note parsing is more robust.
- year (str): The year when an ordinance was passed/changed. Ex: "1985". Will be updated when history note parsing is more robust.
- place_name (str): The place where the law is in effect. Currently only has municipalities and counties Ex: "City of Baker".
- state_name (str): The state where a given place is located. Ex: "Louisiana"
- state_code (str): The two letter abbreviation of a state's name. Ex: "LA"
- bluebook_sate_code (str): An abbreviation of state_name used specifically for Bluebook citation's. Ex: "Mass."
- bluebook_citation (str): A bluebook citation for a given law. Ex: "City of Baker, La., Municipal Code, §17-102 (1972)".
- __index_level_0__ (int): Artifact of the parquet conversion process. Will likely be removed in future updates.

### Embeddings
Files that end in '_embeddings' consist of rows with the following attributes:
- embedding_cid (str): A unique CID for the embedding. It is created from turning each float into a string, concatentating them, then making a CID out of it.
- gnis (str): A place's GNIS id. This functions as a foreign key and allows for cosine similarity searches to be narrowed to a specific location.
- cid (str): The CID for the embeddings's associated law. This functions as a foreign key.
- text_chunk_order (int): The relative location of an embedding for a law. As chunks may sometimes have token counts greater than the embedding model's input limits, laws are split into separate parts if they go over this limit.
- embedding (list(float)): An embedding of the plaintext version of the law, with newlines removed and spaces normalized.
- __index_level_0__ (int): Artifact of the parquet conversion process. Will likely be removed in future updates.
