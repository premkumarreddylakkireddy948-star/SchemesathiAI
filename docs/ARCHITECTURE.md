# SchemeSathi AI Architecture Specification

## Overview
**SchemeSathi AI** is an intelligent full-stack agentic platform that assists Indian citizens in discovering, evaluating, and applying for relevant government schemes, scholarships, and welfare programs based on their demographic profile and socioeconomic parameters.

---

## 1. System Architecture

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

## 2. RAG Pipeline Specifications

The Retrieval-Augmented Generation (RAG) pipeline is structured as follows:

1. **Document Ingestion**: PDF / TXT document guidelines located in `data/sample_documents/`.
2. **Text Cleaning**: Strips whitespace, normalizes Unicode characters, removes header artifacts.
3. **Semantic Chunking**: 600-character overlapping chunks with 150-character overlap along sentence boundaries.
4. **Vector Embeddings**: 384-dimensional dense vectors generated via `SentenceTransformers` (`all-MiniLM-L6-v2`).
5. **Vector Storage**: Indexed into **Qdrant Vector DB** under collection `government_schemes`.
6. **Payload Metadata**:
   - `scheme_name`
   - `document_name`
   - `source_url`
   - `page_number`
   - `chunk_index`
   - `category`
   - `update_date`
7. **Semantic Retrieval**: Cosine similarity top-k search with metadata payload filtering.
8. **LLM Synthesis**: Grounded response synthesis enforcing eligibility disclaimers.

---

## 3. LangGraph Agent Architecture

The agent is designed as a StateGraph:

- **State**: `query`, `user_context`, `tool_calls`, `retrieved_data`, `final_response`, `sources`, `scheme_ids`.
- **Node 1 (`analyze_and_route`)**: Analyzes intent and selects necessary tools dynamically.
- **Node 2 (`execute_tools`)**: Executes RAG search, scheme database queries, eligibility evaluations, and checklist generators.
- **Node 3 (`generate_final_response`)**: Synthesizes a grounded response with source citations. Chain-of-thought internal reasoning is hidden from the final user response.

---

## 4. Strict Eligibility Policy

- **Mandatory Policy**: The system NEVER states *"You are eligible."*
- **Allowed Directive**: *"Based on the information provided, this scheme appears potentially relevant because..."*
- **Disclaimer**: Final eligibility, quota allocations, and benefit sanctioning must always be verified with official government authorities.

---

## 5. PostgreSQL Database Schema

- `users`: User identity records.
- `user_profiles`: Domicile state, category, annual income, occupation, age.
- `schemes`: Structured scheme guidelines, eligibility rules, benefits, income limits, portal URLs.
- `documents`: Knowledge base document metadata and chunk counts.
- `conversations`: Chat sessions.
- `messages`: User & Agent chat messages with JSON source citations.
- `saved_schemes`: Citizen bookmarks and notes.
- `checklists`: Interactive document checklists per scheme.
- `checklist_items`: Individual document status (Available, Missing, Not Applicable) and notes.
