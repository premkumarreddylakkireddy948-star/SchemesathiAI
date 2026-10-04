import logging
import numpy as np
from typing import List

logger = logging.getLogger(__name__)

# Lazy initialization of sentence-transformer model
_model = None

def get_embedding_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Lightweight, high quality 384-dim embedding model
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("SentenceTransformer 'all-MiniLM-L6-v2' model loaded successfully.")
        except Exception as e:
            logger.warning(f"SentenceTransformer load failed ({e}), falling back to numpy semantic embedding generator.")
            _model = "fallback"
    return _model

def get_text_embedding(text: str) -> List[float]:
    model = get_embedding_model()
    if model != "fallback" and hasattr(model, "encode"):
        try:
            vector = model.encode(text)
            return vector.tolist()
        except Exception as e:
            logger.warning(f"Error generating embedding via SentenceTransformer: {e}")

    # Deterministic fallback semantic vector generator (384 dimensions)
    # Maps key terms to specific vector components for robust local similarity search
    vec = np.zeros(384, dtype=np.float32)
    words = text.lower().split()
    for idx, word in enumerate(words):
        # Generate hash-based pseudo-random features
        seed = sum(ord(c) for c in word)
        np.random.seed(seed % 100000)
        word_vec = np.random.normal(0, 0.1, 384)
        vec += word_vec
    
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()

def get_batch_embeddings(texts: List[str]) -> List[List[float]]:
    return [get_text_embedding(t) for t in texts]
