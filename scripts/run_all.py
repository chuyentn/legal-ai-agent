import os
import time
import requests
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# 1. Load config
def load_config():
    load_dotenv()
    db = {
        "host": os.getenv("SUPABASE_DB_HOST"),
        "port": int(os.getenv("SUPABASE_DB_PORT", 5432)),
        "dbname": os.getenv("SUPABASE_DB_NAME", "postgres"),
        "user": os.getenv("SUPABASE_DB_USER", "postgres"),
        "password": os.getenv("SUPABASE_DB_PASSWORD", ""),
        "sslmode": "require"
    }
    model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
    api_url = os.getenv("SEARCH_API_URL", "http://localhost:8080/v1/search")
    return db, model_name, api_url

# 2. Chunking (giả lập, có thể thay bằng script riêng)
def get_chunks(cur):
    cur.execute("SELECT id, content FROM law_chunks WHERE embedding IS NULL ORDER BY id")
    return cur.fetchall()

# 3. Embedding + lưu DB
def embed_and_save(db, model_name):
    print(f"Loading model: {model_name}")
    model = SentenceTransformer(model_name)
    conn = psycopg2.connect(**db)
    cur = conn.cursor()
    chunks = get_chunks(cur)
    total = len(chunks)
    print(f"Total chunks to embed: {total}")
    batch_size = 64
    for i in range(0, total, batch_size):
        batch = chunks[i:i+batch_size]
        ids = [r[0] for r in batch]
        texts = [r[1][:2000] for r in batch]
        embs = model.encode(texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
        for idx, emb in zip(ids, embs):
            cur.execute("UPDATE law_chunks SET embedding = %s WHERE id = %s", (emb.tolist(), str(idx)))
        conn.commit()
        print(f"Embedded: {i+len(batch)}/{total} ({(i+len(batch))*100//total}%)")
    cur.close()
    conn.close()
    print("✅ Embedding done!")

# 4. Test search API
def test_search(api_url):
    print(f"Testing search API: {api_url}")
    q = {"query": "Hợp đồng lao động là gì?", "top_k": 3}
    try:
        r = requests.post(api_url, json=q, timeout=10)
        if r.ok:
            print("Search API OK. Top results:")
            for i, item in enumerate(r.json().get("results", [])):
                print(f"{i+1}. {item.get('content', '')[:80]}")
        else:
            print("Search API error:", r.text)
    except Exception as e:
        print("Search API exception:", e)

if __name__ == "__main__":
    db, model_name, api_url = load_config()
    embed_and_save(db, model_name)
    test_search(api_url)
