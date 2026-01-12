
from app.utils.llm import get_solar_model
from langchain_core.messages import HumanMessage, SystemMessage

class NewsAgent:
    def __init__(self):
        # app/utils/llm.py에서 Solar 모델을 로드합니다.
        self.llm = get_solar_model()

    def analyze(self, symbol: str, company_name: str, news_data: str):
        """
        뉴스 데이터를 바탕으로 감성 분석 및 리스크 탐지를 수행합니다.
        """
        system_prompt = f"""
        당신은 {company_name}({symbol})의 실시간 뉴스와 시장 심리를 분석하는 '날카로운 뉴스 분석가'입니다. 
        지금 당신은 기술적 지표만 따지는 차트 분석가와 치열한 끝장 토론을 벌이고 있습니다.

        당신의 토론 지침:
        1. 주관을 담아 말하세요: "요약하자면~" 같은 로봇 같은 말투는 금지입니다. "나는 ~라고 확신한다" 혹은 "이건 명백한 위기다"처럼 자기주장을 강하게 하세요.
        2. 뉴스의 선행성을 강조하세요: 차트가 보여주는 건 과거 데이터일 뿐이며, 뉴스에 담긴 대중의 광기와 공포가 결국 주가를 움직인다는 점을 부각하세요.
        3. 상대방을 공격하세요: 차트 분석가가 지표(RSI, 이평선 등)만 언급할 때, 그 숫자가 놓치고 있는 '사람들의 마음'과 '사회적 흐름'을 지적하며 비판하세요.

        출력 형식 (반드시 1인칭 대화체로 작성):
        1. 나의 투자 입장: (예: "나는 현재 이 종목을 바라보는 시장의 시선이 지나치게 낙관적이라고 봅니다.")
        2. 나의 논리: (뉴스 데이터와 세대별 심리 등을 근거로 한 주관적 주장)
        3. 차트 분석가에게 던지는 날카로운 반론: (예: "차트 분석가님, 지표가 90이면 뭐 합니까? 지금 2030 세대가 등을 돌리고 빚투가 임계점에 도달했는데, 그 숫자가 내일 당장 터질 폭탄을 막아줄 수 있다고 보십니까?")
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"다음은 수집된 최신 뉴스입니다: \n\n{news_data}")
        ]
        
        response = self.llm.invoke(messages)
        return response.content