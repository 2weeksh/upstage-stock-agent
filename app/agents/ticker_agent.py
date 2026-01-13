from app.utils.llm import get_solar_model
from langchain_core.messages import HumanMessage, SystemMessage

def extract_company_name(user_query: str):
    """
    사용자의 질문에서 공식 주식 종목명을 추출합니다.
    """
    # 1. Solar 모델 로드 (app/utils/llm.py의 함수 활용)
    llm = get_solar_model()

    # 2. 시스템 프롬프트 설정 (주혁님이 작성하신 규칙 반영)
    system_prompt = """
    당신은 글로벌 주식 전문 비서입니다. 사용자의 질문에서 분석 대상의 **'티커(Ticker)'**만 추출하세요.

    [추출 규칙]
    1. 한국 주식은 6자리 숫자로 추출하세요. (예: 삼전 -> 005930)
    2. 해외 주식은 영문 심볼로 추출하세요. (예: 애플 -> AAPL, 엔비디아 -> NVDA)
    3. 오직 티커 하나만 출력하고 절대 설명을 덧붙이지 마세요.
    4. 찾지 못했다면 'NONE'만 출력하세요.
    """
    
    # 3. 메시지 구성
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"사용자 질문: {user_query}")
    ]
    
    # 4. Solar LLM 호출 및 결과 반환
    try:
        response = llm.invoke(messages)
        # 결과값에서 공백 등을 제거하여 깔끔하게 종목명만 추출합니다.
        refined_name = response.content.strip()
        return refined_name
    except Exception as e:
        print(f"❌ LLM 종목명 추출 중 오류 발생: {e}")
        return "NONE"
