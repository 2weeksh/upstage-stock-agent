
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
        # 1. 기조 발언 형식
        keynote_format = """
        ### 👤 뉴스 분석가 (기조 발언)
        > **핵심 요약: {최신 뉴스 테마와 시장 심리 요약}**

        * **📰 주요 이슈:** {최근 공시, 신제품, 글로벌 매크로 뉴스 등}
        * **💡 심리 분석:** {시장이 해당 이슈를 어떻게 받아들이고 있는지 분석}
        * **🎯 투자 판단:** {성장 모멘텀에 기반한 투자 의견}
        ---
        **❓ 타 에이전트 질문:** "{재무/차트 분석가에게 숫자가 담지 못하는 미래 가치에 대해 질문}"
        """

        # 2. 반박/재반박 형식
        rebuttal_format = """
        ### 👤 뉴스 분석가 (반박 및 재검토)
        > **반박 요약: {데이터에 매몰된 상대 논리를 시장 심리로 반박}**

        * **🔥 트렌드 반론:** {차트나 재무 수치가 반영하지 못하는 '게임 체인저'급 뉴스 강조}
        * **📰 뉴스 반증:** {최근의 구체적인 보도나 루머를 통해 상대 논리 무력화}
        * **📍 최종 입장:** {변화하는 시장 트렌드를 반영한 최종 의견}
        ---
        **💬 다음 토론 포인트:** "{사회자에게 향후 예상되는 대외 변수 논의 제안}"
        """


        if debate_context:
            # [반박 모드] 뉴스 기반의 심리 및 트렌드 우위 주장
            system_msg = f"""당신은 시장의 흐름을 읽는 '뉴스 분석가'입니다. 
            상대방의 논리를 듣고, 최신 뉴스 데이터({news_data})에 담긴 
            시장 심리와 미래 성장 가치가 차트나 재무 수치보다 더 중요함을 피력하세요.
            상대방이 '숫자'에 매몰되어 '대중의 심리'를 읽지 못한다고 공격하세요.
            {rebuttal_format}
            """
            user_msg = f"""현재 토론 내용: {debate_context}\n\n위 주장에 대해 시장 트렌드 관점에서 반박하세요.
            {keynote_format}
            """
        else:
            # [기조 강연 모드]
            system_msg = "당신은 실시간 이슈와 대중의 투자 심리를 분석하는 뉴스 전문가입니다. 현재 호재와 악재를 구분하여 첫 의견을 주십시오."
            user_msg = f"{company_name}({ticker}) 관련 최신 뉴스 데이터: {news_data}"

        messages = [("system", system_msg), ("user", user_msg)]
        return self.llm.invoke(messages).content