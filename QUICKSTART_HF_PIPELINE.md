# 🚀 QUICK START: HuggingFace Data Pipeline

## For Victor (Morning: 8h–12h)

```bash
# 1. Setup
cd D:\AI-KILLS\legal-ai-agent-main
git checkout main && git pull
git checkout -b feature/hf-data-integration
.venv\Scripts\activate

# 2. Install deps
pip install -r requirements.txt

# 3. Test run (5 min)
python scripts/load_hf_datasets.py --test

# 4. If OK, commit
git add requirements.txt scripts/load_hf_datasets.py
git commit -m "feat: add HuggingFace datasets integration"
git push origin feature/hf-data-integration

# 5. Start full run (~45-90 min) at lunch
python scripts/load_hf_datasets.py --full
```

**Victor: Monitor in separate terminal**
```bash
python -c "
import psycopg2, os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(
  host=os.getenv('SUPABASE_DB_HOST'), port=5432,
  dbname='postgres', user='postgres',
  password=os.getenv('SUPABASE_DB_PASSWORD'), sslmode='require'
)

cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM law_documents WHERE source_site = \"huggingface\"')
hf_count = cur.fetchone()[0]
cur.execute('SELECT COUNT(*) FROM law_chunks')
chunks = cur.fetchone()[0]

print(f'HF docs: {hf_count:,} | Total chunks: {chunks:,}')
conn.close()
"
```

---

## For Lucky (Afternoon: 13h–17h)

```bash
# 1. Get Victor's code
git fetch origin
git checkout feature/hf-data-integration
.venv\Scripts\activate

# 2. Generate embeddings (~1 hour)
python scripts/generate_embeddings.py

# 3. Index
python scripts/index_chunks.py

# 4. Verify
python scripts/index_chunks.py  # Check stats

# 5. Deploy
git checkout main
git merge feature/hf-data-integration
git push origin main

# 6. Test API
curl https://legal-ai-agent.coach.io.vn/v1/health
curl -X POST https://legal-ai-agent.coach.io.vn/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "luật lao động", "limit": 3}'
```

---

## Expected Timings

| Step | Owner | Time | Notes |
|------|-------|------|-------|
| Setup + test | Victor | 10 min | Fast feedback |
| Full load | Victor | 45-90 min | Can run in background |
| Embeddings | Lucky | 1-2 hours | Monitor progress |
| Deploy + test | Lucky | 15 min | Auto-deploys on main push |
| **Total** | **Team** | **~3 hours** | Can overlap |

---

## Key Numbers (Target)

- **law_documents:** 60K → 240K+ ✅
- **law_chunks:** 117K → 500K+ ✅
- **HF Datasets:** 0 → 2 sources ✅
  - th1nhng0/vietnamese-legal-documents: 179K+ docs
  - thangvip/vietnamese-legal-qa: 9.7K Q&A pairs

---

## Ping Points (Keep in Sync!)

1. **Victor → 12h**: "Test OK! Starting full load"
2. **Victor → 12:30h**: "Full load started, running in background"
3. **Lucky → 13h**: "Morning batch complete?"
4. **Lucky → 15h**: "Embeddings 80% done"
5. **Lucky → 16h**: "Merging to main, deploying..."
6. **Lucky → 16:30h**: "✅ Live! Stats: [copy paste from final check]"

---

## Emergency Stop

If something goes wrong:

```bash
# Stop running script: Ctrl+C

# Rollback DB (Lucky restores backup):
psql postgres://postgres:$PASS@$HOST:5432/postgres \
  < backup_pre_hf_*.sql

# Rollback code:
git revert HEAD
git push origin main
```

---

Good luck! Let's scale this thing! 🚀
