#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
import csv
import json
from pathlib import Path
import re
import time
import traceback
from typing import Any


from bs4 import BeautifulSoup
import duckdb
import pandas as pd
from tqdm import tqdm


from configs import configs
from logger import logger
from utils.get_cid import get_cid


MISSING_DATE_CSV = configs.AMERICAN_LAW_DATA_DIR / 'missing_data.csv'
AMERICAN_LAW_DB_PATH = configs.AMERICAN_LAW_DATA_DIR / 'american_law.db'


def clean_html(html_content):
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


def preview_clean_html(html_content):
    """Preview cleaned HTML content for better display"""
    # Clean up HTML for display (show just a preview)
    clean_html = re.sub(r'<[^>]+>', ' ', html_content)
    clean_html = re.sub(r'\s+', ' ', clean_html).strip()
    preview = clean_html[:500] + "..." if len(clean_html) > 500 else clean_html
    return preview


def log_missing_data(gnis: int, missing_data: Any, csv_path: Path = MISSING_DATE_CSV):
    """Log missing parquet files for a given GNIS to a CSV file."""
    existing_data = {}

    # Read existing data if file exists
    if not csv_path.exists():
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['gnis', 'missing_data_types'])
        logger.info(f"Created new CSV file at {csv_path}")
    else:
        with open(csv_path, 'r', newline='') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            for row in reader:
                existing_data[row[0]] = row[1]

    # Update or add the GNIS entry
    existing_data[gnis] = ','.join(missing_data)

    # Write data back to CSV
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['gnis', 'missing_data_types'])
        for key, value in existing_data.items():
            writer.writerow([key, value])

from utils.run_in_process_pool import run_in_process_pool

def _fix_embeddings_parquet(file: Path) -> bool:
    try:
        df = pd.read_parquet(file.resolve())
        # Make a unique CID out of the embedding and the foreign CID.
        df['embedding_cid'] = df.apply(
            lambda row: get_cid(
                f"{json.dumps(row['embedding'].tolist())}{row['cid']}"
            ),
            axis=1
        )
        df.to_parquet(file.resolve(), index=False)
        logger.info(f"Fixed embeddings in {file}")
        return True
    except Exception as e:
        logger.error(f"Error fixing embeddings in {file}: {e}")
        return False

def _fix_citation_parquet(file: Path) -> bool:
    """Get rid of any duplicate entries in the citation parquet files."""
    try:
        df = pd.read_parquet(file.resolve())
        # Get the length of the dataframe
        original_length = len(df)
        # Drop duplicates based on 'bluebook_cid' and keep the first occurrence
        df = df.drop_duplicates(subset=['bluebook_cid'], keep='first')
        final_length = len(df)
        df.to_parquet(file.resolve(), index=False)
        logger.info(f"Dropped {original_length - final_length} duplicate rows from citations for {file}")
        return True
    except Exception as e:
        logger.error(f"Error fixing duplicate citations in {file}: {e}")
        return False


def fix_parquet_file_in_parallel(parquet_type: str = "_citation.parquet"):
    parquet_type = "_citation.parquet"
    cid_type = parquet_type.split(".")[0].strip("_")  # Get the type of parquet file, e.g., citations
    logger.info(f"Fixing {cid_type} CIDs in all {cid_type} parquet files...")

    files = list(configs.AMERICAN_LAW_DATA_DIR.glob(f"**/*{parquet_type}"))
    for input, output in run_in_process_pool(_fix_citation_parquet, files):
        if output:
            logger.info(f"Processed {input} successfully.")
        else:
            logger.error(f"Failed to process {input}.")
    logger.info(f"Finished fixing all {cid_type} parquet files.")


