# 🏛️ CO-FOUNDER DEPLOYMENT CHECKLIST
## Legal AI Agent: 60K → 240K+ Documents

**Timeline:** 1 day  
**Team:** Victor (Backend, 8h–12h) + Lucky (DevOps, 13h–17h)  
**Goal:** Scale legal document library with HuggingFace datasets

---

## ✅ PRE-DEPLOYMENT (Before 8h)

- [ ] **Lucky**: Database backup
  ```bash
  # Backup production DB to local file (est. 2-5 min)
  pg_dump postgres://postgres:$SUPABASE_DB_PASSWORD@$SUPABASE_DB_HOST:5432/postgres \
    > backup_pre_hf_$(date +%Y%m%d_%H%M%S).sql
  ```

- [ ] **Victor + Lucky**: Verify environment
  ```bash
  # Check .env has all required vars
  echo "SUPABASE_DB_HOST: $SUPABASE_DB_HOST"
  echo "SUPABASE_DB_PASSWORD: [set]"
  
  # Test connection
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
  cur.execute('SELECT version()')
  print(cur.fetchone()[0][:50])
  print('✅ DB Connection OK')
  "
  ```

- [ ] **Victor**: Create feature branch
  ```bash
  cd D:\AI-KILLS\legal-ai-agent-main
  git checkout main && git pull origin main
  git checkout -b feature/hf-data-integration
  git log --oneline -1  # Verify branch point
  ```

---

## 🟢 VICTOR — MORNING PIPELINE (8h–12h)

### 📦 Step V-01: Prepare Environment

- [ ] Activate venv
  ```bash
  .venv\Scripts\activate
  ```

- [ ] Install dependencies
  ```bash
  pip install -r requirements.txt
  pip list | grep -i "datasets\|beautifulsoup\|sentence-transform"
  # Should see: datasets-2.20.0, beautifulsoup4-4.12.0, sentence-transformers-3.x.x
  ```

- [ ] Verify database connection
  ```bash
  python -c "
  import psycopg2, os
  from dotenv import load_dotenv
  
  load_dotenv()
  
  conn = psycopg2.connect(
    host=os.getenv('SUPABASE_DB_HOST'),
    port=5432,
    dbname='postgres',
    user='postgres',
    password=os.getenv('SUPABASE_DB_PASSWORD'),
    sslmode='require'
  )
  
  cur = conn.cursor()
  
  # Check existing data
  cur.execute('SELECT COUNT(*) FROM law_documents')
  doc_count = cur.fetchone()[0]
  
  cur.execute('SELECT COUNT(*) FROM law_chunks')
  chunk_count = cur.fetchone()[0]
  
  print(f'Current state:')
  print(f'  law_documents: {doc_count:,}')
  print(f'  law_chunks: {chunk_count:,}')
  
  conn.close()
  "
  ```
  **Expected output:**
  ```
  Current state:
    law_documents: 60,000
    law_chunks: 117,000
  ```

### 🧪 Step V-02: Test Run (Small Dataset)

- [ ] Run with `--test` flag (500 rows each)
  ```bash
  python scripts/load_hf_datasets.py --test
  ```
  **Expected duration:** 3-5 minutes

- [ ] Expected output:
  ```
  ==================================================
    🚀 HuggingFace Data Loading - TEST MODE
  ==================================================
  
  ✅ Kết nối thành công!
  
  📥 [Dataset 1] th1nhng0/vietnamese-legal-documents
    Kết nối HuggingFace...
    Dataset loaded: 500 rows
    ✅ 500 văn bản nạp
    🎯 Hoàn thành: 500 docs | Bỏ qua: 0
  
  📥 [Dataset 2] thangvip/vietnamese-legal-qa
    ...
    🎯 Hoàn thành: 500+ Q&A
  
  📊 THỐNG KÊ SAU KHI NẠPDATA
    Tổng law_documents : 61,000+
    Từ HuggingFace     : 1,000+
    Tổng law_chunks    : 120,000+
  
  ⏱️  Tổng thời gian: X.X phút
  ✅ SUMMARY:
     Documents: 1000+ inserted
     Q&A Pairs: 500+ inserted
     Chunks: 10000+ created
  ```

