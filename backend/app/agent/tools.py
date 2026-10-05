import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Scheme, DocumentModel, SavedScheme, Checklist, ChecklistItem
from app.services.rag_engine import rag_engine
from app.services.web_search_service import web_search_service, is_official_government_domain

logger = logging.getLogger(__name__)

def search_schemes(query: str, category: Optional[str] = None, state: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search structured schemes database by query, category, or state"""
    db: Session = SessionLocal()
    try:
        q = db.query(Scheme).filter(Scheme.is_active == True)
        if category and category != "All":
            q = q.filter(Scheme.category == category)
        if state and state != "All India":
            q = q.filter((Scheme.state == state) | (Scheme.state == "All India"))
        if query:
            search_pattern = f"%{query}%"
            q = q.filter(
                (Scheme.name.ilike(search_pattern)) |
                (Scheme.summary.ilike(search_pattern)) |
                (Scheme.eligibility_criteria.ilike(search_pattern)) |
                (Scheme.category.ilike(search_pattern))
            )
        schemes = q.all()
        return [
            {
                "id": s.id,
                "scheme_code": s.scheme_code,
                "name": s.name,
                "ministry_or_department": s.ministry_or_department,
                "category": s.category,
                "state": s.state,
                "summary": s.summary,
                "income_limit": s.income_limit,
                "official_portal_url": s.official_portal_url,
                "is_official": is_official_government_domain(s.official_portal_url)
            }
            for s in schemes
        ]
    finally:
        db.close()

def search_knowledge_base(query: str, top_k: int = 5, category: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve grounded chunks from Qdrant vector database using RAG pipeline"""
    return rag_engine.generate_grounded_response(query=query, top_k=top_k, category=category)

def search_web_for_government_schemes(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search live web for official government scheme updates and links"""
    return web_search_service.search_official_schemes(query, max_results=max_results)

def get_scheme_details(scheme_id_or_code: Any) -> Optional[Dict[str, Any]]:
    """Retrieve full details of a specific government scheme by ID or code"""
    db: Session = SessionLocal()
    try:
        if isinstance(scheme_id_or_code, int) or str(scheme_id_or_code).isdigit():
            scheme = db.query(Scheme).filter(Scheme.id == int(scheme_id_or_code)).first()
        else:
            scheme = db.query(Scheme).filter(Scheme.scheme_code == str(scheme_id_or_code)).first()
        
        if not scheme:
            return None
        return {
            "id": scheme.id,
            "scheme_code": scheme.scheme_code,
            "name": scheme.name,
            "ministry_or_department": scheme.ministry_or_department,
            "category": scheme.category,
            "state": scheme.state,
            "summary": scheme.summary,
            "eligibility_criteria": scheme.eligibility_criteria,
            "benefits": scheme.benefits,
            "income_limit": scheme.income_limit,
            "required_documents": scheme.required_documents,
            "application_process": scheme.application_process,
            "official_portal_url": scheme.official_portal_url,
            "is_official": is_official_government_domain(scheme.official_portal_url)
        }
    finally:
        db.close()

def check_eligibility(scheme_id: int, user_income: Optional[float] = None, user_state: Optional[str] = None, user_category: Optional[str] = None, occupation: Optional[str] = None) -> Dict[str, Any]:
    """Analyze eligibility parameters against official scheme requirements"""
    db: Session = SessionLocal()
    try:
        scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
        if not scheme:
            return {"status": "error", "message": f"Scheme with ID {scheme_id} not found."}
        
        reasons = []
        is_potentially_eligible = True

        if scheme.income_limit and user_income is not None:
            if user_income > scheme.income_limit:
                is_potentially_eligible = False
                reasons.append(f"Family annual income (₹{user_income:,.0f}) exceeds maximum limit (₹{scheme.income_limit:,.0f}).")
            else:
                reasons.append(f"Family annual income (₹{user_income:,.0f}) is within limit (₹{scheme.income_limit:,.0f}).")

        if scheme.state != "All India" and user_state and user_state != scheme.state:
            is_potentially_eligible = False
            reasons.append(f"Scheme is specific to {scheme.state}, but user state is {user_state}.")
        else:
            reasons.append(f"State eligibility matches ({scheme.state}).")

        verdict = (
            "Based on the information provided, this scheme appears potentially relevant because " + " ".join(reasons)
            if is_potentially_eligible
            else "Based on the parameters provided, you may not meet certain criteria: " + " ".join(reasons)
        )
        
        return {
            "scheme_id": scheme.id,
            "scheme_name": scheme.name,
            "is_potentially_eligible": is_potentially_eligible,
            "reasons": reasons,
            "verdict": verdict,
            "disclaimer": "Final eligibility must be verified with the official government authority."
        }
    finally:
        db.close()

def get_required_documents(scheme_id_or_name: Any) -> List[str]:
    """Get itemized list of mandatory documents for a scheme"""
    db: Session = SessionLocal()
    try:
        scheme = None
        if isinstance(scheme_id_or_name, int) or (isinstance(scheme_id_or_name, str) and scheme_id_or_name.isdigit()):
            scheme = db.query(Scheme).filter(Scheme.id == int(scheme_id_or_name)).first()
        elif isinstance(scheme_id_or_name, str):
            scheme = db.query(Scheme).filter(Scheme.name.ilike(f"%{scheme_id_or_name}%")).first()
            
        if not scheme:
            return ["Aadhaar Card", "Income Certificate", "Bank Passbook", "Proof of Residency"]
        
        docs_raw = scheme.required_documents or ""
        if docs_raw.startswith("["):
            try:
                return json.loads(docs_raw)
            except Exception:
                pass
        return [line.strip("- *1234567890.") for line in docs_raw.split("\n") if line.strip()]
    finally:
        db.close()

def get_application_process(scheme_id_or_name: Any) -> Dict[str, Any]:
    """Retrieve application workflow and official portal link"""
    db: Session = SessionLocal()
    try:
        scheme = None
        if isinstance(scheme_id_or_name, int) or (isinstance(scheme_id_or_name, str) and scheme_id_or_name.isdigit()):
            scheme = db.query(Scheme).filter(Scheme.id == int(scheme_id_or_name)).first()
        elif isinstance(scheme_id_or_name, str):
            scheme = db.query(Scheme).filter(Scheme.name.ilike(f"%{scheme_id_or_name}%")).first()

        if not scheme:
            return {"status": "error", "message": "Scheme not found."}
        return {
            "scheme_name": scheme.name,
            "application_process": scheme.application_process,
            "official_portal_url": scheme.official_portal_url,
            "is_official": is_official_government_domain(scheme.official_portal_url)
        }
    finally:
        db.close()

def compare_schemes(scheme_names_or_ids: List[Any]) -> List[Dict[str, Any]]:
    """Compare multiple schemes side by side across features"""
    db: Session = SessionLocal()
    try:
        schemes = []
        for sid in scheme_names_or_ids:
            if isinstance(sid, int) or (isinstance(sid, str) and sid.isdigit()):
                s = db.query(Scheme).filter(Scheme.id == int(sid)).first()
            else:
                s = db.query(Scheme).filter(Scheme.name.ilike(f"%{sid}%")).first()
            if s and s not in schemes:
                schemes.append(s)

        if not schemes:
            # Fallback default queries if not found in db directly
            schemes = db.query(Scheme).limit(2).all()

        features = [
            "Purpose",
            "Eligibility Criteria",
            "Benefits Offered",
            "Income Limit",
            "Required Documents",
            "Application Process",
            "Official Portal"
        ]
        
        table = []
        for feat in features:
            row = {"Feature": feat}
            for s in schemes:
                if feat == "Purpose":
                    row[s.name] = s.summary
                elif feat == "Eligibility Criteria":
                    row[s.name] = s.eligibility_criteria
                elif feat == "Benefits Offered":
                    row[s.name] = s.benefits
                elif feat == "Income Limit":
                    row[s.name] = f"₹{s.income_limit:,.0f} per year" if s.income_limit else "No Income Limit"
                elif feat == "Required Documents":
                    row[s.name] = s.required_documents
                elif feat == "Application Process":
                    row[s.name] = s.application_process
                elif feat == "Official Portal":
                    row[s.name] = s.official_portal_url
            table.append(row)
        return table
    finally:
        db.close()

def save_scheme(scheme_id: int, user_id: Optional[int] = None, notes: Optional[str] = None) -> Dict[str, Any]:
    """Save a scheme to user's saved list"""
    db: Session = SessionLocal()
    try:
        existing = db.query(SavedScheme).filter(
            SavedScheme.scheme_id == scheme_id,
            SavedScheme.user_id == user_id
        ).first()
        if existing:
            return {"status": "already_saved", "message": "Scheme is already saved in your bookmarks.", "id": existing.id}
        
        saved = SavedScheme(scheme_id=scheme_id, user_id=user_id, notes=notes or "Saved via AI Navigator")
        db.add(saved)
        db.commit()
        db.refresh(saved)
        return {"status": "success", "message": "Scheme saved successfully!", "id": saved.id}
    finally:
        db.close()

def create_document_checklist(scheme_id_or_name: Any, user_id: Optional[int] = None) -> Dict[str, Any]:
    """Generate interactive document checklist for a scheme"""
    db: Session = SessionLocal()
    try:
        scheme = None
        if isinstance(scheme_id_or_name, int) or (isinstance(scheme_id_or_name, str) and scheme_id_or_name.isdigit()):
            scheme = db.query(Scheme).filter(Scheme.id == int(scheme_id_or_name)).first()
        elif isinstance(scheme_id_or_name, str):
            scheme = db.query(Scheme).filter(Scheme.name.ilike(f"%{scheme_id_or_name}%")).first()

        if not scheme:
            # Fallback mock checklist
            return {
                "scheme_name": str(scheme_id_or_name),
                "items": [
                    {"document_name": "Aadhaar Card", "status": "Mandatory"},
                    {"document_name": "Land Revenue Record / Income Certificate", "status": "Mandatory"},
                    {"document_name": "Active Bank Passbook", "status": "Mandatory"}
                ]
            }
        
        chk = db.query(Checklist).filter(
            Checklist.scheme_id == scheme.id,
            Checklist.user_id == user_id
        ).first()
        
        if not chk:
            chk = Checklist(scheme_id=scheme.id, user_id=user_id)
            db.add(chk)
            db.commit()
            db.refresh(chk)
            
            docs = get_required_documents(scheme.id)
            for doc in docs:
                if doc:
                    item = ChecklistItem(checklist_id=chk.id, document_name=doc, status="Missing")
                    db.add(item)
            db.commit()
            db.refresh(chk)

        items = db.query(ChecklistItem).filter(ChecklistItem.checklist_id == chk.id).all()
        return {
            "checklist_id": chk.id,
            "scheme_id": scheme.id,
            "scheme_name": scheme.name,
            "items": [
                {"id": it.id, "document_name": it.document_name, "status": it.status, "notes": it.notes}
                for it in items
            ]
        }
    finally:
        db.close()
