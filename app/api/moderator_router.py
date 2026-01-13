from fastapi import APIRouter
from fastapi.responses import StreamingResponse  # ❗ 추가
from pydantic import BaseModel
from app.service.stock_service import StockService

router = APIRouter()
service = StockService()

class UserRequest(BaseModel):
    user_question: str

@router.post("/chat")
async def chat_with_agent(request: UserRequest):
    # StreamingResponse로 감싸서 반환
    # media_type="application/x-ndjson" 은 Newline Delimited JSON을 의미합니다.
    return StreamingResponse(
        service.handle_user_task(request.user_question),
        media_type="application/x-ndjson"
    )