from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserRegister(BaseModel):
    email:    EmailStr
    nickname: str
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다")
        return v

    @field_validator("nickname")
    @classmethod
    def nickname_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("닉네임을 입력해주세요")
        return v


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
    model_config = ConfigDict(from_attributes=True)

    score:     int
    lines:     int
    level:     int
    played_at: datetime


class LeaderboardEntry(BaseModel):
    rank:     int
    nickname: str
    score:    int
    lines:    int
    level:    int
    played_at: datetime
