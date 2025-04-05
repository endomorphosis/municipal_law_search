from typing import List


import numpy as np


def cosine_similarity(x: List[float], y: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        x: First vector
        y: Second vector
        
    Returns:
        Cosine similarity score
    """
    return np.dot(
        np.array(x), np.array(y)
            ) / (
        np.linalg.norm(np.array(x)) * np.linalg.norm(np.array(y))
    )
