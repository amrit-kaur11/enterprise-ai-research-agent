from typing import List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class StartResearchRequest(BaseModel):
    topic: str = Field(..., description="Enterprise research topic or question", example="How is AI transforming retail operations?")

class ResearchQuestionSchema(BaseModel):
    id: int
    question: str
    category: str

    class Config:
        from_attributes = True

class SourceDocumentSchema(BaseModel):
    id: str
    title: str
    url: str
    domain: Optional[str] = None
    publication_date: Optional[str] = None
    content_snippet: Optional[str] = None
    credibility_score: float = 0.85

    class Config:
        from_attributes = True

class ExtractedEvidenceSchema(BaseModel):
    id: str
    claim: str
    category: Optional[str] = None
    confidence_score: float = 0.90
    publication_info: Optional[str] = None
    source_id: Optional[str] = None

    class Config:
        from_attributes = True

class FindingSchema(BaseModel):
    id: str
    category: str
    title: str
    summary: str
    impact_level: str
    supporting_source_ids: List[str] = []

    class Config:
        from_attributes = True

class ContradictionSchema(BaseModel):
    id: str
    topic: str
    claim_a: str
    source_a_title: Optional[str] = None
    source_a_url: Optional[str] = None
    claim_b: str
    source_b_title: Optional[str] = None
    source_b_url: Optional[str] = None
    contradiction_type: Optional[str] = None
    analysis: str
    resolution: Optional[str] = None

    class Config:
        from_attributes = True

class TraceableCitationSchema(BaseModel):
    source: str
    url: str
    publication_date: str
    claim: str
    confidence_score: float

class ConclusionSchema(BaseModel):
    id: str
    executive_summary: str
    key_findings_summary: str
    strategic_recommendations: List[str] = []
    traceable_citations: List[TraceableCitationSchema] = []

    class Config:
        from_attributes = True

class ResearchSessionDetailSchema(BaseModel):
    id: str
    topic: str
    status: str
    progress: int
    current_step: str
    error_message: Optional[str] = None
    created_at: datetime
    questions: List[ResearchQuestionSchema] = []
    sources: List[SourceDocumentSchema] = []
    evidences: List[ExtractedEvidenceSchema] = []
    findings: List[FindingSchema] = []
    contradictions: List[ContradictionSchema] = []
    conclusion: Optional[ConclusionSchema] = None

    class Config:
        from_attributes = True

class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: int = 5
