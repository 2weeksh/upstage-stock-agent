# app/service/stock_service.py 예시
from app.agents.moderator_agent import ModeratorAgent

class StockService:
    def __init__(self):
        self.agent = ModeratorAgent()

    async def handle_user_task(self, user_input: str):
        # 에이전트에게 일을 시키고 결과를 그대로 반환
        result = self.agent.process_request(user_input)
        return result