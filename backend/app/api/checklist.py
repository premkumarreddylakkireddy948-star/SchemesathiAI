from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Checklist, ChecklistItem, Scheme
from app.schemas import ChecklistCreate, ChecklistResponse, ChecklistItemUpdate
from app.agent.tools import create_document_checklist

router = APIRouter()

@router.post("/checklist", response_model=ChecklistResponse)
def get_or_create_checklist(request: ChecklistCreate, db: Session = Depends(get_db)):
    """
    POST /api/checklist
    Retrieve or initialize interactive document checklist for a scheme
    """
    res = create_document_checklist(scheme_id=request.scheme_id)
    if res.get("status") == "error":
        raise HTTPException(status_code=404, detail=res.get("message"))

    chk = db.query(Checklist).filter(Checklist.id == res["checklist_id"]).first()
    items = db.query(ChecklistItem).filter(ChecklistItem.checklist_id == chk.id).all()

    return ChecklistResponse(
        id=chk.id,
        scheme_id=chk.scheme_id,
        scheme_name=res["scheme_name"],
        items=items,
        created_at=chk.created_at
    )

@router.get("/checklist/{scheme_id}", response_model=ChecklistResponse)
def get_checklist_by_scheme(scheme_id: int, db: Session = Depends(get_db)):
    """
    GET /api/checklist/{scheme_id}
    Get active checklist for scheme
    """
    chk = db.query(Checklist).filter(Checklist.scheme_id == scheme_id).first()
    if not chk:
        res = create_document_checklist(scheme_id=scheme_id)
        if res.get("status") == "error":
            raise HTTPException(status_code=404, detail=res.get("message"))
        chk = db.query(Checklist).filter(Checklist.id == res["checklist_id"]).first()

    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    items = db.query(ChecklistItem).filter(ChecklistItem.checklist_id == chk.id).all()

    return ChecklistResponse(
        id=chk.id,
        scheme_id=chk.scheme_id,
        scheme_name=scheme.name if scheme else "Government Scheme",
        items=items,
        created_at=chk.created_at
    )

@router.put("/checklist/items/{item_id}")
def update_checklist_item(item_id: int, update: ChecklistItemUpdate, db: Session = Depends(get_db)):
    """
    PUT /api/checklist/items/{id}
    Update status (Available / Missing / Not Applicable) and notes for a document item
    """
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found.")
    
    item.status = update.status
    if update.notes is not None:
        item.notes = update.notes

    db.commit()
    db.refresh(item)
    return {"status": "success", "item": {"id": item.id, "status": item.status, "notes": item.notes}}
