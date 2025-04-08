import numpy as np


def cosine_similarity(x: list[float], y: list[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        x: First vector
        y: Second vector
        
    Returns:
        Cosine similarity score, ranging from -1 to 1.
            - 1 indicates identical vectors, 
            - 0 indicates orthogonal (e.g. perpendicular) vectors
            - -1 indicates opposite vectors.
    """
    return np.dot(
        np.array(x), np.array(y)
            ) / (
        np.linalg.norm(np.array(x)) * np.linalg.norm(np.array(y))
    )
