import pytest


REGISTER_URL   = "/api/register"
LOGIN_URL      = "/api/login"
ME_URL         = "/api/me"
SCORES_URL     = "/api/scores"
MY_SCORES_URL  = "/api/scores/my"
LEADERBOARD_URL = "/api/leaderboard"

USER_A = {"email": "a@test.com", "nickname": "alice", "password": "pass1234"}
USER_B = {"email": "b@test.com", "nickname": "bob",   "password": "pass5678"}


# ── helpers ───────────────────────────────────────────────────────────────────

def register_and_login(client, user=USER_A):
    client.post(REGISTER_URL, json=user)
    resp = client.post(LOGIN_URL, json={"email": user["email"], "password": user["password"]})
    return resp.json()["access_token"]

def headers(token):
    return {"Authorization": f"Bearer {token}"}

def submit_score(client, token, score=1000, lines=10, level=2):
    return client.post(SCORES_URL, json={"score": score, "lines": lines, "level": level}, headers=headers(token))


# ── POST /api/register ────────────────────────────────────────────────────────

class TestRegister:
    def test_success_returns_201(self, client):
        resp = client.post(REGISTER_URL, json=USER_A)
        assert resp.status_code == 201

    def test_duplicate_email_returns_400(self, client):
        client.post(REGISTER_URL, json=USER_A)
        resp = client.post(REGISTER_URL, json=USER_A)
        assert resp.status_code == 400

    def test_different_emails_can_register(self, client):
        assert client.post(REGISTER_URL, json=USER_A).status_code == 201
        assert client.post(REGISTER_URL, json=USER_B).status_code == 201

    def test_invalid_email_format_returns_422(self, client):
        resp = client.post(REGISTER_URL, json={"email": "not-an-email", "nickname": "x", "password": "pass1234"})
        assert resp.status_code == 422

    def test_short_password_returns_422(self, client):
        resp = client.post(REGISTER_URL, json={"email": "x@test.com", "nickname": "x", "password": "short"})
        assert resp.status_code == 422

    def test_empty_nickname_returns_422(self, client):
        resp = client.post(REGISTER_URL, json={"email": "x@test.com", "nickname": "   ", "password": "pass1234"})
        assert resp.status_code == 422


# ── POST /api/login ───────────────────────────────────────────────────────────

class TestLogin:
    def test_success_returns_token_and_nickname(self, client):
        client.post(REGISTER_URL, json=USER_A)
        resp = client.post(LOGIN_URL, json={"email": USER_A["email"], "password": USER_A["password"]})
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["nickname"] == USER_A["nickname"]
        assert body["token_type"] == "bearer"

    def test_wrong_password_returns_401(self, client):
        client.post(REGISTER_URL, json=USER_A)
        resp = client.post(LOGIN_URL, json={"email": USER_A["email"], "password": "wrongpassword"})
        assert resp.status_code == 401

    def test_unregistered_email_returns_401(self, client):
        resp = client.post(LOGIN_URL, json={"email": "nobody@test.com", "password": "pw"})
        assert resp.status_code == 401


# ── GET /api/me ───────────────────────────────────────────────────────────────

class TestMe:
    def test_returns_my_info(self, client):
        token = register_and_login(client, USER_A)
        resp = client.get(ME_URL, headers=headers(token))
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == USER_A["email"]
        assert body["nickname"] == USER_A["nickname"]

    def test_no_token_returns_401(self, client):
        resp = client.get(ME_URL)
        assert resp.status_code == 401

    def test_invalid_token_returns_401(self, client):
        resp = client.get(ME_URL, headers={"Authorization": "Bearer bad.token"})
        assert resp.status_code == 401


# ── POST /api/scores ──────────────────────────────────────────────────────────

