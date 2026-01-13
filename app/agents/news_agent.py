
from app.utils.llm import get_solar_model
from langchain_core.messages import HumanMessage, SystemMessage

class NewsAgent:
    def __init__(self, llm):
        # app/utils/llm.py에서 Solar 모델을 로드합니다.
        if llm:
            self.llm = llm
        else:
            from app.utils.llm import get_solar_model
            self.llm = get_solar_model()
    
    def analyze(self, company_name, ticker, news_data, debate_context=None):
        if debate_context:
            # [반박 모드] 뉴스 기반의 심리 및 트렌드 우위 주장
            system_msg = f"""당신은 시장의 흐름을 읽는 '뉴스 분석가'입니다. 
            상대방의 논리를 듣고, 최신 뉴스 데이터({news_data})에 담긴 
            시장 심리와 미래 성장 가치가 차트나 재무 수치보다 더 중요함을 피력하세요.
            상대방이 '숫자'에 매몰되어 '대중의 심리'를 읽지 못한다고 공격하세요."""
            user_msg = f"현재 토론 내용: {debate_context}\n\n위 주장에 대해 시장 트렌드 관점에서 반박하세요."
        else:
            # [기조 강연 모드]
            system_msg = "당신은 실시간 이슈와 대중의 투자 심리를 분석하는 뉴스 전문가입니다. 현재 호재와 악재를 구분하여 첫 의견을 주십시오."
            user_msg = f"{company_name}({ticker}) 관련 최신 뉴스 데이터: {news_data}"

        messages = [("system", system_msg), ("user", user_msg)]
        return self.llm.invoke(messages).content
    
    
    
    
    
    '''
    def analyze(self, symbol: str, company_name: str, news_data: str, debate_context = None):
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
    '''