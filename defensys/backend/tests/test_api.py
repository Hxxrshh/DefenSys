import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.main import app, get_db
from api.database import Base
import os
import uuid
import sys



SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
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

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown_db():
    # Setup: create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown: drop tables and close connections
    engine.dispose()
    try:
        os.remove("./test.db")
    except (PermissionError, FileNotFoundError):
        pass  # Ignore if file is locked or doesn't exist

def test_create_project():
    unique_repo = f"https://github.com/test/project-{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/api/projects/",
        json={"name": "Test Project", "repository_url": unique_repo},
    )
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["repository_url"] == unique_repo
    assert "id" in data

def test_read_projects():
    response = client.get("/api/projects/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_start_scan():
    unique_repo = f"https://github.com/test/project-{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/api/scan",
        json={"repository_url": unique_repo, "scan_types": ["sast"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Scan started in the background"
    assert "scan_id" in data
