from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Scheme, SavedScheme
from app.schemas import SchemeResponse

router = APIRouter()

@router.get("/schemes", response_model=List[SchemeResponse])
def get_schemes(
    category: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    GET /api/schemes
    List government schemes with optional filtering by category, state, or search text
    """
    q = db.query(Scheme).filter(Scheme.is_active == True)
    
    if category and category != "All":
        q = q.filter(Scheme.category == category)
    if state and state != "All India":
        q = q.filter((Scheme.state == state) | (Scheme.state == "All India"))
    if search and search.strip():
        pattern = f"%{search.strip()}%"
        q = q.filter(
            (Scheme.name.ilike(pattern)) |
            (Scheme.summary.ilike(pattern)) |
            (Scheme.eligibility_criteria.ilike(pattern)) |
            (Scheme.category.ilike(pattern))
        )
    
    schemes = q.all()
    
    # Check saved schemes
    saved_ids = set(r[0] for r in db.query(SavedScheme.scheme_id).all())
    
    result = []
    for s in schemes:
        sr = SchemeResponse.model_validate(s)
        sr.is_saved = s.id in saved_ids
        result.append(sr)
        
    return result

@router.get("/schemes/{scheme_id}", response_model=SchemeResponse)
def get_scheme_by_id(scheme_id: int, db: Session = Depends(get_db)):
    """
    GET /api/schemes/{id}
    Retrieve detailed information for a specific scheme
    """
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme with ID {scheme_id} not found.")
    
    sr = SchemeResponse.model_validate(scheme)
    saved = db.query(SavedScheme).filter(SavedScheme.scheme_id == scheme_id).first()
    sr.is_saved = bool(saved)
    return sr
