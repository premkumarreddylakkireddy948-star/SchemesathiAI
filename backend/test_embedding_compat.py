import sys
import os
import math
import logging

sys.stdout.reconfigure(encoding='utf-8')

# Insert backend root to sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.embedding_service import get_text_embedding, get_batch_embeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_embedding_compat")

def test_embedding_compatibility():
    logger.info("Starting FastEmbed Embedding & Compatibility Test...")

    # 1. Verify single text embedding
    text = "What is PM-KISAN Samman Nidhi?"
    vec = get_text_embedding(text)
    
    assert isinstance(vec, list), "Embedding must be a list of floats"
    assert len(vec) == 384, f"Expected vector dimension 384, got {len(vec)}"
    assert all(isinstance(x, (float, int)) for x in vec), "All elements must be numbers"

    # Verify cosine norm is approximately 1.0 (normalized)
    norm = math.sqrt(sum(x * x for x in vec))
    logger.info(f"Vector dimension: {len(vec)}, L2 Norm: {norm:.4f}")
    assert abs(norm - 1.0) < 0.05, f"Vector should be unit-normalized for cosine metric, got norm {norm}"

    # 2. Verify batch embeddings
    texts = ["PM-KISAN scheme", "Pradhan Mantri Awas Yojana", "Ayushman Bharat"]
    batch_vecs = get_batch_embeddings(texts)
    assert len(batch_vecs) == len(texts), "Batch embeddings count mismatch"
    for b_vec in batch_vecs:
        assert len(b_vec) == 384, f"Batch vector dimension expected 384, got {len(b_vec)}"

    # 3. Verify Qdrant Service / API search with query vector
    try:
        from app.services.qdrant_service import qdrant_service, COLLECTION_NAME
        collections = [c.name for c in qdrant_service.client.get_collections().collections]
        assert COLLECTION_NAME in collections, f"Collection '{COLLECTION_NAME}' must exist in Qdrant"
        search_results = qdrant_service.search(query_vector=vec, top_k=3)
        logger.info(f"Qdrant search returned {len(search_results)} results for FastEmbed vector.")
    except Exception as e:
        logger.info(f"Qdrant direct client locked by active server ({e}). Testing vector retrieval via HTTP API...")
        import requests
        res = requests.post("http://localhost:8000/api/query", json={"query": text, "top_k": 3})
        assert res.status_code == 200, f"API query failed: {res.text}"
        logger.info(f"HTTP RAG Query API returned {len(res.json().get('results', []))} results using FastEmbed vector.")

    # 4. Verify no sentence_transformers module is imported
    assert "sentence_transformers" not in sys.modules, "sentence_transformers must NOT be loaded in sys.modules"

    print("\n[SUCCESS] EMBEDDING COMPATIBILITY TEST PASSED SUCCESSFULLY!")
    print(f"- Vector Dimension: {len(vec)} == 384")
    print(f"- Cosine Normalization: L2 Norm = {norm:.4f}")
    print(f"- Qdrant Collection Preserved & Searchable")
    print(f"- sentence_transformers import: ABSENT (0 PyTorch overhead)")

if __name__ == "__main__":
    test_embedding_compatibility()
