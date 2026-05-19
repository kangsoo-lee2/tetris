from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    email      = Column(String(255), unique=True, index=True, nullable=False)
    nickname   = Column(String(50), nullable=False)
    hashed_pw  = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    scores = relationship("Score", back_populates="user", cascade="all, delete-orphan")


class Score(Base):
    __tablename__ = "scores"

    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(Integer, ForeignKey("users.id"), nullable=False)
    score     = Column(Integer, nullable=False)
    lines     = Column(Integer, nullable=False, default=0)
    level     = Column(Integer, nullable=False, default=1)
    played_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="scores")
