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
    
    