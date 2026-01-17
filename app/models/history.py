from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime, timedelta

def get_korea_time():
    return datetime.utcnow() + timedelta(hours=9)

class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # 누가 저장했는지

    question = Column(String)  # 질문
    summary = Column(Text)  # 요약
    conclusion = Column(Text)  # 결론
    chat_logs = Column(Text)  # 대화내역 (JSON 문자열)

    created_at = Column(DateTime, default=get_korea_time)

    # User 모델과 관계 설정
    owner = relationship("app.models.user.User", back_populates="histories")