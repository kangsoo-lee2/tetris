from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from .database import engine, get_db, Base
from .models import User, Score
from .schemas import (
    UserRegister, UserLogin, TokenResponse,
    ScoreSubmit, ScoreRecord, LeaderboardEntry,
)
from .auth import hash_password, verify_password, create_token, get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tetris API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/api/register", status_code=201)
def register(body: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다")
    user = User(
        email=body.email,
        nickname=body.nickname,
        hashed_pw=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    return {"message": "회원가입 완료"}


@app.post("/api/login", response_model=TokenResponse)
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_pw):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다")
    return TokenResponse(access_token=create_token(user.id), nickname=user.nickname)


@app.get("/api/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "nickname": user.nickname}


# ── Scores ────────────────────────────────────────────────────────────────────

@app.post("/api/scores", status_code=201)
def submit_score(
    body: ScoreSubmit,
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
):
    record = Score(
        user_id=user.id,
        score=body.score,
        lines=body.lines,
        level=body.level,
    )
    db.add(record)
    db.commit()
    return {"message": "기록 저장 완료"}


@app.get("/api/scores/my", response_model=list[ScoreRecord])
def my_scores(
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
):
    return (
        db.query(Score)
        .filter(Score.user_id == user.id)
        .order_by(Score.score.desc())
        .limit(20)
        .all()
    )


@app.get("/api/leaderboard", response_model=list[LeaderboardEntry])
def leaderboard(db: Session = Depends(get_db)):
    # 각 사용자의 최고 점수 1개씩만 추출
    subq = (
        db.query(Score.user_id, func.max(Score.score).label("best"))
        .group_by(Score.user_id)
        .subquery()
    )
    rows = (
        db.query(Score, User.nickname)
        .join(User, User.id == Score.user_id)
        .join(subq, (subq.c.user_id == Score.user_id) & (subq.c.best == Score.score))
        .order_by(Score.score.desc())
        .limit(10)
        .all()
    )
    return [
        LeaderboardEntry(
            rank=i + 1,
            nickname=nickname,
            score=s.score,
            lines=s.lines,
            level=s.level,
            played_at=s.played_at,
        )
        for i, (s, nickname) in enumerate(rows)
    ]
