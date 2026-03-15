# Legal AI Agent 🏛️

AI-powered legal assistant for Vietnamese companies. Cloud API platform providing contract review, legal Q&A, compliance checking, and document drafting.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full system design.

## Quick Start

```bash
# Clone
git clone <repo-url>
cd legal-ai-agent

# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your Supabase + Anthropic keys

# Run
uvicorn src.api.main:app --reload --port 8000
```

## API

```bash
# Legal Q&A
curl -X POST http://localhost:8000/v1/legal/ask \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "Nhân viên nghỉ thai sản được bao lâu?"}'

# Contract Review
curl -X POST http://localhost:8000/v1/contracts/review \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@contract.pdf"
```

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** Supabase (Postgres + pgvector)
- **LLM:** Claude (Anthropic)
- **Auth:** Supabase Auth + API Keys

## License

Proprietary — All rights reserved.
