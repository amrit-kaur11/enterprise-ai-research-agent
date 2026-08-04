import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db, SessionLocal
from app.models.research import ResearchSession
from app.schemas.research import (
    StartResearchRequest, ResearchSessionDetailSchema
)
from app.services.pipeline import pipeline_orchestrator

router = APIRouter(prefix="/research", tags=["Enterprise Research Pipeline"])

async def run_pipeline_task(session_id: str):
    db = SessionLocal()
    try:
        await pipeline_orchestrator.execute_pipeline(session_id, db)
    finally:
        db.close()

@router.post("/start", response_model=ResearchSessionDetailSchema)
async def start_research(
    req: StartResearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    if not req.topic or len(req.topic.strip()) < 3:
        raise HTTPException(status_code=400, detail="Research topic must be a valid non-empty string.")

    # Create session record
    session = ResearchSession(
        topic=req.topic.strip(),
        status="QUEUED",
        progress=5,
        current_step="Research request accepted. Queuing background pipeline..."
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Launch pipeline background execution
    background_tasks.add_task(run_pipeline_task, session.id)

    return session

@router.get("/session/{session_id}", response_model=ResearchSessionDetailSchema)
def get_research_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Research session not found")
    return session

@router.get("/sessions", response_model=List[ResearchSessionDetailSchema])
def list_research_sessions(limit: int = 20, db: Session = Depends(get_db)):
    sessions = db.query(ResearchSession).order_by(ResearchSession.created_at.desc()).limit(limit).all()
    return sessions
