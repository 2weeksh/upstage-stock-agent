from langchain_upstage import ChatUpstage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.utils.llm import get_solar_model


class BaseAgent:
    def __init__(self, name, role, retriever, category):
        self.name = name
        self.role = role
        self.retriever = retriever # get_vector_db(ticker)로 반환된 Chroma 객체
        self.llm = get_solar_model() # 업스테이지의 최신 모델 사용
        self.parser = StrOutputParser()
        self.category = category        # 본인의 전공 카테고리 (news, chart, finance 등)

        self.context_cache = {}

    def _get_context(self, query, category=None, debug=False):
        """
        특정 카테고리에 대한 지식을 벡터 DB에서 가져옵니다. (캐시 적용)
        """

        # 1. 캐시 확인: 해당 카테고리의 지식을 이미 가져왔다면 검색 생략
        if category in self.context_cache:
            return self.context_cache[category]

        # 1. 카테고리 필터 설정
        search_filter = {"category": category} if category else None

        # # k값은 데이터의 중요도에 따라 조정 가능 (DART는 조금 더 많이 가져옴)
        k_value = 4 if category == "common" else 3

        # 2. 벡터 DB 검색 (similarity_search 사용)
        docs = self.retriever.similarity_search(
            query, 
            k=k_value, 
            filter=search_filter
        )

        # 3. 캐시에 저장
        context_str = "\n\n".join([doc.page_content for doc in docs])
        self.context_cache[category] = context_str
        
        # [디버그] 검색된 정보 확인 (기존 로직 유지)
        if debug:
            print(f"\n🔍 [{self.name}] RAG 검색 수행 (Category: {category})")
            print(f"   > 쿼리: {query}")
            for i, doc in enumerate(docs):
                source = doc.metadata.get('source', 'Unknown')
                # 내용의 첫 100자 미리보기
                content_preview = doc.page_content.replace('\n', ' ')[:100]
                print(f"     [{i+1}] {source}: {content_preview}...")
            print("="*30)

        return context_str

    def _get_dual_context(self, query, debug=False):
        """
        [이중 검색 핵심 로직]
        1. 'common'(DART)에서 공식적인 기업 기본 정보를 가져옵니다.
        2. 'self.category'(전공)에서 에이전트 특화 실시간 데이터를 가져옵니다.
        """
        # 1. 공통 지식 확보 (DART)
        common_context = self._get_context(query, category="common", debug=debug)
        
        # 2. 전공 지식 확보 (news, chart, finance 중 하나)
        special_context = self._get_context(query, category=self.category, debug=debug)

        # 3. 두 정보를 구조화하여 결합
        combined_context = f"""
### [1. 공식 보고서 기반 기초 데이터 (DART)]
{common_context}

### [2. 최신 {self.category.upper()} 특화 데이터]
{special_context}
"""
        return combined_context

    def create_prompt(self, context, query):
        """자식 클래스에서 구현할 프롬프트 생성 추상 메서드"""
        raise NotImplementedError("자식 클래스에서 create_prompt를 구현해야 합니다.")


    def analyze(self, company_name, ticker, debate_context=None, debug=False):
        """
        에이전트가 이중 검색된 지식을 바탕으로 분석을 수행합니다.
        """
        # 1. 이중 검색 수행
        search_query = f"{company_name} {ticker} 재무 실적 현황 이슈 분석"
        context = self._get_dual_context(search_query, debug=debug)

        # 2. 프롬프트 생성 (토론 맥락이 있다면 포함)
        query_text = f"{company_name}({ticker})에 대한 분석을 수행하세요."
        if debate_context:
            query_text += f"\n\n[이전 토론 맥락]\n{debate_context}"

        prompt = self.create_prompt(context, query_text)
        
        # 3. LLM 호출
        response = self.llm.invoke(prompt)
        return response.content