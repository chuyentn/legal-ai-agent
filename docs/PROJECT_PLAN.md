# Legal AI Agent — Project Plan

## Product Name: **LegalAI.vn** (tạm)

## MVP Scope (8-10 weeks)

### Sprint 1: Foundation (Week 1-2)
- [x] Architecture design
- [x] Database schema design
- [ ] Supabase project setup + run migration
- [ ] FastAPI project scaffold
- [ ] Auth system (API key generation + validation)
- [ ] Basic project structure + CI/CD

### Sprint 2: Law Data Pipeline (Week 3-4)
- [ ] Crawl Bộ luật Lao động 2019 from thuvienphapluat.vn
- [ ] Law parser — extract articles, clauses, points
- [ ] Chunking strategy implementation
- [ ] Embedding pipeline (BGE-M3 or OpenAI)
- [ ] Load into Supabase pgvector
- [ ] Crawl 5 key supporting Nghị định / Thông tư

### Sprint 3: RAG + Legal Q&A Agent (Week 5-6)
- [ ] Hybrid search implementation (semantic + keyword)
- [ ] Reranker integration
- [ ] Legal Q&A agent with Claude
- [ ] Citation verification system
- [ ] Hallucination guard
- [ ] API endpoint: POST /v1/legal/ask

### Sprint 4: Contract Review Agent (Week 7-8)
- [ ] Document upload + storage (Supabase Storage)
- [ ] PDF/DOCX text extraction
- [ ] Contract type classification
- [ ] Clause extraction + risk analysis
- [ ] Review report generation
- [ ] API endpoint: POST /v1/contracts/review

### Sprint 5: Polish + Launch (Week 9-10)
- [ ] Usage tracking + billing foundation
- [ ] Rate limiting
- [ ] Error handling + logging
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Simple web dashboard (Next.js)
- [ ] Deploy to production
- [ ] Beta test with HRVN

## Post-MVP
- Compliance audit agent
- Document drafter agent
- WebSocket realtime chat
- Embedding server (self-hosted BGE-M3)
- Mobile SDK
- More law domains (tax, real estate, IP)

## Tech Stack
- **Backend:** Python 3.11+, FastAPI, Celery
- **Database:** Supabase (Postgres + pgvector + Auth + Storage)
- **LLM:** Claude 3.5 Sonnet (Anthropic API)
- **Embedding:** OpenAI text-embedding-3-small (MVP) → BGE-M3 (scale) | tạm dùng sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (384-dim) cho data HF
- **OCR:** Surya (Vietnamese support)
- **Queue:** Redis
- **Frontend:** Next.js 14+ (dashboard)
- **Deploy:** Docker + Hetzner VPS
