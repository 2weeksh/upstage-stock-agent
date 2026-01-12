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
    당신은 한국 주식 전문 비서입니다. 
    사용자의 질문에서 주식 분석 대상인 '공식 종목명'만 추출하세요.
    
    [규칙]
    1. 약어나 별칭은 공식 명칭으로 바꿉니다. (예: 삼전 -> 삼성전자, 하이닉스 -> SK하이닉스, 닉스 -> SK하이닉스, 현대차 -> 현대자동차)
    2. 결과에는 종목명만 딱 한 단어로 출력하세요. 부연 설명이나 마침표는 생략합니다.
    3. 종목을 도저히 못 찾겠거나 주식 관련 질문이 아니라면 'NONE'이라고만 하세요.
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

# 테스트 코드 (로컬에서 바로 실행해볼 수 있습니다)
if __name__ == "__main__":
    test_queries = [
        "삼전 분석해줘",
        "하이닉스 오늘 어때?",
        "현대차랑 기아차 비교해줄래?", # 이 경우 첫 번째 종목 위주로 추출하도록 유도됨
        "내일 날씨 알려줘"
    ]
    
    for query in test_queries:
        result = extract_company_name(query)
        print(f"Q: {query} -> A: {result}")