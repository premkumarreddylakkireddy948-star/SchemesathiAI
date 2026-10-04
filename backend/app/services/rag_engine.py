import os
import uuid
import datetime
import logging
from typing import List, Dict, Any, Optional

from app.services.embedding_service import get_text_embedding, get_batch_embeddings
from app.services.qdrant_service import qdrant_service
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        pass

    def extract_text(self, file_path: str) -> str:
        """Extract raw text from TXT or PDF files"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text
            except Exception as e:
                logger.warning(f"pypdf extraction failed for {file_path} ({e}), trying standard text read.")
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                cleaned_lines.append(stripped)
        return "\n".join(cleaned_lines)

    def chunk_text(self, text: str, chunk_size: int = 600, overlap: int = 150) -> List[str]:
        """Split text into overlapping semantic chunks"""
        chunks = []
        if not text:
            return chunks

        start = 0
        text_len = len(text)
        while start < text_len:
            end = min(start + chunk_size, text_len)
            
            # Adjust end to nearest sentence or line boundary if possible
            if end < text_len:
                next_newline = text.find("\n", end - 50, end + 50)
                if next_newline != -1:
                    end = next_newline

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap if end < text_len else text_len
            if start >= end:
                start = end

        return chunks

    def process_and_index_document(
        self,
        file_path: str,
        document_name: str,
        scheme_name: str = "Government Scheme",
        category: str = "General",
        source_url: str = "https://myschemes.gov.in"
    ) -> Dict[str, Any]:
        """
        Extracts, cleans, chunks, embeds, and indexes document into Qdrant Vector DB
        """
        raw_text = self.extract_text(file_path)
        cleaned_text = self.clean_text(raw_text)
        chunks = self.chunk_text(cleaned_text)

        if not chunks:
            return {"status": "error", "chunks_indexed": 0, "message": "No text content extracted."}

        embeddings = get_batch_embeddings(chunks)
        
        points = []
        update_date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")

        for idx, (chunk_str, emb_vec) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{document_name}_{idx}"))
            points.append({
                "id": point_id,
                "vector": emb_vec,
                "payload": {
                    "scheme_name": scheme_name,
                    "document_name": document_name,
                    "source_url": source_url,
                    "page_number": (idx // 3) + 1,  # Estimated page number
                    "chunk_index": idx,
                    "category": category,
                    "update_date": update_date_str,
                    "text": chunk_str
                }
            })

        success = qdrant_service.upsert_chunks(points)
        return {
            "status": "success" if success else "failed",
            "chunks_indexed": len(chunks) if success else 0,
            "document_name": document_name
        }

    def retrieve_top_chunks(self, query: str, top_k: int = 5, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Perform semantic vector search to fetch top-k relevant chunks"""
        query_vector = get_text_embedding(query)
        results = qdrant_service.search(query_vector, top_k=top_k, category=category)
        return results

    def generate_grounded_response(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Full RAG pipeline: Query -> Embedding -> Qdrant Search -> Top-K Chunks -> LLM -> Grounded Response + Sources
        """
        chunks = self.retrieve_top_chunks(query, top_k=top_k, category=category)
        
        # System prompt for agentic RAG navigator
        system_prompt = (
            "You are SchemeSathi AI, an intelligent agentic guide for Indian government schemes, "
            "scholarships, and welfare programs.\n"
            "SYSTEM RULES:\n"
            "1. Ground your response in the provided document chunks.\n"
            "2. NEVER state 'You are eligible.' Instead say 'Based on the information provided, this scheme appears potentially relevant because...'\n"
            "3. Clearly state that final eligibility must be verified with the official government authority.\n"
            "4. Be clear, accurate, encouraging, and structured using markdown headings and bullet points."
        )

        user_msg = f"User Profile Context: {user_context}\nUser Request: {query}" if user_context else query

        grounded_answer = llm_service.generate_response(system_prompt, user_msg, chunks)

        # Build clean source citations
        citations = []
        seen_keys = set()
        for c in chunks:
            p = c.get("payload", {})
            key = f"{p.get('scheme_name')}_{p.get('chunk_index')}"
            if key not in seen_keys:
                seen_keys.add(key)
                citations.append({
                    "scheme_name": p.get("scheme_name", "Government Scheme"),
                    "document_name": p.get("document_name", "Official Guideline"),
                    "source_url": p.get("source_url", "https://myschemes.gov.in"),
                    "page_number": p.get("page_number", 1),
                    "chunk_index": p.get("chunk_index", 0),
                    "category": p.get("category", "General"),
                    "update_date": p.get("update_date", ""),
                    "snippet": p.get("text", "")[:250] + "..."
                })

        return {
            "query": query,
            "answer": grounded_answer,
            "sources": citations,
            "chunks_retrieved": len(chunks)
        }

rag_engine = RAGEngine()
