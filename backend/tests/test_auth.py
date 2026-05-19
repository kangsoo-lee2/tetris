import time
import pytest
from datetime import datetime, timedelta
from jose import jwt

from backend.auth import (
    hash_password,
    verify_password,
    create_token,
    SECRET_KEY,
    ALGORITHM,
)


class TestHashPassword:
    def test_hash_differs_from_plain(self):
        assert hash_password("secret") != "secret"

    def test_same_plain_produces_different_hashes(self):
        # bcrypt는 매번 다른 salt를 사용
        assert hash_password("secret") != hash_password("secret")


class TestVerifyPassword:
    def test_correct_password_returns_true(self):
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_wrong_password_returns_false(self):
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_empty_password_returns_false(self):
        hashed = hash_password("mypassword")
        assert verify_password("", hashed) is False


class TestCreateToken:
    def test_token_contains_correct_user_id(self):
        token = create_token(42)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "42"

    def test_token_has_expiry(self):
        token = create_token(1)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload

    def test_token_expiry_is_in_future(self):
        token = create_token(1)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["exp"] > time.time()


class TestGetCurrentUser:
    """get_current_user는 FastAPI 의존성이므로 API를 통해 검증."""

    def test_valid_token_allows_access(self, client):
        client.post("/api/register", json={"email": "a@b.com", "nickname": "alice", "password": "pw"})
        token = client.post("/api/login", json={"email": "a@b.com", "password": "pw"}).json()["access_token"]
        resp = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_no_token_returns_401(self, client):
        resp = client.get("/api/me")
        assert resp.status_code == 401

    def test_invalid_token_returns_401(self, client):
        resp = client.get("/api/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401

    def test_expired_token_returns_401(self, client):
        exp = datetime.utcnow() - timedelta(hours=1)
        expired = jwt.encode({"sub": "1", "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)
        resp = client.get("/api/me", headers={"Authorization": f"Bearer {expired}"})
        assert resp.status_code == 401

    def test_token_for_nonexistent_user_returns_401(self, client):
        token = create_token(99999)
        resp = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
