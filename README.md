# SchemeSathi AI
### Agentic RAG-Based Government Scheme & Benefits Navigator

**SchemeSathi AI** is a serious full-stack AI platform built to help citizens discover, evaluate, and navigate Indian government schemes, scholarships, welfare programs, and financial benefits tailored to their demographic situation.

---

## 🔗 Deployment & Live Demo Links

- **Frontend Application**: `[Deployed Frontend URL Placeholder - e.g., https://schemesathi.vercel.app]`
- **Backend API Service**: `[Deployed Backend URL Placeholder - e.g., https://schemesathi-backend.onrender.com]`
- **GitHub Repository**: `[GitHub Repository URL Placeholder - e.g., https://github.com/user/schemesathi-ai]`

---

## 📌 Problem Statement

Navigating Indian government welfare programs and scholarships is often overwhelming due to fragmented information across central and state portals, complex eligibility rules, and stringent document requirements. Citizens frequently miss out on entitled benefits because they lack a unified tool that evaluates their profile against verified policy guidelines.

**SchemeSathi AI** solves this problem by combining:
1. **Vector RAG (Retrieval-Augmented Generation)** over vectorized official policy guidelines.
2. **LangGraph Function-Calling Agent** that dynamically executes specialized tools for search, eligibility checking, scheme comparison, and document checklist generation.
3. **Strict Non-Definitive Eligibility Reasoning** enforcing clear disclaimers that final eligibility rests with competent government authorities.

---

## 🌟 Key Features

1. **Landing / Home Page**: Clear project overview, hero AI search box, sector exploration pills, RAG architecture walkthrough, and official government disclaimers.
2. **AI Navigator Chat**: Interactive agentic chat interface powered by **LangGraph** tools, vector RAG grounding in official guidelines, grounded source citations, and attached scheme cards.
3. **Scheme Explorer**: Full scheme directory with filters for search keywords, categories, and state domiciles.
4. **Scheme Details**: In-depth view featuring overview summaries, eligibility criteria, financial benefits, mandatory documents, and step-by-step application steps.
5. **Compare Schemes**: Interactive matrix table comparing multiple schemes side by side across eligibility, benefits, income caps, documents, and application processes.
6. **My Saved Schemes**: Bookmarked schemes for quick citizen access and tracking.
7. **Document Checklist**: Interactive document readiness tracker with status toggles (*Available*, *Missing*, *Not Applicable*) and progress percentage indicators.
8. **Admin Knowledge Base**: Portal for uploading TXT and PDF guidelines, running text extraction, chunking, vector embedding generation, and managing Qdrant vector database indexes.

---

## 🛠️ Technology Stack

- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons, Axios, React Router v6
- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2
- **Vector Database**: Qdrant Vector DB (384-dimensional cosine similarity search)
- **Agent Framework**: LangGraph StateGraph Agent with multi-tool calling
- **Relational Database**: PostgreSQL (Production) / SQLite (Development) via SQLAlchemy 2.0 ORM
- **RAG & Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`), PyPDF, custom 600-char overlapping semantic chunker
- **LLM**: Google Gemini API / Grounded reasoning synthesis engine

---

## 🏗️ Architecture & Workflow

```text
User
 ↓
React Frontend (Vite + Tailwind)
 ↓
FastAPI Backend (/api/chat, /api/query, /api/schemes)
 ↓
LangGraph Agent
 ├── Tool 1: search_schemes()
 ├── Tool 2: search_knowledge_base() [RAG]
 ├── Tool 3: get_scheme_details()
 ├── Tool 4: check_eligibility()
 ├── Tool 5: get_required_documents()
 ├── Tool 6: get_application_process()
 ├── Tool 7: compare_schemes()
 ├── Tool 8: save_scheme()
 └── Tool 9: create_document_checklist()
       ↓
 ┌───────────────┬────────────────┐
 ↓               ↓                ↓
