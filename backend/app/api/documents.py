import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DocumentModel, Scheme
from app.schemas import DocumentResponse
from app.services.rag_engine import rag_engine
from app.services.qdrant_service import qdrant_service

router = APIRouter()

UPLOAD_DIR = "data/sample_documents"

@router.post("/documents/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    scheme_id: Optional[int] = Form(None),
    category: Optional[str] = Form("General"),
    db: Session = Depends(get_db)
):
    """
    POST /api/documents/upload
    Upload document file (TXT / PDF), parse, chunk, embed, and index into Qdrant vector database
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size = os.path.getsize(file_location)

    scheme_name = "Government Scheme"
    if scheme_id:
        scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
        if scheme:
            scheme_name = scheme.name
            category = scheme.category

    # RAG Ingestion Pipeline
    res = rag_engine.process_and_index_document(
        file_path=file_location,
        document_name=file.filename,
        scheme_name=scheme_name,
        category=category or "General"
    )

    doc = DocumentModel(
        document_name=file.filename,
        file_path=file_location,
        scheme_id=scheme_id,
        category=category or "General",
        file_size=file_size,
        chunk_count=res.get("chunks_indexed", 0)
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc

@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    """
    GET /api/documents
    List all knowledge base documents and indexing status
    """
    return db.query(DocumentModel).order_by(DocumentModel.upload_date.desc()).all()

@router.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """
    DELETE /api/documents/{id}
    Delete document record and purge vector embeddings from Qdrant
    """
    doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    # Delete from Qdrant
    qdrant_service.delete_document_chunks(doc.document_name)
    
    # Delete file if exists
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    return {"status": "success", "message": f"Document '{doc.document_name}' deleted."}
