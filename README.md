# Enterprise AI Research Agent

> Production-Quality Multi-Stage Research & Evidence Engine (Modus Enterprise AI Build Challenge — Assignment 9)

## Overview

The **Enterprise AI Research Agent** is a structured, production-ready AI application designed to conduct enterprise research at scale. It replaces simple chatbot prompt wrappers with an autonomous 11-stage research pipeline:

1. **Define Research Questions**: Dynamic sub-question decomposition.
2. **Search Sources**: Multi-provider search via Tavily, SerpAPI, DuckDuckGo & HTML web scraper.
3. **Collect Information**: Full webpage content parsing and extraction.
4. **Store Raw Documents**: Structured storage in relational database (PostgreSQL / SQLite).
5. **Generate Embeddings**: Dense semantic vector encoding (`sentence-transformers/all-MiniLM-L6-v2`).
6. **Store Embeddings in ChromaDB**: Persistent vector knowledge archive with cosine similarity index.
7. **Retrieve Relevant Knowledge**: Context construction and similarity search.
8. **Send Context to Grok**: Grok xAI reasoning engine (`api.x.ai`) with local Ollama / fallback LLM support.
9. **Extract Findings & Evidence**: Fact extraction with confidence scoring.
10. **Detect Contradictions**: Conflict detector analyzing claim discrepancies, timeline shifts, and metric mismatches.
11. **Generate Conclusions & Citations**: Executive synthesis with traceable source footnotes.

---

## Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Lucide / FontAwesome Icons.
- **Backend**: FastAPI (Async Python 3.11+).
- **Database**: PostgreSQL (Production) / SQLite (Zero-config local mode) via SQLAlchemy ORM.
- **Vector Database**: ChromaDB / Vector Memory Index.
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` / Dense Feature Projection.
- **LLM Engine**: Primary: Grok (`xAI API`) | Fallback: Ollama (`llama3`) & Deterministic Reasoning Engine.
- **Authentication**: JWT Bearer Token Security.

---

## Quick Start (Local Run)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables (Optional)
Set your xAI Grok API key or search API keys in `.env` or shell environment:
```bash
export XAI_API_KEY="your-xai-grok-api-key"
export TAVILY_API_KEY="your-tavily-api-key"
```

### 3. Run FastAPI Application & Frontend Console
```bash
python -m uvicorn app.main:app --reload --port 8000
```
Open your browser at **[http://localhost:8000](http://localhost:8000)** to launch the interactive Enterprise Research Console.

---

## Quick Start (Docker Deployment)

```bash
docker-compose up --build
```
This boots:
- PostgreSQL database container
- FastAPI backend application container
- Persistent ChromaDB vector volume mount

---

## Automated Test Suite

Run unit and integration tests verifying API endpoints, research pipelines, and vector operations:

```bash
$env:PYTHONPATH="backend"; python -m pytest backend/tests
```