PostgreSQL    Qdrant Vector DB   LLM (Gemini API)
                 ↑
        Document Ingestion (PDF / TXT)
```

---

## 🔒 Production vs Development Configuration

- **Development Mode (`ENVIRONMENT=development`)**:
  - Allows fallback to local embedded SQLite (`sqlite:///./schemesathi.db`) and embedded local Qdrant vector storage for rapid local developer iteration.
- **Production Mode (`ENVIRONMENT=production`)**:
  - **Relational DB**: STRICTLY requires a live PostgreSQL instance (`DATABASE_URL=postgresql://...`). Fails loudly if PostgreSQL is unreachable or if SQLite is specified.
  - **Vector DB**: STRICTLY requires a live Qdrant instance (`QDRANT_URL=http://qdrant:6333`). Fails loudly if Qdrant is unreachable.
  - **CORS**: STRICTLY enforces origin domain validation parsed from `CORS_ORIGINS`.

---

## 📁 Repository Structure

```text
schemesathi-ai/
├── frontend/                  # React + Vite + Tailwind CSS Frontend
│   ├── src/
│   │   ├── components/        # Navbar, Footer, SchemeCard, SourceCitationCard, etc.
│   │   ├── pages/             # 8 Main Frontend Pages
│   │   ├── context/           # SchemeContext global state
│   │   └── services/          # REST API client (axios)
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── vercel.json            # Vercel SPA routing
│   └── Dockerfile
├── backend/                   # Python FastAPI Backend
│   ├── app/
│   │   ├── api/               # REST API Routers (chat, query, schemes, compare, etc.)
│   │   ├── agent/             # LangGraph Agent & 9 Tools
│   │   ├── services/          # RAG Engine, Qdrant Service, Embedding & LLM Services
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── seed_data.py           # Seeds database & indexes sample RAG documents
│   └── Dockerfile
├── data/
│   └── sample_documents/      # 7 Official Government Scheme Guidelines
├── docs/
│   └── ARCHITECTURE.md        # Technical architecture specifications
├── .env.example
├── .gitignore
├── docker-compose.yml         # Containerized local environment
├── render.yaml                # Render backend deployment manifest
└── README.md
```

---

## 🚀 Local Setup Instructions

### Step 1: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run database seeder and vector indexer
python seed_data.py

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

FastAPI server runs at `http://localhost:8000`. API Docs available at `http://localhost:8000/docs`. Health check: `http://localhost:8000/health`.

---

### Step 2: Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

Frontend runs at `http://localhost:3000`.

---

## 🐳 Docker Setup

To run the entire full-stack environment locally using Docker Compose:

```bash
# Create local .env from example
cp .env.example .env

# Build and start services
docker-compose up --build
```

---

## 🌐 Production Deployment Guide

### Deploying Backend (Render)

1. Connect your GitHub repository to **Render**.
2. Select **New Blueprint** and reference `render.yaml`, or create a **Web Service** pointing to the `backend/` root directory.
3. Configure environment variables in Render Dashboard:
   - `ENVIRONMENT=production`
   - `DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<dbname>`
   - `QDRANT_URL=https://<your-qdrant-cluster-url>:6333`
   - `GEMINI_API_KEY=<your_gemini_api_key>`
   - `FRONTEND_URL=https://<your-frontend-domain>.vercel.app`
   - `CORS_ORIGINS=https://<your-frontend-domain>.vercel.app`

### Deploying Frontend (Vercel)

1. Import your repository into **Vercel**.
2. Set **Root Directory** to `frontend/`.
3. Set **Framework Preset** to `Vite`.
4. Add Environment Variable:
   - `VITE_API_BASE_URL=https://<your-render-backend-url>.onrender.com/api`
5. Click **Deploy**.

---

## 📜 Official Government Disclaimer

*SchemeSathi AI provides recommendations based on indexed official guidelines. Final eligibility, quota allocations, and benefit disbursements must always be verified directly with the official government authority or designated department.*
