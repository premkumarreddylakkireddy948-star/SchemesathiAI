from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Source Citation Schema
class SourceCitation(BaseModel):
    scheme_name: str
    document_name: str
    source_url: Optional[str] = None
    page_number: Optional[int] = 1
    chunk_index: Optional[int] = 0
    category: Optional[str] = "General"
    update_date: Optional[str] = None
    snippet: str

# Chat & Query Schemas
class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: Optional[str] = None
    question: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None

    @property
    def effective_message(self) -> str:
        return self.message or self.question or ""

class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    answer: Optional[str] = None
    sources: List[SourceCitation] = []
    relevant_scheme_ids: List[int] = []
    agent_steps: Optional[List[str]] = None

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    category: Optional[str] = None

class QueryResponse(BaseModel):
    query: str
    sources: List[SourceCitation]

# Scheme Schemas
class SchemeBase(BaseModel):
    scheme_code: str
    name: str
    ministry_or_department: str
    category: str
    state: str = "All India"
    summary: str
    eligibility_criteria: str
    benefits: str
    income_limit: Optional[float] = None
    required_documents: str
    application_process: str
    official_portal_url: str

class SchemeResponse(SchemeBase):
    id: int
    is_active: bool
    updated_at: datetime
    is_saved: Optional[bool] = False

    class Config:
        from_attributes = True

# Compare Schema
class CompareRequest(BaseModel):
    scheme_ids: List[int]

class CompareResponse(BaseModel):
    comparison_table: List[Dict[str, Any]]

# Document Schema
class DocumentResponse(BaseModel):
    id: int
    document_name: str
    file_path: str
    scheme_id: Optional[int]
    category: str
    file_size: int
    upload_date: datetime
    chunk_count: int

    class Config:
        from_attributes = True

# Checklist Schemas
class ChecklistItemBase(BaseModel):
    document_name: str
    status: str = "Missing"  # Available, Missing, Not Applicable
    notes: Optional[str] = None

class ChecklistItemResponse(ChecklistItemBase):
    id: int

    class Config:
        from_attributes = True

class ChecklistItemUpdate(BaseModel):
    id: int
    status: str  # Available, Missing, Not Applicable
    notes: Optional[str] = None

class ChecklistCreate(BaseModel):
    scheme_id: int
    items: Optional[List[ChecklistItemBase]] = None

class ChecklistResponse(BaseModel):
    id: int
    scheme_id: int
    scheme_name: str
    items: List[ChecklistItemResponse]
    created_at: datetime

    class Config:
        from_attributes = True

# Saved Scheme Schemas
class SavedSchemeCreate(BaseModel):
    scheme_id: int
    notes: Optional[str] = None

class SavedSchemeResponse(BaseModel):
    id: int
    scheme_id: int
    scheme: SchemeResponse
    saved_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True
