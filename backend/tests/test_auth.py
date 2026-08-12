import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash, verify_password

# In-memory test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
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

def test_password_hashing_and_verification_normal():
    password = "StandardSecurePassword123!"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert hashed.startswith("$2b$")
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False
    assert verify_password("", hashed) is False

def test_password_hashing_and_verification_long_password():
    # Password exceeding 72 bytes (120 characters)
    long_password = "SuperLongEnterprisePasswordExcreedingBcryptLimit_" + ("a" * 80) + "_2026!"
    assert len(long_password.encode('utf-8')) > 72

    hashed = get_password_hash(long_password)
    
    assert hashed != long_password
    assert hashed.startswith("$2b$")
    assert verify_password(long_password, hashed) is True
    assert verify_password(long_password[:-1], hashed) is False  # slight modification fails
    assert verify_password("ShortPassword", hashed) is False

def test_user_registration_and_login_flow():
    email = "test.user@enterprise.ai"
    password = "EnterpriseUserPass2026!"

    # 1. Register User
    reg_response = client.post(
        "/api/auth/register",
        json={"email": email, "full_name": "Enterprise Tester", "password": password}
    )
    assert reg_response.status_code == 200
    reg_data = reg_response.json()
    assert reg_data["email"] == email
    assert "id" in reg_data

    # 2. Duplicate Registration Fail
    dup_response = client.post(
        "/api/auth/register",
        json={"email": email, "full_name": "Enterprise Tester", "password": password}
    )
    assert dup_response.status_code == 400

    # 3. Successful Login
    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password}
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"

    # 4. Invalid Password Login Fail
    invalid_login = client.post(
        "/api/auth/login",
        json={"email": email, "password": "WrongPassword!"}
    )
    assert invalid_login.status_code == 401

def test_user_registration_long_password():
    email = "longpass.user@enterprise.ai"
    long_password = "X" * 150  # 150 char password

    reg_response = client.post(
        "/api/auth/register",
        json={"email": email, "full_name": "Long Password User", "password": long_password}
    )
    assert reg_response.status_code == 200

    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": long_password}
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
