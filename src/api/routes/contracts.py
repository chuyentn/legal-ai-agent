"""Contract review endpoints."""
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.models.schemas import ContractReviewResponse

router = APIRouter()

@router.post("/review", response_model=ContractReviewResponse)
async def review_contract(file: UploadFile = File(...)):
    """Upload and review a contract for legal compliance."""
    # TODO: implement contract review pipeline
    raise HTTPException(status_code=501, detail="Coming soon")

@router.get("/{job_id}/report")
async def get_review_report(job_id: str):
    """Get the review report for a submitted contract."""
    raise HTTPException(status_code=501, detail="Coming soon")
