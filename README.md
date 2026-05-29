# AI Hospital — Hygeia Assistant

A multi-agent RAG chatbot for Hygeia Hospital Tirana. Answers questions about doctors, departments, billing packages, and reception in Albanian and English.

## Architecture

```
User → React/Vite (port 5173)
         ↓ POST /ask/stream (SSE)
       FastAPI (port 8000)
         ↓ keyword routing
       Agent (reception | doctors | departments | billing)
         ↓ FAISS vector search over department PDFs
       OpenAI GPT-4o-mini
         ↑ streamed tokens back to browser
```

## Quick Start

### 1. Backend

```bash
cd Backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your OpenAI API key
copy .env.example .env
# then open .env and paste your key: OPENAI_API_KEY=sk-...

# Run the server
uvicorn app.main:app --reload --port 8000
```

Backend will be at: http://127.0.0.1:8000

### 2. Frontend

```bash
cd Frontend
npm install
npm run dev
```

Frontend will be at: http://localhost:5173

Open http://localhost:5173 and start chatting.

---

## Features

- **4 specialized agents** — reception, doctors, departments, billing
- **FAISS vector search** — retrieves relevant chunks from hospital PDFs
- **Streaming responses** — tokens appear as they're generated (SSE)
- **Bilingual** — Albanian + English
- **Persistent chat** — history saved in localStorage
- **Source display** — shows which PDF the answer came from
- **Smalltalk handling** — greetings, thanks, goodbyes handled without hitting the LLM

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | — | Your OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | Model to use (e.g. `gpt-4o`) |

## Project Structure

```
Backend/
  app/
    agents/         # reception, doctors, departments, billing handlers
    api/routes.py   # /ask and /ask/stream endpoints
    core/config.py  # paths configuration
    rag/
      llm.py        # OpenAI calls (normal + streaming)
      retriever.py  # FAISS search
      ingest.py     # PDF → embeddings → FAISS index
    data/
      pdfs/         # Source PDFs for each department
      index/        # Pre-built FAISS indexes
  requirements.txt
  .env.example

Frontend/
  src/
    App.jsx         # Main chat UI with streaming
    api/chat.js     # askBackend + askBackendStream helpers
    App.css         # Styles
```

## Rebuilding Indexes

If you update the PDFs, rebuild the FAISS indexes:

```bash
cd Backend
python -m app.rag.ingest
```
