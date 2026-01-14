from app.utils.llm import get_solar_model
from langchain_core.messages import HumanMessage, SystemMessage

class ChartAgent:
    def __init__(self, llm= None):
        # app/utils/llm.py에서 Solar 모델을 로드합니다.
        if llm:
            self.llm = llm
        else:
            from app.utils.llm import get_solar_model
            self.llm = get_solar_model()


    def analyze(self, company_name, ticker, chart_data, debate_context=None):
        # 1. 기조 발언용 형식 (첫 시작 시)
        keynote_format = """
        ### 👤 차트 분석가 (기조 발언)
        > **핵심 요약: {전체적인 차트 흐름 요약}**

        * **📊 기술적 지표:** {RSI, 거래량 등 현재 수치}
        * **💡 분석 근거:** {데이터를 통한 향후 방향성 예측}
        * **🎯 투자 판단:** {매수/매도/관망}
        ---
        **❓ 타 에이전트 질문:** "{뉴스/재무 분석가에게 자신의 데이터와 상충될 만한 질문 던지기}"
        """

        # 2. 반박/재반박용 형식 (토론 진행 시)
        rebuttal_format = """
        ### 👤 차트 분석가 (반박 및 재검토)
        > **반박 요약: {상대 논리의 허점을 한 줄로 지적}**

        * **🔥 상대 논리 비판:** {전달받은 토론 내용 중 기술적으로 틀린 점 지적}
        * **📊 보완 데이터:** {자신의 차트 데이터로 상대방 논리 재반박}
        * **📍 최종 입장:** {입장 고수 혹은 부분 수용}
        ---
        **💬 다음 토론 포인트:** "{사회자에게 다음으로 논의할 기술적 쟁점 제안}"
        """

        if debate_context:
            # [반박 모드]
            system_msg = f"""
            "당신은 냉철한 차트 분석가입니다. 
            현재 진행 중인 토론의 내용을 듣고, 당신의 기술적 지표({chart_data})를 근거로 
            상대방의 논리를 반박하거나 당신의 입장을 고수하세요."
            {rebuttal_format}"""
            user_msg = f"현재 토론 상황: {debate_context}\n\n데이터: {chart_data}"
        else:
            # [기조 강연 모드]
            system_msg = f"""당신은 데이터와 확률을 믿는 차트 분석가입니다. 지표를 분석해 첫 의견을 주세요.
            {keynote_format}"""
            user_msg = f"{company_name}({ticker}) 분석 데이터: {chart_data}"
        
        messages = [
            ("system", system_msg),
            ("user", user_msg)
        ]
        return self.llm.invoke(messages).content

if __name__ == "__main__":
    llm = get_solar_model()
    agent = ChartAgent(llm)
    sample_chart_data = "예시 차트 데이터: 상승 추세, 거래량 증가, RSI 70 이상"
    result = agent.analyze("삼성전자", "005930", sample_chart_data)
    print(result)