- [ ] Verify test data in DB
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
  
  # Check HF data inserted
  cur.execute('''
    SELECT source_site, COUNT(*) FROM law_documents 
    GROUP BY source_site
  ''')
  
  print('Data by source:')
  for source, count in cur.fetchall():
    print(f'  {source}: {count:,}')
  
  # Sample HF document
  cur.execute('''
    SELECT title, source_site, LENGTH(full_text) as text_len
    FROM law_documents
    WHERE source_site = 'huggingface'
    LIMIT 1
  ''')
  
  row = cur.fetchone()
  if row:
    print(f'\\nSample HF doc:')
    print(f'  Title: {row[0][:60]}...')
    print(f'  Source: {row[1]}')
    print(f'  Text length: {row[2]:,} chars')
  
  conn.close()
  "
  ```

### 💾 Step V-03: Commit & Push Test

- [ ] Commit requirements.txt update
  ```bash
  git add requirements.txt
  git commit -m "deps: add HuggingFace datasets + beautifulsoup4 + sentence-transformers"
  ```

- [ ] Commit data pipeline script
  ```bash
  git add scripts/load_hf_datasets.py
  git commit -m "feat: add HuggingFace datasets integration (th1nhng0 + thangvip Q&A)"
  ```

- [ ] Push to feature branch
  ```bash
  git push origin feature/hf-data-integration
  ```

- [ ] Verify push
  ```bash
  git log --oneline origin/feature/hf-data-integration -5
  ```

### 🚀 Step V-04: Full Run (Lunch Time)

**⏰ Time:** ~12h (after smoke test verification)  
**Duration:** 45–90 minutes (can run in background)

- [ ] Launch full dataset load
  ```bash
  # Start in new terminal (can be left running)
  python scripts/load_hf_datasets.py --full
  ```

- [ ] Monitor in another terminal while eating
  ```bash
  # Open new PowerShell
  # Ctrl + Shift + ` to split terminal in VS Code
  
  # Every 10 min, check progress:
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
  
  # Overall stats
  cur.execute('SELECT COUNT(*) FROM law_documents')
  total_docs = cur.fetchone()[0]
  
  cur.execute('SELECT COUNT(*) FROM law_documents WHERE source_site = \"huggingface\"')
  hf_docs = cur.fetchone()[0]
  
  cur.execute('SELECT COUNT(*) FROM law_chunks')
  chunks = cur.fetchone()[0]
  
  print(f'Progress: {hf_docs:,} HF docs | {chunks:,} total chunks | {total_docs:,} total docs')
  
  conn.close()
  "
  ```

- [ ] Wait for completion message (should say "✅ SUMMARY" + timings)

---

## 🔵 LUCKY — AFTERNOON PIPELINE (13h–17h)

### 📥 Step L-01: Pull Victor's Branch

- [ ] Fetch latest code
  ```bash
  cd D:\AI-KILLS\legal-ai-agent-main
  git fetch origin
  git checkout feature/hf-data-integration
  git pull origin feature/hf-data-integration
  
  # Verify scripts present
  ls scripts/load_hf_datasets.py
  ```

### ⚙️ Step L-02: Generate Embeddings

**Goal:** Embed all law_chunks without embeddings (both old + new HF docs)

- [ ] Check how many chunks need embedding
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
  
  # Check embedding status
  cur.execute('SELECT COUNT(*) FROM law_chunks WHERE embedding IS NULL')
  no_embed = cur.fetchone()[0]
  
  cur.execute('SELECT COUNT(*) FROM law_chunks')
  total = cur.fetchone()[0]
  
  progress = (total - no_embed) / total * 100 if total > 0 else 0
  
  print(f'Embedding status:')
  print(f'  Total chunks: {total:,}')
  print(f'  Need embedding: {no_embed:,}')
  print(f'  Already embedded: {total - no_embed:,}')
  print(f'  Progress: {progress:.1f}%')
  
  conn.close()
  "
  ```
  **Expected:** Most chunks need embedding (HF data is fresh)

- [ ] Verify script present
  ```bash
  ls scripts/generate_embeddings.py
  ```

- [ ] (**If generating embeddings**) Install GPU support (optional but faster)
  ```bash
  # Check CUDA availability
  python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
  
  # If GPU available, might speed up embeddings 10x
  ```

