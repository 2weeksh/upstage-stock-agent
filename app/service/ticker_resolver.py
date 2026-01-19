from ..utils.ticker_utils import get_clean_ticker
from ..agents.ticker_agent import extract_company_name # 유저님이 작성하신 LLM 추출 함수

def resolve_target_ticker(user_input: str):
    """
    ticker_agent으로 이름을 뽑고, Ticker_utils로 형식을 정리하는 통합 함수
    """
    print(f"🧐 분석 대상 식별 중: '{user_input}'")
    
    # 1. ticker_agent을 통해 질문에서 티커/종목명 추출 (005930 또는 삼성전자 등)
    raw_ticker = extract_company_name(user_input)
    
    if raw_ticker == "NONE":
        raise ValueError("분석 대상을 찾을 수 없습니다. 종목명을 정확히 입력해 주세요.")
    
    # 2. Ticker_utils를 통해 표준화된 티커로 변환 (005930.KS 등)
    try:
        clean_ticker = get_clean_ticker(raw_ticker)
        print(f"✅ 최종 식별된 티커: {clean_ticker}")
        return clean_ticker
    except Exception as e:
        # Ticker_utils가 못 찾아도 LLM이 준 값을 믿고 한 번 더 시도
        return raw_ticker