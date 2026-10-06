import logging
import numpy as np
from typing import List

logger = logging.getLogger(__name__)

# Lazy initialization of FastEmbed text embedding model
_model = None

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

def get_embedding_model():
    global _model
    if _model is None:
        try:
            from fastembed import TextEmbedding
            # Lightweight FastEmbed ONNX runtime (384-dimensional cosine embeddings)
            _model = TextEmbedding(model_name=MODEL_NAME)
            logger.info(f"FastEmbed model '{MODEL_NAME}' initialized successfully (384-dim, ONNX runtime).")
        except Exception as e:
            logger.warning(f"FastEmbed initialization failed ({e}), falling back to numpy semantic vector generator.")
            _model = "fallback"
    return _model

def get_text_embedding(text: str) -> List[float]:
    """
    Generate a 384-dimensional cosine-normalized vector embedding for a single text string.
    Uses FastEmbed (ONNX runtime) with deterministic fallback.
    """
    if not text or not isinstance(text, str):
        text = ""

    model = get_embedding_model()
    if model != "fallback":
        try:
            embeddings_generator = model.embed([text])
            vector = list(embeddings_generator)[0]
            if hasattr(vector, "tolist"):
                return vector.tolist()
            return [float(x) for x in vector]
        except Exception as e:
            logger.warning(f"Error generating embedding via FastEmbed: {e}")

    # Deterministic fallback semantic vector generator (384 dimensions)
    vec = np.zeros(EMBEDDING_DIMENSION, dtype=np.float32)
    words = text.lower().split()
    for word in words:
        seed = sum(ord(c) for c in word)
        np.random.seed(seed % 100000)
        word_vec = np.random.normal(0, 0.1, EMBEDDING_DIMENSION)
        vec += word_vec
    
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()

def get_batch_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate 384-dimensional embeddings for a batch of text strings using FastEmbed.
    """
    if not texts:
        return []
    
    model = get_embedding_model()
    if model != "fallback":
        try:
            embeddings_generator = model.embed(texts)
            results = []
            for vec in embeddings_generator:
                if hasattr(vec, "tolist"):
                    results.append(vec.tolist())
                else:
                    results.append([float(x) for x in vec])
            return results
        except Exception as e:
            logger.warning(f"Batch embedding failed via FastEmbed: {e}")
    
    return [get_text_embedding(t) for t in texts]