- [ ] Run embeddings (can take 1+ hour for 500K+ chunks)
  ```bash
  # Background job - can monitor while working on other tasks
  python scripts/generate_embeddings.py
  
  # In separate terminal, monitor:
  # (repeat every 5-10 min)
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
  cur.execute('SELECT COUNT(*) FROM law_chunks WHERE embedding IS NULL')
  no_embed = cur.fetchone()[0]
  cur.execute('SELECT COUNT(*) FROM law_chunks')
  total = cur.fetchone()[0]
  progress = (total - no_embed) / total * 100 if total > 0 else 0
  
  print(f'[{os.popen(\"date +%H:%M:%S\").read().strip()}] Embedding progress: {progress:.1f}% ({total-no_embed:,}/{total:,})')
  
  conn.close()
  "
  ```

### 🔍 Step L-03: Index & Verify Data Quality

- [ ] Run indexing script (for full-text search)
  ```bash
  python scripts/index_chunks.py
  ```

- [ ] Verify data quality
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
  
  # Sample 5 HF documents
  cur.execute('''
    SELECT title, source_site, word_count
    FROM law_documents
    WHERE source_site = 'huggingface'
    ORDER BY created_at DESC
    LIMIT 5
  ''')
  
  print('=== 5 HF Documents (Latest) ===')
  for title, source, words in cur.fetchall():
    print(f'[{source}] {title[:60]}... ({words:,} words)')
  
  # Distribution by type
  cur.execute('''
    SELECT law_type, COUNT(*) as cnt
    FROM law_documents
    WHERE source_site = 'huggingface'
    GROUP BY law_type
    ORDER BY cnt DESC
  ''')
  
  print('\\n=== Document Types (HF) ===')
  for dtype, cnt in cur.fetchall():
    print(f'  {dtype:<15} : {cnt:>6,}')
  
  # Embedding status
  cur.execute('SELECT COUNT(*) FROM law_chunks WHERE embedding IS NULL')
  no_embed = cur.fetchone()[0]
  
  cur.execute('SELECT COUNT(*) FROM law_chunks')
  total = cur.fetchone()[0]
  
  print(f'\\n=== Embedding Status ===')
  print(f'  Total chunks: {total:,}')
  print(f'  Embedded: {total - no_embed:,}')
  print(f'  Missing: {no_embed:,}')
  
  conn.close()
  "
  ```

### 🚀 Step L-04: Deploy to Production

**⚠️ Before merging to main:**
- [ ] Verify all HF documents have chunks
- [ ] Verify all chunks have embeddings (or ready for embedding)
- [ ] Test search API works

- [ ] Merge feature branch
  ```bash
  git checkout main
  git merge feature/hf-data-integration --no-ff \
    -m "merge: HuggingFace datasets integration (240K+ docs)"
  ```

- [ ] Push to production
  ```bash
  git push origin main
  ```

- [ ] Restart backend (Render will auto-deploy on push)
  ```bash
  # If using Docker locally:
  docker compose pull
  docker compose up -d --no-deps --build app
  
  # Check logs
  docker compose logs -f app --tail=50
  ```

### 🧪 Step L-05: Smoke Test

- [ ] Test API is up
  ```bash
  curl https://legal-ai-agent.coach.io.vn/v1/health
  # Should return: {"status": "ok"}
  ```

- [ ] Test search endpoint
  ```bash
  curl -X POST https://legal-ai-agent.coach.io.vn/v1/search \
    -H "Content-Type: application/json" \
    -d '{
      "query": "thủ tục đăng ký kinh doanh",
      "limit": 3
    }' \
    | python -m json.tool
  ```
  **Should return:** Search results with HF documents included

- [ ] Check stats endpoint
  ```bash
  curl https://legal-ai-agent.coach.io.vn/v1/stats | python -m json.tool
  ```
  **Should show:** Updated document count (~240K+)

### 📊 Step L-06: Final Verification

- [ ] Query final database stats
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
  
  print('\\n' + '='*50)
  print('  📊 FINAL PRODUCTION STATS')
  print('='*50)
  
  # Total documents
  cur.execute('SELECT COUNT(*) FROM law_documents')
  total_docs = cur.fetchone()[0]
  
  # By source
  cur.execute('''
    SELECT source_site, COUNT(*) FROM law_documents
    GROUP BY source_site ORDER BY 2 DESC
  ''')
  
  print(f'\\nTotal law_documents: {total_docs:,}\\n')
  
  for source, cnt in cur.fetchall():
    pct = cnt / total_docs * 100
    print(f'  {source:<20} : {cnt:>8,} ({pct:>5.1f}%)')
  
  # Chunks
  cur.execute('SELECT COUNT(*) FROM law_chunks')
  total_chunks = cur.fetchone()[0]
  
  print(f'\\nTotal law_chunks: {total_chunks:,}')
  
  # Embedding coverage
  cur.execute('SELECT COUNT(*) FROM law_chunks WHERE embedding IS NOT NULL')
  embedded = cur.fetchone()[0]
  
  pct_embedded = embedded / total_chunks * 100 if total_chunks > 0 else 0
  print(f'  Embedded: {embedded:,} ({pct_embedded:.1f}%)')
  
  # Document types (HF)
  cur.execute('''
    SELECT law_type, COUNT(*) FROM law_documents 
    WHERE source_site = 'huggingface'
    GROUP BY law_type ORDER BY 2 DESC LIMIT 5
  ''')
  
  print('\\nTop HF Document Types:')
  for dtype, cnt in cur.fetchall():
    print(f'  {dtype:<15} : {cnt:>6,}')
  
  print('\\n' + '='*50)
  
  conn.close()
  "
  ```

