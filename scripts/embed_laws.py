"""
Embed crawled law articles into Supabase pgvector.
Run after crawl_laws.py.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import asyncio
from src.rag.embedder import get_embedder
from src.services.supabase_client import get_supabase

DATA_DIR = Path(__file__).parent.parent / "data" / "laws"


async def process_law_file(filepath: Path):
    """Process a single law JSON file and insert into Supabase."""
    with open(filepath, "r", encoding="utf-8") as f:
        law_data = json.load(f)
    
    supabase = get_supabase()
    embedder = get_embedder()
    
    print(f"\n📜 Processing: {law_data['name']}")
    
    # 1. Insert law document
    law_doc = {
        "title": law_data["name"],
        "law_number": law_data["number"],
        "law_type": law_data["type"],
        "issuer": law_data["issuer"],
        "domains": law_data["domains"],
        "status": "active",
        "full_text": law_data.get("full_text", ""),
        "article_count": law_data.get("article_count", 0),
        "word_count": law_data.get("word_count", 0),
        "source_url": law_data.get("url", ""),
        "source_site": "thuvienphapluat",
    }
    
    result = supabase.table("law_documents").insert(law_doc).execute()
    law_id = result.data[0]["id"]
    print(f"  ✅ Law document inserted: {law_id}")
    
    # 2. Chunk and embed articles
    articles = law_data.get("articles", [])
    if not articles:
        print("  ⚠️ No articles found")
        return
    
    # Prepare chunks
    chunks = []
    for art in articles:
        content = art["content"]
        if not content.strip():
            continue
        
        # Build searchable text
        chunk_text = f"{art['article']}. {art.get('title', '')}\n{content}"
        
        # Parent context for better retrieval
        parent_ctx = f"{law_data['name']} ({law_data['number']})"
        if art.get("chapter"):
            parent_ctx += f" > {art['chapter']}"
        
        chunks.append({
            "law_id": law_id,
            "chapter": art.get("chapter", ""),
            "section": art.get("section", ""),
            "article": art["article"],
            "title": art.get("title", ""),
            "content": content,
            "parent_context": parent_ctx,
            "domains": law_data["domains"],
        })
    
    print(f"  📋 {len(chunks)} chunks to embed")
    
    # 3. Embed in batches
    batch_size = 20
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [c["content"] for c in batch]
        
        embeddings = await embedder.embed_batch(texts)
        
        # Insert with embeddings
        rows = []
        for chunk, embedding in zip(batch, embeddings):
            rows.append({
                **chunk,
                "embedding": embedding,
            })
        
        supabase.table("law_chunks").insert(rows).execute()
        print(f"  ✅ Embedded batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
    
    print(f"  🎉 Done: {len(chunks)} chunks embedded")


async def main():
    """Process all crawled law files."""
    print("🏛️ Legal AI — Law Embedding Pipeline")
    
    json_files = list(DATA_DIR.glob("*.json"))
    if not json_files:
        print("❌ No law files found. Run crawl_laws.py first.")
        return
    
    print(f"Found {len(json_files)} law files")
    
    for filepath in json_files:
        try:
            await process_law_file(filepath)
        except Exception as e:
            print(f"  ❌ Error processing {filepath.name}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
