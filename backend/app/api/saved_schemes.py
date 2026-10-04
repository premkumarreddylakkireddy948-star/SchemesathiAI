from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SavedScheme, Scheme
from app.schemas import SavedSchemeCreate, SavedSchemeResponse, SchemeResponse
from app.agent.tools import save_scheme

router = APIRouter()

@router.post("/schemes/{scheme_id}/save", response_model=SavedSchemeResponse)
def save_scheme_endpoint(scheme_id: int, payload: SavedSchemeCreate = None, db: Session = Depends(get_db)):
    """
    POST /api/schemes/{id}/save
    Save/Bookmark a scheme for quick access
    """
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme {scheme_id} not found.")

    res = save_scheme(scheme_id=scheme_id, notes=payload.notes if payload else None)
    
    saved = db.query(SavedScheme).filter(SavedScheme.id == res["id"]).first()
    sr = SchemeResponse.model_validate(scheme)
    sr.is_saved = True

    return SavedSchemeResponse(
        id=saved.id,
        scheme_id=saved.scheme_id,
        scheme=sr,
        saved_at=saved.saved_at,
        notes=saved.notes
    )

@router.get("/saved-schemes", response_model=List[SavedSchemeResponse])
def get_saved_schemes(db: Session = Depends(get_db)):
    """
    GET /api/saved-schemes
    List all bookmarked schemes with details
    """
    saved_list = db.query(SavedScheme).order_by(SavedScheme.saved_at.desc()).all()
    result = []
    for s in saved_list:
        scheme = db.query(Scheme).filter(Scheme.id == s.scheme_id).first()
        if scheme:
            sr = SchemeResponse.model_validate(scheme)
            sr.is_saved = True
            result.append(
                SavedSchemeResponse(
                    id=s.id,
                    scheme_id=s.scheme_id,
                    scheme=sr,
                    saved_at=s.saved_at,
                    notes=s.notes
                )
            )
    return result

@router.delete("/saved-schemes/{saved_id}")
def remove_saved_scheme(saved_id: int, db: Session = Depends(get_db)):
    """
    DELETE /api/saved-schemes/{id}
    Unsave/remove bookmark
    """
    saved = db.query(SavedScheme).filter(SavedScheme.id == saved_id).first()
    if not saved:
        raise HTTPException(status_code=404, detail="Saved scheme record not found.")
    
    db.delete(saved)
    db.commit()
    return {"status": "success", "message": "Scheme removed from saved list."}
