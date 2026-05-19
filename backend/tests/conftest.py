import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app

# StaticPool: 모든 연결이 동일한 in-memory DB를 공유
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    def override_get_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# 편의 픽스처: 등록된 사용자 + 토큰
@pytest.fixture
def registered_user(client):
    client.post("/api/register", json={
        "email": "user@test.com",
        "nickname": "tester",
        "password": "pass1234",
    })
    resp = client.post("/api/login", json={
        "email": "user@test.com",
        "password": "pass1234",
    })
    token = resp.json()["access_token"]
    return {"email": "user@test.com", "nickname": "tester", "token": token}


@pytest.fixture
def auth_headers(registered_user):
    return {"Authorization": f"Bearer {registered_user['token']}"}
