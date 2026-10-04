from fastapi import APIRouter
from app.schemas import QueryRequest, QueryResponse, SourceCitation
from app.services.rag_engine import rag_engine

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    """
    POST /api/query
    Direct RAG semantic search and chunk retrieval endpoint
    """
    chunks = rag_engine.retrieve_top_chunks(
        query=request.query,
        top_k=request.top_k,
        category=request.category
    )

    citations = []
    for c in chunks:
        p = c.get("payload", {})
        citations.append(
            SourceCitation(
                scheme_name=p.get("scheme_name", "Government Scheme"),
                document_name=p.get("document_name", "Official Guideline"),
                source_url=p.get("source_url"),
                page_number=p.get("page_number", 1),
                chunk_index=p.get("chunk_index", 0),
                category=p.get("category", "General"),
                update_date=p.get("update_date"),
                snippet=p.get("text", "")
            )
        )

    return QueryResponse(
        query=request.query,
        sources=citations
    )
