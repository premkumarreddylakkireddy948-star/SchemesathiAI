from fastapi import APIRouter, HTTPException
from app.schemas import CompareRequest, CompareResponse
from app.agent.tools import compare_schemes

router = APIRouter()

@router.post("/schemes/compare", response_model=CompareResponse)
def compare_schemes_endpoint(request: CompareRequest):
    """
    POST /api/schemes/compare
    Side-by-side scheme comparison table generation across features
    """
    if not request.scheme_ids or len(request.scheme_ids) < 1:
        raise HTTPException(status_code=400, detail="Please select at least 1 scheme to compare.")
    
    table = compare_schemes(request.scheme_ids)
    return CompareResponse(comparison_table=table)
