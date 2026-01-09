from app.agents.moderator_agent import ModeratorAgent

class StockService:
    def __init__(self):
        self.agent = ModeratorAgent()

    def handle_user_task(self, user_input: str):
        # Agent에게 일을 시킴
        analysis_result = self.agent.process_request(user_input)
        
        # 중요: 반드시 'data'라는 키에 결과값을 담아서 반환!
        return {"status": "success", "data": analysis_result}
