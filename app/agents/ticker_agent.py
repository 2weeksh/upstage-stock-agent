from app.utils.llm import get_solar_model
from langchain_core.messages import HumanMessage, SystemMessage
import re

def extract_company_name(user_query: str):
    """
    사용자의 질문에서 공식 주식 종목명을 추출합니다.
    """
    # 1. Solar 모델 로드 
    llm = get_solar_model()

    # 2. 시스템 프롬프트 설정
    system_prompt = """
    당신은 글로벌 주식 전문 비서입니다. 사용자의 질문에서 분석 대상의 **'티커(Ticker)'**만 추출하세요.

    [추출 규칙 - 엄격 준수]
    1. 한국 주식은 **6자리 숫자**로 추출하세요. (예: 삼전 -> 005930, 한화오션 ->042660)
    2. 해외 주식은 **영문 심볼**로 추출하세요. (예: 쿠팡 -> CPNG, 애플 -> AAPL, 엔비디아 -> NVDA)
    3. 오직 결과값(티커 또는 정식명칭) 하나만 출력하고 절대 설명을 덧붙이지 마세요.
    4. 만약 티커가 도저히 생각나지 않는 경우에만 기업의 '정식 명칭'을 출력하세요.
    5. **결과값 외에 (설명, 추론 과정(Thought), '정답:') 같은 수식어를 절대 붙이지 마세요.** 단 한 단어만 출력하세요.
    6. 어떤 정보도 찾지 못했다면 'NONE'만 출력하세요.
    """
    
    # 3. 메시지 구성
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"사용자 질문: {user_query}")
    ]
    
    # 4. Solar LLM 호출 및 결과 반환
    try:
        response = llm.invoke(messages).content.strip()
        
        match = re.search(r'(?:정답|티커|Ticker):\s*([A-Z0-9.]+)', response, re.I)
        if match:
            return match.group(1).strip()
        
        # 2. 줄바꿈이 있다면 마지막 줄의 첫 단어를 가져옴 (보통 결론이 마지막에 오므로)
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        if lines:
            last_word = lines[-1].split()[-1] # 마지막 줄의 마지막 단어
            # 특수문자 제거 (**, [], () 등)
            return re.sub(r'[^\w.]', '', last_word)
        return response
     
    except Exception as e:
        print(f"❌ LLM 종목명 추출 중 오류 발생: {e}")
        return "NONE"
