from typing import Optional


import duckdb
import numpy as np


from configs import configs
from logger import logger
from utils.llm.cosine_similarity import cosine_similarity


def get_embedding_and_calculate_cosine_similarity(
    embedding_data: dict[str, str],
    query_embedding: list[float] = None,
) -> Optional[tuple[str, float]]:
    """
    Calculate the cosine similarity between a query embedding and a given embedding.

    Args:
        embedding_data (dict[str, str]): A dictionary containing the embedding_cid and cid.
        query_embedding (list[float], optional): The embedding vector for the query.

    Returns:
        Optional[tuple[str, float]]: A tuple containing the CID and similarity score if the
                                    cosine similarity exceeds the threshold, otherwise None.
    """
    try:
        # Extract the embedding and CID from the input data
        embedding_cid = embedding_data.get("embedding_cid")
        cid = embedding_data.get("cid")

        if not embedding_cid or not cid:
            logger.debug("No embedding CID or CID found in the input data.")
            return None

        with duckdb.connect(configs.AMERICAN_LAW_DATA_DIR / "embeddings.db", read_only=True) as conn:
            with conn.cursor() as cursor:

                # Fetch the embedding from the database
                cursor.execute('''
                    SELECT embedding, cid
                    FROM embeddings
                    WHERE embedding_cid = ?
                    LIMIT 1;
                ''', (embedding_cid,))
                embedding: dict = cursor.fetchdf().to_dict(orient='records')[0]
                if not embedding:
                    #logger.debug(f"No embedding found for the given CID {cid}.")
                    return None

                law_embedding = embedding.get("embedding")
                if law_embedding is None:
                    return None

                # Calculate the cosine similarity
                similarity_score: np.float64 = cosine_similarity(query_embedding, law_embedding)
                #logger.debug(f"\nCosine similarity score: {similarity_score}")

                # Yield the CID if the similarity score exceeds the threshold
                if similarity_score >= configs.SIMILARITY_SCORE_THRESHOLD:
                    return cid, similarity_score.item()
                else:
                    return None

    except Exception as e:
        logger.error(f"Error in get_embedding_and_calculate_cosine_similarity: {e}")
        return None
