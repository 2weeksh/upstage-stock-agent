# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
<<<<<<< HEAD
from datetime import datetime
from app.core.database import Base

=======
from datetime import datetime, timedelta
from app.core.database import Base
from sqlalchemy.orm import relationship

def get_korea_time():
    return datetime.utcnow() + timedelta(hours=9)
>>>>>>> 6482c8e3a29de456261bdf2e425a48ccdbfa2d25

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

    hashed_password = Column(String)
    nickname = Column(String)
<<<<<<< HEAD
    created_at = Column(DateTime, default=datetime.now)
=======
    created_at = Column(DateTime, default=get_korea_time)
    histories = relationship("app.models.history.History", back_populates="owner")
>>>>>>> 6482c8e3a29de456261bdf2e425a48ccdbfa2d25