---

## ✅ POST-DEPLOYMENT

- [ ] **Both**: Document any issues in #tech Slack channel
- [ ] **Lucky**: Verify monitoring alerts are working
- [ ] **Victor**: Code review + documentation
  ```bash
  # Add script docstring to README
  echo "
  ## Data Loading from HuggingFace
  
  To load additional HuggingFace datasets:
  
  \`\`\`bash
  python scripts/load_hf_datasets.py --full
  \`\`\`
  
  Supports:
  - th1nhng0/vietnamese-legal-documents (179K docs)
  - thangvip/vietnamese-legal-qa (9.7K Q&A pairs)
  
  " >> README.md
  ```

---

## 📍 EXPECTED RESULTS (EOD)

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| law_documents | 60,000 | ~240,000 | ✅ 240K+ |
| law_chunks | 117,000 | ~500,000+ | ✅ 500K+ |
| Q&A pairs | 0 | ~9,720+ | ✅ Added |
| Chunk embeddings | ~117K | Almost all | ✅ >99% |
| API response time | ~2-3s | <3s | ✅ Maintained |

---

## 🚨 TROUBLESHOOTING

### Problem: "Connection refused" to Supabase
**Solution:**
```bash
# Verify .env loaded
echo $SUPABASE_DB_HOST
echo $SUPABASE_DB_PASSWORD | wc -c  # Should be > 20 chars

# Test with psql
psql -h $SUPABASE_DB_HOST -U postgres -d postgres \
  -c "SELECT version();" --password
```

### Problem: "HuggingFace dataset not found"
**Solution:**
```bash
# HF CLI login may be cached
huggingface-cli login
# Or offline mode:
python -c "from datasets import load_dataset; load_dataset(..., download_mode='force_redownload')"
```

### Problem: "law_type not valid enum"
**Solution:**
- Check TYPE_MAP in load_hf_datasets.py
- Valid types: bo_luat, luat, nghi_dinh, quyet_dinh, thong_tu, phap_lenh, hien_phap, nghi_quyet

### Problem: Embedding generation very slow
**Solution:**
- Check GPU is available: `python -c "import torch; print(torch.cuda.is_available())"`
- Can run overnight if needed - process is idempotent
- Monitor with separate connection

### Problem: Database fills up
**Solution:**
```bash
# Check disk usage
df -h /data/

# Can pause and resume load_hf_datasets.py (pick up from last successful batch)
```

---

## 📞 ESCALATION

| Issue | Owner | Escalate To |
|-------|-------|-------------|
| DB connection | Lucky | AWS/Supabase support |
| Python errors | Victor | Tech lead |
| Deployment blocked | Lucky | DevOps team |
| Data quality issues | Victor | Data team |

---

**Last Updated:** April 5, 2026  
**Prepared by:** GitHub Copilot  
**For:** Victor + Lucky Co-founder Brief
