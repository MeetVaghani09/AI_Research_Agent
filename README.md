# AI Research Agent

A hybrid RAG + live web search research assistant. A LangGraph agent decides,
per question, whether to answer from your uploaded PDFs, from live web
search, or both — then returns a synthesized answer with cited sources.

- **Backend:** FastAPI + LangGraph + Qdrant + DeepSeek + Tavily + Redis
- **Frontend:** React (Create React App)

## Architecture

```
┌─────────────────┐        HTTP (axios)        ┌──────────────────────┐
│  React frontend  │ ───────────────────────── │   FastAPI backend     │
│  localhost:3000  │  /api/research, /upload,   │   localhost:8000      │
└─────────────────┘  /api/status, /clear/{id}  └──────────────────────┘
                                                          │
                                    ┌─────────────────────┼─────────────────────┐
                                    ▼                     ▼                     ▼
                              ┌──────────┐          ┌──────────┐          ┌──────────┐
                              │  Qdrant  │          │ DeepSeek │          │  Tavily  │
                              │ (vectors)│          │  (LLM)   │          │(web search)│
                              └──────────┘          └──────────┘          └──────────┘
                                    │
                                    ▼
                              ┌──────────┐
                              │  Redis   │
                              │ (memory) │  optional — falls back to in-memory
                              └──────────┘
```

## Project structure

```
AI Research Agent/
├── app/                        # FastAPI backend
│   ├── main.py                 # App entrypoint, CORS config, router mounting
│   ├── config.py                # Pydantic settings (.env loader)
│   ├── llm.py                   # DeepSeek client (ChatOpenAI-compatible)
│   ├── api/
│   │   └── routes/
│   │       └── research.py     # /research, /upload, /clear/{session_id}
│   ├── graph/                   # LangGraph state machine (router → retrieve/search → answer)
│   ├── rag/                     # Qdrant vector store, embeddings, PDF ingestion, retriever
│   ├── memory/                  # Redis / in-memory chat history
│   ├── prompts/                 # Router + answer prompt templates
│   ├── tools/                   # Tavily web search tool
│   ├── models/                  # Pydantic request/response schemas
│   └── evaluation/              # LangSmith evaluation scripts
├── frontend/                    # React app (Create React App)
│   ├── src/
│   │   ├── App.js
│   │   ├── components/
│   │   │   ├── Chat.js
│   │   │   ├── InputArea.js
│   │   │   ├── Message.js
│   │   │   ├── Sidebar.js
│   │   │   └── StatusIndicator.js
│   │   └── services/
│   │       └── api.js          # Axios client — talks to http://localhost:8000
│   └── package.json
├── data/                        # Uploaded PDFs (gitignored, created at runtime)
├── .env.example
└── requirements.txt
```

## Prerequisites

- Python 3.12+
- Node.js 18+ and npm
- A running Qdrant instance — local (Docker) or [Qdrant Cloud](https://cloud.qdrant.io)
- API keys: [DeepSeek](https://platform.deepseek.com), [Tavily](https://tavily.com)
- (Optional) Redis — for persistent chat history across restarts

## 1. Backend setup

```powershell
cd "AI Research Agent"
uv venv .venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your keys:

```powershell
Copy-Item .env.example .env
```

Required in `.env`:

| Variable | Notes |
|---|---|
| `DEEPSEEK_API_KEY` | required |
| `DEEPSEEK_MODEL` | defaults to `deepseek-v4-flash` |
| `TAVILY_API_KEY` | required for web search routes |
| `QDRANT_URL` | `http://localhost:6333` for local, or your Qdrant Cloud cluster URL |
| `QDRANT_API_KEY` | required for Qdrant Cloud, leave empty for local/no-auth |
| `REDIS_URL` | optional — leave empty to use in-memory chat history |

If using **Qdrant Cloud**, no local Qdrant setup is needed. If running **local Qdrant**:

```powershell
docker run -d --name qdrant -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest
```

### Run the backend

```powershell
uvicorn app.main:app --reload --port 8000
```

The API is now live at `http://localhost:8000`. Check it's up:

```powershell
curl http://localhost:8000/api/status
```

Interactive API docs (Swagger UI) are auto-generated at `http://localhost:8000/docs`.

## 2. Frontend setup

In a **separate terminal**:

```powershell
cd "AI Research Agent\frontend"
npm install
npm start
```

This opens `http://localhost:3000` automatically. The React app is pre-configured
(`src/services/api.js`) to call the backend at `http://localhost:8000` — no
extra frontend `.env` needed as long as the backend is running on that port.

## API reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/status` | Health check for DeepSeek/Tavily/Qdrant/Redis |
| `POST` | `/api/research` | Form fields: `session_id`, `question`. Returns `{ answer, route, sources }` |
| `POST` | `/api/upload` | Form fields: `session_id`, `file` (PDF, max 25MB). Ingests into Qdrant, scoped to that session |
| `DELETE` | `/api/clear/{session_id}` | Deletes all indexed document chunks for that session |

Routing (`route` in the response) is one of:
- `document` — answered from your uploaded PDF(s)
- `web` — answered from live Tavily search
- `both` — combined document + web context

## How retrieval works

- Each uploaded PDF is chunked and embedded (`sentence-transformers/all-MiniLM-L6-v2`, 384-dim) and stored in Qdrant tagged with `session_id`.
- Retrieval is **strictly scoped to the current session** — a document uploaded in one session never appears in another session's answers.
- Qdrant Cloud requires a payload index on filtered fields (`metadata.session_id`). This is created automatically on first run — see `app/rag/vector_store.py`.

## Troubleshooting

**CORS errors in the browser console**
Confirm the backend is running on port 8000 and the frontend on 3000/3001 — these are the only origins allowed in `app/main.py`'s `CORSMiddleware`. If you run the frontend on a different port, add it there.

**`Bad request: Index required but not found for "metadata.session_id"`**
Qdrant Cloud enforces payload indexes for filtered fields. Ensure `app/rag/vector_store.py` creates the keyword index on `metadata.session_id` at startup (already handled — restart the backend if you still see this after pulling the latest code).

**DeepSeek API errors**
DeepSeek retired the legacy `deepseek-chat`/`deepseek-reasoner` model aliases. Confirm `DEEPSEEK_MODEL` in `.env` is set to a currently active model id.

**`transformers` import warnings on startup** (e.g. `torchvision`-related errors from vision model submodules like ViTPose/YOLOS)
Harmless — these come from `transformers`' lazy module loading being introspected on startup and don't affect the text-embedding pipeline this project actually uses. Install `torchvision` (CPU build) if you want to silence them entirely:
```powershell
uv pip install torchvision --index-url https://download.pytorch.org/whl/cpu
```

## Tech stack

| Layer | Technology |
|---|---|
| LLM | DeepSeek API |
| Agent framework | LangGraph, LangChain |
| Vector DB | Qdrant |
| Embeddings | HuggingFace sentence-transformers (MiniLM-L6-v2) |
| Web search | Tavily |
| Memory | Redis (optional, in-memory fallback) |
| Observability | LangSmith |
| Backend | FastAPI, Pydantic |
| Frontend | React (Create React App), Axios |
| PDF processing | pypdf |
