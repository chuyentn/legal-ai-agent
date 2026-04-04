"""Embedding service for text vectorization."""

import os
from typing import Optional

import httpx


class Embedder:
    """Generate embeddings for text using OpenAI or self-hosted model."""
    
    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        dimensions: int = 1024,
    ):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or "https://api.openai.com/v1"
        self.dimensions = dimensions
    
    async def embed(self, text: str) -> list[float]:
        """Embed a single text string."""
        results = await self.embed_batch([text])
        return results[0]
    
    async def embed_batch(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        """Embed multiple texts in batches."""
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "input": batch,
                        "dimensions": self.dimensions,
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()
                
                embeddings = [item["embedding"] for item in data["data"]]
                all_embeddings.extend(embeddings)
        
        return all_embeddings


# Singleton
_embedder: Optional[Embedder] = None


def get_embedder() -> Embedder:
    """Get or create the embedder singleton."""
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder
