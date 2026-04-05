import os
"""Generate embeddings for law_chunks using local model"""
import time
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

host = os.getenv("SUPABASE_DB_HOST", "localhost")
is_pooler = "pooler" in host.lower()

# Avoid Windows TLS issues when downloading HF models
os.environ.setdefault("HF_HUB_DISABLE_SSL_VERIFICATION", "1")
os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "10")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "30")

DB_CONFIG = {
    "host": host,
    "port": 6543 if is_pooler else 5432,
    "dbname": "postgres",
    "user": "postgres.cjkrsnqdsfucngmrsnpm" if is_pooler else "postgres",
    "password": os.getenv("SUPABASE_DB_PASSWORD", ""),
    "sslmode": "require"
}

# Use multilingual model that supports Vietnamese well
# paraphrase-multilingual-MiniLM-L12-v2: 384 dims, fast, good for Vietnamese
# But our DB uses 1536 dims... let's check

print("Loading model...")
# intfloat/multilingual-e5-large: 1024 dims
# BAAI/bge-m3: 1024 dims  
# We need 1536 (OpenAI compatible) OR we change the DB column

# Use GPU if available, otherwise CPU
device = "cuda" if os.getenv("CUDA_VISIBLE_DEVICES") else "cpu"
model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
print(f"Loading model: {model_name} on {device}...", flush=True)
try:
    model = SentenceTransformer(model_name, device=device)
    test = model.encode(["test"], show_progress_bar=False)
    print(f"Model dim: {test.shape[1]}", flush=True)
except Exception as e:
    print(f"Failed to load model: {e}", flush=True)
    raise

# Update DB vector column if needed
conn = psycopg2.connect(**DB_CONFIG)
conn.autocommit = True
cur = conn.cursor()

dim = test.shape[1]
if dim != 1536:
    print(f"Updating vector dimension from 1536 to {dim}...")
    # Drop old index, alter column, recreate index
    cur.execute("DROP INDEX IF EXISTS idx_law_chunks_embedding;")
    cur.execute("DROP INDEX IF EXISTS idx_company_chunks_embedding;")
    cur.execute(f"ALTER TABLE law_chunks ALTER COLUMN embedding TYPE vector({dim});")
    # company_chunks may not exist in this environment
    cur.execute("SELECT to_regclass('public.company_chunks')")
    if cur.fetchone()[0]:
        cur.execute(f"ALTER TABLE company_chunks ALTER COLUMN embedding TYPE vector({dim});")
        cur.execute("CREATE INDEX idx_company_chunks_embedding ON company_chunks USING hnsw (embedding vector_cosine_ops);")
    cur.execute("CREATE INDEX idx_law_chunks_embedding ON law_chunks USING hnsw (embedding vector_cosine_ops);")
    print(f"  ✅ Updated to {dim} dimensions")

# Get chunks without embeddings
cur.execute("SELECT COUNT(*) FROM law_chunks WHERE embedding IS NULL")
total = cur.fetchone()[0]
print(f"\n📊 Chunks to embed: {total}")

BATCH_SIZE = 256
offset = 0
embedded = 0
start_time = time.time()

while offset < total:
    cur.execute("""
        SELECT id, content FROM law_chunks 
        WHERE embedding IS NULL 
        ORDER BY id 
        LIMIT %s
    """, (BATCH_SIZE,))
    rows = cur.fetchall()
    if not rows:
        break
    
    ids = [r[0] for r in rows]
    texts = [r[1][:2000] for r in rows]  # Limit text length
    
    # Generate embeddings
    embeddings = model.encode(texts, batch_size=64, show_progress_bar=False, normalize_embeddings=True)
    
    # Update DB
    for chunk_id, emb in zip(ids, embeddings):
        cur.execute(
            "UPDATE law_chunks SET embedding = %s WHERE id = %s",
            (emb.tolist(), str(chunk_id))
        )
    
    embedded += len(rows)
    elapsed = time.time() - start_time
    rate = embedded / elapsed
    remaining = (total - embedded) / rate if rate > 0 else 0
    
    if embedded % 1024 == 0 or embedded == total:
        print(f"  📊 {embedded}/{total} ({embedded*100//total}%) | {rate:.0f} chunks/s | ETA: {remaining:.0f}s")
    
    offset += BATCH_SIZE

cur.execute("SELECT COUNT(*) FROM law_chunks WHERE embedding IS NOT NULL")
final = cur.fetchone()[0]
print(f"\n🏆 DONE! {final} chunks with embeddings")
print(f"⏱️ Total time: {time.time()-start_time:.0f}s")

cur.close()
conn.close()
