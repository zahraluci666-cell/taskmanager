"""
Integration tests for the FastAPI app using TestClient.
Overrides the DB dependency to use an isolated in-memory SQLite DB.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.api.main import app

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def auth_headers(client):
    client.post("/auth/register", json={"username": "alice", "password": "secret123"})
    resp = client.post("/auth/login", data={"username": "alice", "password": "secret123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_register_and_login(client):
    resp = client.post("/auth/register", json={"username": "bob", "password": "secret123"})
    assert resp.status_code == 201

    resp = client.post("/auth/login", data={"username": "bob", "password": "secret123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_create_and_list_task(client, auth_headers):
    resp = client.post("/tasks", json={"title": "Buy milk"}, headers=auth_headers)
    assert resp.status_code == 201
    task_id = resp.json()["id"]

    resp = client.get("/tasks", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == task_id


def test_task_requires_auth(client):
    resp = client.get("/tasks")
    assert resp.status_code == 401


def test_mark_done_and_delete(client, auth_headers):
    resp = client.post("/tasks", json={"title": "Ship it"}, headers=auth_headers)
    task_id = resp.json()["id"]

    resp = client.post(f"/tasks/{task_id}/done", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"

    resp = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 204

    resp = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 404
