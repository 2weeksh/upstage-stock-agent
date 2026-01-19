# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timedelta
from app.core.database import Base
from sqlalchemy.orm import relationship

def get_korea_time():
    return datetime.utcnow() + timedelta(hours=9)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

    hashed_password = Column(String)
    nickname = Column(String)
    created_at = Column(DateTime, default=get_korea_time)
    histories = relationship("app.models.history.History", back_populates="owner")