class TestSubmitScore:
    def test_success_returns_201(self, client):
        token = register_and_login(client)
        resp = submit_score(client, token)
        assert resp.status_code == 201

    def test_no_token_returns_401(self, client):
        resp = client.post(SCORES_URL, json={"score": 100, "lines": 1, "level": 1})
        assert resp.status_code == 401

    def test_score_zero_is_allowed(self, client):
        token = register_and_login(client)
        resp = submit_score(client, token, score=0, lines=0, level=1)
        assert resp.status_code == 201


# ── GET /api/scores/my ────────────────────────────────────────────────────────

class TestMyScores:
    def test_returns_empty_list_initially(self, client):
        token = register_and_login(client)
        resp = client.get(MY_SCORES_URL, headers=headers(token))
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_submitted_scores(self, client):
        token = register_and_login(client)
        submit_score(client, token, score=500)
        submit_score(client, token, score=300)
        resp = client.get(MY_SCORES_URL, headers=headers(token))
        assert resp.status_code == 200
        scores = [s["score"] for s in resp.json()]
        assert 500 in scores
        assert 300 in scores

    def test_scores_ordered_by_desc(self, client):
        token = register_and_login(client)
        for s in [200, 800, 500]:
            submit_score(client, token, score=s)
        scores = [s["score"] for s in client.get(MY_SCORES_URL, headers=headers(token)).json()]
        assert scores == sorted(scores, reverse=True)

    def test_only_returns_my_scores(self, client):
        token_a = register_and_login(client, USER_A)
        token_b = register_and_login(client, USER_B)
        submit_score(client, token_a, score=9999)
        submit_score(client, token_b, score=1111)

        my_scores = client.get(MY_SCORES_URL, headers=headers(token_b)).json()
        assert len(my_scores) == 1
        assert my_scores[0]["score"] == 1111

    def test_no_token_returns_401(self, client):
        resp = client.get(MY_SCORES_URL)
        assert resp.status_code == 401


# ── GET /api/leaderboard ──────────────────────────────────────────────────────

class TestLeaderboard:
    def test_returns_empty_list_when_no_scores(self, client):
        resp = client.get(LEADERBOARD_URL)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_correct_fields(self, client):
        token = register_and_login(client)
        submit_score(client, token, score=1000, lines=10, level=2)
        entry = client.get(LEADERBOARD_URL).json()[0]
        assert "rank" in entry
        assert "nickname" in entry
        assert "score" in entry
        assert "lines" in entry
        assert "level" in entry
        assert "played_at" in entry

    def test_rank_starts_at_1(self, client):
        token = register_and_login(client)
        submit_score(client, token, score=100)
        entry = client.get(LEADERBOARD_URL).json()[0]
        assert entry["rank"] == 1

    def test_ordered_by_score_desc(self, client):
        token_a = register_and_login(client, USER_A)
        token_b = register_and_login(client, USER_B)
        submit_score(client, token_a, score=500)
        submit_score(client, token_b, score=1500)
        board = client.get(LEADERBOARD_URL).json()
        assert board[0]["score"] > board[1]["score"]
        assert board[0]["rank"] == 1
        assert board[1]["rank"] == 2

    def test_only_best_score_per_user(self, client):
        token = register_and_login(client)
        submit_score(client, token, score=300)
        submit_score(client, token, score=900)
        submit_score(client, token, score=600)
        board = client.get(LEADERBOARD_URL).json()
        # 같은 유저가 여러 번 제출해도 1개만 나와야 함
        assert len(board) == 1
        assert board[0]["score"] == 900

    def test_max_10_entries(self, client):
        # 11명 등록 후 점수 제출
        for i in range(11):
            u = {"email": f"u{i}@test.com", "nickname": f"user{i}", "password": "password123"}
            token = register_and_login(client, u)
            submit_score(client, token, score=(i + 1) * 100)
        board = client.get(LEADERBOARD_URL).json()
        assert len(board) == 10

    def test_no_auth_required(self, client):
        resp = client.get(LEADERBOARD_URL)
        assert resp.status_code == 200