def create_american_law_db(base_path: Path):
    """Process the dataset and store in DuckDB database"""

    if not AMERICAN_LAW_DB_PATH.exists():
        logger.info(f"Creating new DuckDB database at {AMERICAN_LAW_DB_PATH}")
        duckdb.connect(AMERICAN_LAW_DB_PATH).close()
        logger.info("Database created successfully.")
    else:
        logger.debug(f"DuckDB database exists at {AMERICAN_LAW_DB_PATH}.")

    conn = duckdb.connect(AMERICAN_LAW_DB_PATH)
    cursor = conn.cursor()
    table_creation_dict = {
        "html_table":'''
            CREATE TABLE html (
                cid TEXT PRIMARY KEY,
                doc_id VARCHAR NOT NULL,
                doc_order INTEGER NOT NULL,
                html_title TEXT NOT NULL,
                html TEXT NOT NULL,
                index_level_0 INTEGER
            )
        ''',
        "embeddings_table": '''
            CREATE TABLE embeddings (
                embedding_cid TEXT PRIMARY KEY,
                gnis TEXT NOT NULL,
                cid TEXT NOT NULL,
                text_chunk_order INTEGER NOT NULL,
                embedding DOUBLE[1536] NOT NULL,
            )
        ''',
        "citations_table": '''
            CREATE TABLE citations (
                bluebook_cid TEXT PRIMARY KEY,
                cid TEXT NOT NULL,
                title TEXT NOT NULL,
                title_num TEXT,
                date TEXT,
                public_law_num TEXT,
                chapter TEXT,
                chapter_num TEXT,
                history_note TEXT,
                ordinance TEXT,
                section TEXT,
                enacted TEXT,
                year TEXT,
                place_name TEXT NOT NULL,
                state_name TEXT NOT NULL,
                state_code TEXT NOT NULL,
                bluebook_state_code TEXT NOT NULL,
                bluebook_citation TEXT NOT NULL,
            )'''
    }
    for key, value in table_creation_dict.items():
        try:
            cursor.execute(value)
            logger.info(f"Table {key} created successfully.")
            schema = cursor.execute(f"DESCRIBE {key.split('_')[0]}").fetchall()
            #logger.debug(f"Schema for {key}: {schema}")
        except duckdb.CatalogException as e:
            logger.warning(f"Table {key} already exists. Skipping creation. Error: {e}")

    # Find all citation files
    citation_files = list(base_path.glob("**/*_citation.parquet"))
    logger.info(f"Found {len(citation_files)} citation files in {base_path}")

    errored = None
    for citation_path in tqdm(citation_files, desc="Processing files"):
        skip = False
        gnis = citation_path.stem.split('_')[0]  # Extract GNIS from filename

        try:
            # Read citation data to see if it loads.
            citation_df = pd.read_parquet(citation_path.resolve())
            logger.debug(f"citation_df for gnis '{gnis}':\n{citation_df.head()}")  # Trigger loading to check for errors
        except Exception as e:
            logger.error(f"Error reading {citation_path}: {e}")
            traceback.print_exc()
            errored = e
            break

        try:
            # Get corresponding HTML file
            html_path = base_path / gnis / f"{gnis}_html.parquet"
            embedding_path = base_path / gnis / f"{gnis}_embeddings.parquet"

            missing_data = []
            # Check for missing parquet files
            if not html_path.exists():
                missing_data.append("html")
                skip = True

            if not embedding_path.exists():
                missing_data.append("embedding")
                skip = True

            if skip:
                #print(f"Warning: Empty data in {', '.join(missing_data)} file(s) for gnis {gnis}. Skipping.")
                # Log the issue to a CSV file for tracking.
                log_missing_data(gnis, ','.join(missing_data))
                continue

            parquet_list = [("html", html_path,), ("citations",citation_path,), ("embeddings", embedding_path,)]
            for file in parquet_list:
                try:
                    match file[0]:
                        case "html" | "citations":
                            conn.execute(f'''
                                INSERT INTO {file[0]}
                                    SELECT * FROM read_parquet('{file[1].resolve()}');
                            ''')
                        case _: # Apparently embeddings don't have the __index_level_0__ index. What the hell!?!?!
                            conn.execute(f'''
                                INSERT INTO {file[0]}
                                    SELECT embedding_cid, gnis, cid, text_chunk_order, embedding FROM read_parquet('{file[1].resolve()}');
                            ''')
                except Exception as e:
                    errored = f"Error from {file[1]}: {e}"
                    if "Constraint Error" in str(e) and "embeddings" in file[1].name:
                        logger.error(f"Duplicate entry found in embeddings for {file[1]}. Skipping insertion.")
                        time.sleep(30)
                        # If this occurred, it means we have a duplicate entry in the embeddings table.

                    # # If we can't do it direct, do it manually.
                    # logger.error(f"Error inserting data into {file[0]} from {file[1]}: {e}")
                    # df = pd.read_parquet(file[1].resolve())
                    # for _, row in df.iterrows():
                    #     values = [value for value in row.values()]
                    #     keys = list(row.keys())
                    #     try:
                    #         if file[0] == "html":
                    #             conn.execute('''
                    #                 INSERT INTO html 
                    #                 (cid, doc_id, doc_order, html_title, html, index_level_0)
                    #                 VALUES (?, ?, ?, ?, ?, ?)
                    #             ''', [
                    #                 row['cid'],
                    #                 row['doc_id'],
                    #                 int(row['doc_order']),
                    #                 row['html_title'],
                    #                 row['html'],
                    #                 row.get('index_level_0', None)
                    #             ])
                    #         elif file[0] == "citations":
                    #             conn.execute('''
                    #                 INSERTINTO citations 
                    #                 (bluebook_cid, cid, title, title_num, date, public_law_num, 
                    #                  chapter, chapter_num, history_note, ordinance, section, 
                    #                  enacted, year, place_name, state_name, state_code,
                    #                  bluebook_state_code, bluebook_citation, index_level_0)
                    #                 VALUES (?,

            # conn.execute(f'''
            #     INSERT OR REPLACE INTO citations
            #         SELECT * FROM read_parquet('{citation_path.resolve()}');
            # ''')

            # conn.execute(f'''
            #     INSERT OR REPLACE INTO embeddings
            #         SELECT * FROM read_parquet('{embedding_path.resolve()}');
            # ''')

            # # Process each citation
            # for _, citation_row in citation_df.iterrows():
            #     cid = citation_row['cid']
                
            #     # Find matching HTML content
            #     matching_html = html_df[html_df['cid'] == cid]
                
            #     if not matching_html.empty:
            #         # Clean HTML content
            #         html_content = matching_html.iloc[0]['html']
            #         html_title = matching_html.iloc[0]['html_title'] if 'html_title' in matching_html.columns else ''
            #         doc_id = matching_html.iloc[0]['doc_id'] if 'doc_id' in matching_html.columns else ''
            #         doc_order = matching_html.iloc[0]['doc_order'] if 'doc_order' in matching_html.columns else 0
            #         index_level_0 = matching_html.iloc[0]['index_level_0'] if 'index_level_0' in matching_html.columns else None

            #         # Coerce doc_order to int if it's not an integer
            #         if not isinstance(doc_order, int):
            #             doc_order = int(doc_order) if pd.notna(doc_order) else 0

            #         # Insert into html table
            #         conn.execute('''
            #         INSERT OR REPLACE INTO html 
            #         (cid, doc_id, doc_order, html_title, html, index_level_0)
            #         VALUES (?, ?, ?, ?, ?, ?)
            #         ''', [
            #             cid,
            #             doc_id,
            #             doc_order,
            #             html_title,
            #             html_content,
            #             index_level_0
            #         ])
                    
            #         # Insert into citations table
            #         conn.execute('''
            #         INSERT OR REPLACE INTO citations 
            #         (bluebook_cid, cid, title, title_num, date, public_law_num, 
            #          chapter, chapter_num, history_note, ordinance, section, 
            #          enacted, year, place_name, state_name, state_code,
            #          bluebook_state_code, bluebook_citation, index_level_0)
            #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            #         ''', [
            #             citation_row.get('bluebook_cid', ''),
            #             cid,
            #             citation_row.get('title', ''),
            #             citation_row.get('title_num', ''),
            #             citation_row.get('date', ''),
            #             citation_row.get('public_law_num', ''),
            #             citation_row.get('chapter', ''),
            #             citation_row.get('chapter_num', ''),
            #             citation_row.get('history_note', ''),
            #             citation_row.get('ordinance', ''),
            #             citation_row.get('section', ''),
            #             citation_row.get('enacted', ''),
            #             citation_row.get('year', ''),
            #             citation_row.get('place_name', ''),
            #             citation_row.get('state_name', ''),
            #             citation_row.get('state_code', ''),
            #             citation_row.get('bluebook_state_code', ''),
            #             citation_row.get('bluebook_citation', ''),
            #             citation_row.get('index_level_0', None)
            #         ])
                    
            #         # Process embeddings - store file paths for this cid
            #         matching_embeddings = embedding_df[embedding_df['cid'] == cid]
            #         if not matching_embeddings.empty:
            #             for _, embedding_row in matching_embeddings.iterrows():
            #                 conn.execute('''
            #                 INSERT OR REPLACE INTO embeddings 
            #                 (embedding_cid, gnis, cid, text_chunk_order, embedding_filepath, index_level_0)
            #                 VALUES (?, ?, ?, ?, ?, ?)
            #                 ''', [
            #                     embedding_row.get('embedding_cid', ''),
            #                     gnis,
            #                     cid,
            #                     embedding_row.get('text_chunk_order', 0),
            #                     str(embedding_path.resolve()),  # Store the filepath to the embedding parquet file
            #                     embedding_row.get('index_level_0', None)
            #                 ])
            
        except Exception as e:
            logger.error(f"Error processing {citation_path}: {e}")
            traceback.print_exc()
            errored = e
            break

        if errored:
            raise Exception(errored)

    # Create indexes for faster searching
    # conn.execute('CREATE INDEX IF NOT EXISTS s_idx ON html(cid)')
    # conn.execute('CREATE INDEX IF NOT EXISTS s_idx ON citations(cid)')
    # conn.execute('CREATE INDEX IF NOT EXISTS s_idx ON embeddings(cid)')
    conn.close()

if __name__ == "__main__":
    # fix_parquet_file_in_parallel()
    # time.sleep(60)
    base_path = configs.PARQUET_FILES_DIR
    create_american_law_db(base_path)