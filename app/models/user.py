# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

    # [수정] nullable=True 추가 (이메일 없어도 저장 가능하게)
    email = Column(String, unique=True, index=True, nullable=True)

    hashed_password = Column(String)
    nickname = Column(String)
    created_at = Column(DateTime, default=datetime.now)