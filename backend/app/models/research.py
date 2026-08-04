import uuid
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    topic = Column(String, nullable=False, index=True)
    status = Column(String, default="QUEUED")  # QUEUED, SEARCHING, COLLECTING, EMBEDDING, RETRIEVING, ANALYZING, COMPLETED, FAILED
    progress = Column(Integer, default=0)
    current_step = Column(String, default="Initialized")
    error_message = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    questions = relationship("ResearchQuestion", back_populates="session", cascade="all, delete-orphan")
    sources = relationship("SourceDocument", back_populates="session", cascade="all, delete-orphan")
    evidences = relationship("ExtractedEvidence", back_populates="session", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="session", cascade="all, delete-orphan")
    contradictions = relationship("Contradiction", back_populates="session", cascade="all, delete-orphan")
    conclusion = relationship("Conclusion", back_populates="session", uselist=False, cascade="all, delete-orphan")

class ResearchQuestion(Base):
    __tablename__ = "research_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    category = Column(String, default="general")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ResearchSession", back_populates="questions")

class SourceDocument(Base):
    __tablename__ = "source_documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    url = Column(Text, nullable=False)
    domain = Column(String, nullable=True)
    publication_date = Column(String, nullable=True)
    content_snippet = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)
    credibility_score = Column(Float, default=0.85)
    chroma_doc_ids = Column(JSON, default=list)  # list of chunk UUIDs in ChromaDB
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ResearchSession", back_populates="sources")

class ExtractedEvidence(Base):
    __tablename__ = "extracted_evidence"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(String, ForeignKey("source_documents.id", ondelete="CASCADE"), nullable=True)
    claim = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    confidence_score = Column(Float, default=0.90)
    publication_info = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ResearchSession", back_populates="evidences")

class Finding(Base):
    __tablename__ = "findings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False)
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    impact_level = Column(String, default="HIGH")  # HIGH, MEDIUM, LOW
    supporting_source_ids = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ResearchSession", back_populates="findings")

class Contradiction(Base):
    __tablename__ = "contradictions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String, nullable=False)
    claim_a = Column(Text, nullable=False)
    source_a_title = Column(String, nullable=True)
    source_a_url = Column(Text, nullable=True)
    claim_b = Column(Text, nullable=False)
    source_b_title = Column(String, nullable=True)
    source_b_url = Column(Text, nullable=True)
    contradiction_type = Column(Text, nullable=True) # Direct Conflict, Timeline Divergence, Metric Mismatch
    analysis = Column(Text, nullable=False)
    resolution = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ResearchSession", back_populates="contradictions")

class Conclusion(Base):
    __tablename__ = "conclusions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    executive_summary = Column(Text, nullable=False)
    key_findings_summary = Column(Text, nullable=False)
    strategic_recommendations = Column(JSON, default=list)
    traceable_citations = Column(JSON, default=list)  # [{source, url, date, claim, confidence}]
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ResearchSession", back_populates="conclusion")
