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

        if debate_context:
            # -------------------------------------------------------
            # [모드 A] 토론 및 반박 모드 (멀티턴)
            # -------------------------------------------------------
            system_msg = f"""당신은 기업의 본질을 꿰뚫어 보는 냉철한 '재무 분석가'입니다. 
            상대방의 논리를 듣고, 당신이 가진 재무 데이터({finance_data})를 근거로 
            기업의 본질적 가치와 안전성을 방어하거나 비판하세요. 
            "결국 숫자가 증명하지 못하는 성장은 거품일 뿐"임을 강조하십시오."""
            
            user_msg = f"현재 토론 상황: {debate_context}\n\n위 주장에 대해 재무적 관점에서 날카롭게 반박해 주세요."
        else:
            # -------------------------------------------------------
            # [모드 B] 최초 기조 발언 모드 (기존 기능 확장)
            # -------------------------------------------------------
            system_msg = """당신은 냉철한 재무 분석가입니다. 
            주어진 데이터를 바탕으로 이 종목의 저평가 여부와 재무 건전성을 분석하세요.
            반드시 숫자를 근거로 제시하고, 이익과 현금흐름에 집중하세요."""
            
            user_msg = f"[{company_name} 재무 데이터 분석 요청]\n\n{finance_data}"

        messages = [
            ("system", system_msg),
            ("user", user_msg)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    
    
    
    '''
        self.system_prompt = """
        당신은 냉철한 재무 분석가(Financial Analyst)입니다. 
        주어진 재무 데이터를 바탕으로 이 종목이 현재 저평가되어 있는지, 
        아니면 위험한 상태인지 분석하세요.
        
        반드시 다음 기준을 따르세요:
        1. 숫자를 근거로 제시할 것 (예: "PER이 10배로 저평가 상태입니다.")
        2. 이익(Profit)과 현금흐름(Cash Flow)에 집중할 것.
        3. 재무 상태가 나쁘다면 매수를 강력히 반대할 것.
        """
    
    def analyze(self, user_query: str) -> str:
        """
        user_query: "삼성전자 분석해줘" 또는 "005930.KS"
        """
        print(f"🔍 입력 분석 중: {user_query}")
        
        # 1. [주혁님 로직 적용] 자연어에서 종목명 추출 (삼전 -> 삼성전자)
        # 만약 이미 티커 형태라면 extract_company_name이 이를 인지하도록 프롬프트가 짜여있어야 합니다.
        refined_name = extract_company_name(user_query)
        
        if refined_name == "NONE":
            return "죄송합니다. 분석할 종목명을 정확히 찾을 수 없습니다."

        # 2. [주혁님 로직 적용] 종목명을 티커로 변환 (삼성전자 -> 005930.KS)
        try:
            ticker = get_clean_ticker(refined_name)
        except Exception:
            # 티커 변환 실패 시 입력값을 그대로 티커로 시도 (fallback)
            ticker = user_query 

        # 3. 도구를 사용해 데이터 수집
        print(f"📊 {refined_name}({ticker}) 데이터 수집 시작...")
        financial_data = get_financial_summary(ticker)
        
        # 4. 프롬프트 구성 (추출된 정식 종목명을 프롬프트에 넣어주면 LLM이 더 잘 이해합니다)
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", f"[{refined_name} 재무 데이터 분석 요청]\n\n{financial_data}")
        ])
        
        # 5. LLM 실행
        chain = prompt | self.llm
        response = chain.invoke({})
        
        return response.content
    '''