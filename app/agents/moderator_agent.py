<<<<<<< HEAD

=======
class ModeratorAgent:
    def process_request(self, user_input: str):
        # 나중에 여기에 Upstage LLM 로직이 들어갈 자리입니다.
        # 지금은 프론트엔드 UI가 요구하는 키 값에 맞춰 가짜 데이터를 반환합니다.

        return {
            "summary": f"'{user_input}'에 대한 시장의 핵심 요약입니다.",
            "conclusion": "현재 지표상 '보유' 의견을 유지하며, 추가 하락 시 분할 매수를 권장합니다.",
            "discussion": "차트 에이전트: 거래량이 늘고 있습니다.\n재무 에이전트: 영업이익률이 개선되었습니다.\n뉴스 에이전트: 긍정적인 기사가 많습니다."
        }
>>>>>>> origin/develop
