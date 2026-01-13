from fastapi import APIRouter
from pydantic import BaseModel
from app.service.stock_service import StockService

router = APIRouter()
service = StockService()

# 프론트엔드의 JSON Body와 키 이름을 맞춥니다.
class UserRequest(BaseModel):
    user_question: str

@router.post("/chat")
async def chat_with_agent(request: UserRequest):
    # 서비스 계층에 질문 전달
    # 서비스에서 최종적으로 summary, conclusion, discussion이 담긴 dict를 반환해야 합니다.
    return await service.handle_user_task(request.user_question)