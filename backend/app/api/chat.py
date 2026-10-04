import uuid
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Conversation, Message
from app.schemas import ChatRequest, ChatResponse, SourceCitation
from app.agent.graph import agent_executor

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    POST /api/chat
    Chat with SchemeSathi AI LangGraph Agent.
    Full RAG grounding, multi-tool agent execution, and source citations.
    """
    cid = request.conversation_id
    if not cid or cid.strip() == "":
        cid = str(uuid.uuid4())
    
    user_query = request.effective_message
    if not user_query:
        raise HTTPException(status_code=400, detail="Query message or question is required")

    # Check or create conversation
    conv = db.query(Conversation).filter(Conversation.id == cid).first()
    if not conv:
        conv = Conversation(id=cid, title=user_query[:40])
        db.add(conv)
        db.commit()

    # Save user message
    user_msg = Message(
        conversation_id=cid,
        sender="user",
        content=user_query
    )
    db.add(user_msg)
    db.commit()

    # Execute Agent graph
    agent_output = agent_executor.run(
        query=user_query,
        user_context=request.user_context
    )

    answer_text = agent_output.get("answer", "")
    raw_sources = agent_output.get("sources", [])
    scheme_ids = agent_output.get("scheme_ids", [])
    tools_used = agent_output.get("tools_used", [])

    # Format source citations
    citations = [
        SourceCitation(
            scheme_name=s.get("scheme_name", "Government Scheme"),
            document_name=s.get("document_name", "Guideline"),
            source_url=s.get("source_url"),
            page_number=s.get("page_number", 1),
            chunk_index=s.get("chunk_index", 0),
            category=s.get("category", "General"),
            update_date=s.get("update_date"),
            snippet=s.get("snippet", "")
        )
        for s in raw_sources
    ]

    # Save agent message with sources json
    agent_msg = Message(
        conversation_id=cid,
        sender="agent",
        content=answer_text,
        sources_json=json.dumps([c.model_dump() for c in citations])
    )
    db.add(agent_msg)
    db.commit()

    return ChatResponse(
        conversation_id=cid,
        message=answer_text,
        answer=answer_text,
        sources=citations,
        relevant_scheme_ids=scheme_ids,
        agent_steps=tools_used
    )
