"""Legal AI Agent — FastAPI Application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import legal, contracts, chat, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: initialize connections
    print("🏛️ Legal AI Agent starting up...")
    yield
    # Shutdown: cleanup
    print("Legal AI Agent shutting down...")


app = FastAPI(
    title="Legal AI Agent",
    description="AI-powered legal assistant for Vietnamese companies",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, tags=["Health"])
app.include_router(legal.router, prefix="/v1/legal", tags=["Legal Q&A"])
app.include_router(contracts.router, prefix="/v1/contracts", tags=["Contract Review"])
app.include_router(chat.router, prefix="/v1/chat", tags=["Chat"])
