import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models
from app.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "government_schemes"
VECTOR_SIZE = 384

class QdrantService:
    def __init__(self):
        self.client = self._init_client()
        self._ensure_collection()

    def _init_client(self) -> QdrantClient:
        # If QDRANT_URL is explicitly set and not localhost, connect to remote Qdrant service
        if settings.QDRANT_URL and "localhost" not in settings.QDRANT_URL and "127.0.0.1" not in settings.QDRANT_URL:
            try:
                client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None, timeout=10.0)
                client.get_collections()
                logger.info(f"Connected to remote Qdrant DB at {settings.QDRANT_URL}")
                return client
            except Exception as e:
                logger.warning(f"Could not connect to remote Qdrant at {settings.QDRANT_URL}: {e}")

        # Attempt connection to local Qdrant server
        try:
            client = QdrantClient(url=settings.QDRANT_URL or "http://localhost:6333", timeout=3.0)
            client.get_collections()
            logger.info("Connected to local Qdrant server")
            return client
        except Exception:
            logger.info("Using embedded persistent Qdrant vector store at './qdrant_db'.")
            return QdrantClient(path="./qdrant_db")

    def _ensure_collection(self):
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if COLLECTION_NAME not in collections:
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=rest_models.VectorParams(
                        size=VECTOR_SIZE,
                        distance=rest_models.Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection '{COLLECTION_NAME}' with vector size {VECTOR_SIZE} and Cosine distance metric.")
        except Exception as e:
            logger.error(f"Error ensuring Qdrant collection: {e}")

    def upsert_chunks(self, points: List[Dict[str, Any]]) -> bool:
        if not points:
            return True
        
        qdrant_points = []
        for p in points:
            qdrant_points.append(
                rest_models.PointStruct(
                    id=p["id"],
                    vector=p["vector"],
                    payload=p["payload"]
                )
            )

        try:
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=qdrant_points
            )
            return True
        except Exception as e:
            logger.error(f"Failed to upsert points to Qdrant: {e}")
            return False

    def search(self, query_vector: List[float], top_k: int = 5, category: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            query_filter = None
            if category and category != "All":
                query_filter = rest_models.Filter(
                    must=[
                        rest_models.FieldCondition(
                            key="category",
                            match=rest_models.MatchValue(value=category)
                        )
                    ]
                )

            try:
                results = self.client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=query_vector,
                    limit=top_k,
                    query_filter=query_filter
                )
            except AttributeError:
                results = self.client.query_points(
                    collection_name=COLLECTION_NAME,
                    query=query_vector,
                    limit=top_k,
                    query_filter=query_filter
                ).points

            output = []
            for res in results:
                payload = getattr(res, "payload", {})
                score = getattr(res, "score", 0.0)
                output.append({
                    "score": float(score),
                    "payload": payload
                })
            return output
        except Exception as e:
            logger.error(f"Qdrant search error: {e}")
            return []

    def delete_document_chunks(self, document_name: str) -> bool:
        try:
            self.client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=rest_models.FilterSelector(
                    filter=rest_models.Filter(
                        must=[
                            rest_models.FieldCondition(
                                key="document_name",
                                match=rest_models.MatchValue(value=document_name)
                            )
                        ]
                    )
                )
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting chunks for document {document_name}: {e}")
            return False

qdrant_service = QdrantService()
