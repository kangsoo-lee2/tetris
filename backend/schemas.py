from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email:    EmailStr
    nickname: str
    password: str


class UserLogin(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    nickname:     str


class ScoreSubmit(BaseModel):
    score: int
    lines: int
    level: int


class ScoreRecord(BaseModel):
    score:     int
    lines:     int
    level:     int
    played_at: datetime

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    rank:     int
    nickname: str
    score:    int
    lines:    int
    level:    int
    played_at: datetime
