"""Health check endpoint."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "healthy", "service": "legal-ai-agent", "version": "0.1.0"}
