
import functools
import json
from pathlib import Path
from typing import Callable, Optional


import pandas as pd


from app.configs import configs
from app.logger import logger
from app.utils.common.run_in_process_pool import run_in_process_pool
from app.utils.common import get_cid


def _get_rid_of_index_level_0_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Get rid of __index_level_0__ column
    if "__index_level_0__" in df.columns:
        df.drop(columns=["__index_level_0__"], inplace=True)
    logger.info("Removed __index_level_0__ column from the dataframe.")
    return df

def _fix_parquet(file: Path, funcs: list[Callable]) -> Optional[Exception]:
    try:
        df = pd.read_parquet(file.resolve())
        for func in funcs:
            df = func(df)
        df.to_parquet(file.resolve(), index=False)
        return None
    except Exception as e:
        logger.error(f"Error fixing {file}: {e}")
        return e

def _make_unique_cid_out_of_embedding_and_foreign_cid(df: pd.DataFrame) -> pd.DataFrame:
    df['embedding_cid'] = df.apply(
        lambda row: get_cid(f"{json.dumps(row['embedding'].tolist())}{row['cid']}"),
        axis=1
    )
    logger.info("Generated unique embedding_cid based on embedding and foreign cid.")
    return df

def _add_gnis_column(df: pd.DataFrame, gnis: int = None) -> pd.DataFrame:
    if 'gnis' not in df.columns:
        df['gnis'] = gnis
        logger.info(f"Added gnis column with value '{gnis}' to the dataframe.")
    return df

def _drop_duplicates_based_on_cid_and_keep_the_first_occurrence(df: pd.DataFrame) -> pd.DataFrame:
    original_length = len(df)
    df = df.drop_duplicates(subset=['cid'], keep='first')
    logger.info(f"Dropped {original_length - len(df)} rows with duplicate CIDs from {df['gnis'].iloc[0]}.")
    return df

def _drop_duplicates_based_on_bluebook_cid_and_keep_the_first_occurrence(df: pd.DataFrame) -> pd.DataFrame:
    original_length = len(df)
    df = df.drop_duplicates(subset=['bluebook_cid'], keep='first')
    logger.info(f"Dropped {original_length - len(df)} rows with duplicate bluebook_cid from {df['gnis'].iloc[0]}.")
    return df

def _fix_citation_parquet(file: Path) -> bool:
    """Get rid of any duplicate entries in the citation parquet files."""
    funcs = [
        functools.partial(_add_gnis_column, gnis=int(file.stem.split("_")[0])),
        _drop_duplicates_based_on_bluebook_cid_and_keep_the_first_occurrence,
        _get_rid_of_index_level_0_columns,
    ]
    return _fix_parquet(file, funcs)

def _fix_embeddings_parquet(file: Path) -> bool:
    """Re-generate embedding_cid based on the embedding and foreign cid."""
    funcs = [
        functools.partial(_add_gnis_column, gnis=int(file.stem.split("_")[0])),
        _make_unique_cid_out_of_embedding_and_foreign_cid,
        _get_rid_of_index_level_0_columns
    ]
    return _fix_parquet(file, funcs)

def _fix_html_parquet(file: Path) -> bool:
    """Get rid of any duplicate entries in the citation parquet files."""
    funcs = [
        functools.partial(_add_gnis_column, gnis=int(file.stem.split("_")[0])),
        _drop_duplicates_based_on_cid_and_keep_the_first_occurrence,
        _get_rid_of_index_level_0_columns,
    ]
    return _fix_parquet(file, funcs)


def fix_parquet_files_in_parallel(parquet_type: str = "_citation.parquet") -> None:
    func_dict = {
        "citation": _fix_citation_parquet,
        "embeddings": _fix_embeddings_parquet,
        "html": _fix_html_parquet
    }

    if parquet_type not in ["_citation.parquet", "_embeddings.parquet", "_html.parquet"]:
        raise ValueError("Invalid parquet type. Choose from '_citation.parquet', '_embeddings.parquet', or '_html.parquet'.")

    cid_type = parquet_type.split(".")[0].strip("_")  # Get the type of parquet file, e.g., citations
    logger.info(f"Fixing {cid_type} CIDs in all {cid_type} parquet files...")

    files = list(configs.AMERICAN_LAW_DATA_DIR.glob(f"**/*{parquet_type}"))
    for input, output in run_in_process_pool(func_dict[cid_type], files):
        if isinstance(output, Exception):
            logger.error(f"Error processing {input}: {output}")
            continue
        else:
            logger.info(f"Processed {input} successfully.")
    logger.info(f"Finished fixing all {cid_type} parquet files.")