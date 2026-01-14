# app/agents/finance_agent.py
from langchain_core.prompts import ChatPromptTemplate
from app.tools.finance_tools import get_financial_summary
from app.agents.ticker_agent import extract_company_name
from app.utils.ticker_utils import get_clean_ticker

class FinanceAgent:
    def __init__(self, llm):
        self.llm = llm

    def analyze(self, company_name, ticker, finance_data=None, debate_context=None):
        """
        finance_data: 외부에서 데이터를 주면 그걸 쓰고, 없으면 직접 수집합니다.
        debate_context: 사회자가 질문을 던지면 '반박 모드'로 작동합니다.
        """
        
        # 1. 데이터가 없으면 직접 수집 (기존 기능 유지)
        if not finance_data:
            print(f"📊 {company_name}({ticker}) 재무 데이터 실시간 수집 중...")
            finance_data = get_financial_summary(ticker)

        keynote_format = """
        ### 👤 재무 분석가 (기조 발언)
        > **핵심 요약: {재무 건전성 및 밸류에이션 한 줄 평가}**

        * **📊 주요 재무 지표:** {PER, PBR, ROE, 부채비율 등 수치}
        * **💡 가치 평가:** {현금흐름과 수익성에 기반한 본질적 가치 분석}
        * **🎯 투자 판단:** {저평가/고평가 여부에 따른 의견}
        ---
        **❓ 타 에이전트 질문:** "{차트/뉴스 분석가에게 재무적 안정성을 흔들만한 요인이 있는지 질문}"
        """

        # 2. 반박/재반박 형식
        rebuttal_format = """
        ### 👤 재무 분석가 (반박 및 재검토)
        > **반박 요약: {상대의 낙관론/비관론을 숫자로 반박}**

        * **🔥 논리 비판:** {상대방이 간과한 재무적 리스크나 회계적 수치 지적}
        * **📊 데이터 반증:** {재무제표 상의 팩트로 상대 주장의 허점 공격}
        * **📍 최종 입장:** {재무적 안전마진 고려 시 최종 결론}
        ---
        **💬 다음 토론 포인트:** "{사회자에게 가치 평가의 기준점에 대한 논의 제안}"
        """


        if debate_context:
            # 토론 및 반박 모드 (멀티턴)
            system_msg = f"""당신은 기업의 본질을 꿰뚫어 보는 냉철한 '재무 분석가'입니다. 
            상대방의 논리를 듣고, 당신이 가진 재무 데이터({finance_data})를 근거로 
            기업의 본질적 가치와 안전성을 방어하거나 비판하세요. """
            {rebuttal_format}
            user_msg = f"현재 토론 상황: {debate_context}\n\n위 주장에 대해 재무적 관점에서 날카롭게 반박해 주세요."
        else:
            # -------------------------------------------------------
            # [모드 B] 최초 기조 발언 모드 (기존 기능 확장)
            # -------------------------------------------------------
            system_msg = f"""당신은 냉철한 재무 분석가입니다. 
            주어진 데이터를 바탕으로 이 종목의 저평가 여부와 재무 건전성을 분석하세요.
            반드시 숫자를 근거로 제시하고, 이익과 현금흐름에 집중하세요.
            {keynote_format}
            """
            user_msg = f"[{company_name} 재무 데이터 분석 요청]\n\n{finance_data}"

        messages = [
            ("system", system_msg),
            ("user", user_msg)
        ]
        
        response = self.llm.invoke(messages)
        return response.content

