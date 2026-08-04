from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.vector_store import vector_store
from app.schemas.research import KnowledgeSearchRequest

router = APIRouter(prefix="/knowledge", tags=["Reusable Knowledge Base"])

@router.post("/search")
def search_knowledge_base(req: KnowledgeSearchRequest):
    """
    Queries ChromaDB vector store across all past enterprise research sessions.
    """
    results = vector_store.query_similar(query=req.query, n_results=req.top_k)
    
    formatted = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0] if "distances" in results else [0.0]*len(docs)
    
    for idx in range(len(docs)):
        formatted.append({
            "chunk_text": docs[idx],
            "metadata": metas[idx] if idx < len(metas) else {},
            "similarity_score": round(1.0 - float(distances[idx]), 3) if idx < len(distances) else 0.95
        })
        
    return {
        "query": req.query,
        "total_results": len(formatted),
        "matches": formatted
    }
