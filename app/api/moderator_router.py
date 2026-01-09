from fastapi import APIRouter
from pydantic import BaseModel
from app.service.stock_service import StockService

router = APIRouter()
service = StockService()

class UserRequest(BaseModel):
    query: str

@router.post("/chat")
def chat_with_agent(request: UserRequest):
    # 사용자의 query(입력값)를 서비스로 넘김
    return service.handle_user_task(request.query)
