import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.vector_store import vector_store

# Setup in-memory test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_research.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200

def test_start_research_session():
    payload = {"topic": "How is AI transforming retail operations?"}
    response = client.post("/api/research/start", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "How is AI transforming retail operations?"
    assert data["status"] in ["QUEUED", "DEFINING_QUESTIONS", "COLLECTING_SOURCES", "COMPLETED"]
    assert "id" in data

def test_list_sessions():
    response = client.get("/api/research/sessions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_vector_store_add_and_query():
    docs = ["AI driven supply chain optimization reduces inventory costs by 25%."]
    metas = [{"session_id": "test-123", "title": "Supply Chain AI"}]
    ids = ["test-doc-1"]
    
    vector_store.add_documents(docs, metas, ids)
    res = vector_store.query_similar("supply chain cost reduction", n_results=1)
    assert len(res["documents"][0]) > 0
    assert "supply chain" in res["documents"][0][0].lower()
