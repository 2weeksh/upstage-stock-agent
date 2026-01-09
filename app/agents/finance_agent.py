from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from src.tools.finance_tools import get_financial_summary
# llm은 main이나 utils에서 가져온다고 가정

class FinanceAgent:
    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = """
        당신은 냉철한 재무 분석가(Financial Analyst)입니다. 
        주어진 재무 데이터를 바탕으로 이 종목이 현재 저평가되어 있는지, 
        아니면 위험한 상태인지 분석하세요.
        
        반드시 다음 기준을 따르세요:
        1. 숫자를 근거로 제시할 것 (예: "PER이 10배로 저평가 상태입니다.")
        2. 이익(Profit)과 현금흐름(Cash Flow)에 집중할 것.
        3. 재무 상태가 나쁘다면 매수를 강력히 반대할 것.
        """

    def analyze(self, ticker: str) -> str:
        # 1. 도구를 사용해 데이터 수집
        financial_data = get_financial_summary(ticker)
        
        # 2. 프롬프트 구성
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", f"다음 재무 데이터를 분석하고 투자 의견(매수/매도/보류)을 제시해줘.\n\n{financial_data}")
        ])
        
        # 3. LLM 실행
        chain = prompt | self.llm
        response = chain.invoke({})
        
        return response.content

# 사용 예시
# agent = FinanceAgent(llm)
# print(agent.analyze("005930.KS")) # 삼성전자