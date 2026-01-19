from langchain_core.documents import Document  # [추가]
from app.utils.llm import get_solar_model

class DataValidator:
    def __init__(self):
        self.llm = get_solar_model()

    # [수정] ticker 인자 추가, 리턴 타입 변경 (str -> list[Document])
    def validate_and_filter(self, category: str, company_name: str, ticker: str, raw_data: str) -> list[Document]:
        """
        Raw Data를 검증/정제한 후, Ingestor가 바로 쓸 수 있게 Document 객체로 포장하여 반환합니다.
        """
        # 데이터가 비어있거나 에러 메시지인 경우 빈 리스트 반환 (또는 '데이터 없음' 문서 반환)
        if not raw_data or "오류" in raw_data or "Error" in raw_data:
            print(f"⚠️ [Validator] {category} 데이터 유효하지 않음.")
            return []  # 빈 리스트 반환하여 DB 저장을 건너뛰거나, 필요시 더미 데이터 반환

        # 1. 카테고리별 검증 기준 설정
        if category == "news":
            criteria = (
                "- 광고, 스팸, 홍보성 문구 제거\n"
                "- 해당 종목과 직접 관련 없는 기사 제외\n"
                "- 날짜가 명시되지 않은 오래된 정보 제외\n"
                "- 중복된 내용 통합 및 핵심 팩트 요약"
            )
        elif category == "finance":
            criteria = (
                "- 숫자 단위(원/달러/억/조)의 오류 확인\n"
                "- 필수 지표(매출, 영업이익 등) 누락 여부 확인\n"
                "- 예상치(Consensus)와 확정치(Actual) 구분"
            )
        elif category == "chart":
            criteria = (
                "- 0원, NaN 등 비정상적인 수치 제외\n"
                "- 데이터 끊김 확인\n"
                "- 기술적 지표의 수치 오류 확인"
            )
        else:
            criteria = "데이터의 논리적 일관성 확인 및 노이즈 제거"

        # 2. 검증 프롬프트
        prompt = f"""
        당신은 금융 데이터 신뢰성 검증 AI입니다. 
        아래 [Raw Data]를 [검증 기준]에 맞춰 필터링하고 정제하십시오.

        [검증 대상]
        - 종목: {company_name} ({ticker})
        - 카테고리: {category}

        [검증 기준]
        {criteria}

        [Raw Data]
        {raw_data}

        [지시사항]
        1. 데이터가 유효하다면, 분석가가 사용하기 좋게 노이즈를 제거하고 핵심만 요약하여 출력하시오.
        2. 데이터가 분석에 부적합하거나 내용이 없다면 오직 "NULL" 이라고만 출력하시오.
        """

        messages = [
            ("system", "당신은 데이터 품질 관리자입니다."),
            ("user", prompt)
        ]

        try:
            cleaned_text = self.llm.invoke(messages).content
            
            if "NULL" in cleaned_text:
                return []

            # [핵심] 여기서 Document 객체로 포장합니다.
            doc = Document(
                page_content=cleaned_text,
                metadata={
                    "source": category,
                    "ticker": ticker,
                    "company": company_name
                }
            )
            return [doc] # 리스트 형태로 반환

        except Exception as e:
            print(f"❌ [Validator] 검증 중 에러: {e}")
            # 에러 시 원본이라도 포장해서 반환 (Fallback)
            return [Document(page_content=raw_data, metadata={"source": category, "ticker": ticker, "note": "validation_failed"})]