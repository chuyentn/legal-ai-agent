from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/v1/health")
async def health():
    return {"status": "healthy", "port": os.getenv("PORT", "unknown")}

@app.get("/")
async def root():
    return {"message": "Legal AI Agent"}
