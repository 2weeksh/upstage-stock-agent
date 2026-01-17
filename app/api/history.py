from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.core.database import get_db
from app.models.history import History
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/history", tags=["History"])


# 데이터 주고받을 형식
class HistoryCreate(BaseModel):
    question: str
    summary: str
    conclusion: str
    chat_logs: str


class HistoryResponse(BaseModel):
    id: int
    question: str
    summary: str
    conclusion: str
    chat_logs: str
    created_at: str

    class Config:
        from_attributes = True


# 1. 히스토리 저장
@router.post("/", response_model=HistoryResponse)
def create_history(
        item: HistoryCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    new_history = History(
        user_id=current_user.id,
        question=item.question,
        summary=item.summary,
        conclusion=item.conclusion,
        chat_logs=item.chat_logs
    )
    db.add(new_history)
    db.commit()
    db.refresh(new_history)

    return HistoryResponse(
        id=new_history.id,
        question=new_history.question,
        summary=new_history.summary,
        conclusion=new_history.conclusion,
        chat_logs=new_history.chat_logs,
        created_at=new_history.created_at.strftime("%Y-%m-%d %H:%M")
    )


# 2. 내 히스토리 목록 조회 (수정된 부분)
@router.get("/", response_model=List[HistoryResponse])
def read_histories(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # DB에서 기록 가져오기
    histories = db.query(History) \
        .filter(History.user_id == current_user.id) \
        .order_by(History.created_at.desc()) \
        .all()

    # [수정] datetime 객체를 문자열로 변환하여 리스트로 반환
    results = []
    for h in histories:
        results.append(HistoryResponse(
            id=h.id,
            question=h.question,
            summary=h.summary,
            conclusion=h.conclusion,
            chat_logs=h.chat_logs,
            # 여기서 datetime을 string으로 바꿈
            created_at=h.created_at.strftime("%Y-%m-%d %H:%M")
        ))

    return results