"""Chat session endpoints."""
from fastapi import APIRouter, HTTPException
from src.models.schemas import ChatMessageRequest, ChatMessageResponse

router = APIRouter()

@router.post("/sessions")
async def create_session():
    """Create a new chat session."""
    raise HTTPException(status_code=501, detail="Coming soon")

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """Send a message in a chat session."""
    raise HTTPException(status_code=501, detail="Coming soon")
