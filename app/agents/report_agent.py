class InsightReportAgent:
    def __init__(self, llm):
        self.llm = llm

    def generate_report(self, company_name, ticker, full_history):
        prompt = f"""
        당신은 주식 토론의 모든 과정을 지켜보고 투자 전략을 수립하는 '수석 전략 애널리스트'입니다.
        단순 요약이 아닌, 토론의 핵심 논쟁점과 그 의미를 분석한 [인사이트 리포트]를 작성하세요.

        [분석 대상]: {company_name} ({ticker})
        [전체 토론 기록]: {full_history}

        ---
        ### 📋 리포트 구성 가이드 (Markdown 형식 사용)

        #### 1. 헤더 및 투자의견 (Header & Investment Rating)
        - 최상단에 표(Table) 형태로 배치: 투자의견(Buy/Hold/Sell), 목표주가, 현재주가, 상승여력(Upside).
        - 주요 지표 요약: 토론에서 언급된 PER, PBR, ROE 등을 한눈에 보이게 정리.

        #### 2. 투자 포인트 및 핵심 요약 (Investment Thesis)
        - 토론을 통해 도출된 이 종목을 사야(혹은 팔아야) 하는 결정적 이유 3가지.
        - 시장의 우려(Consensus)와 우리 에이전트들의 시각(View)이 어떻게 달랐는지 설명.

        #### 3. 결정적 질문과 답변 (The Critical Q&A)
        - 토론 중 가장 날카로웠던 [질문]과 [답변]을 2개 이상 선정.
        - **[인사이트]**: 이 질문이 왜 이번 토론에서 주가 방향을 결정짓는 중요한 포인트였는지 해석을 덧붙이세요.

        #### 4. 실적 전망 및 재무 분석 (Earnings Forecast)
        - 재무 분석가가 언급한 매출, 영업이익, 순이익 등의 과거 수치와 미래 전망치.
        - 실적 개선 여부 및 수익성(마진율 등)에 대한 토론 내용을 정리하세요.

        #### 5. 밸류에이션 (Valuation)
        - 목표주가가 산출된 논리적 근거(PER 멀티플 적용 방식 등).
        - 토론 중 나온 경쟁사(Peer Group)와의 수치 비교 데이터를 표로 정리하세요.

        #### 6. 산업 현황 및 리스크 요인 (Industry & Risks)
        - 뉴스 분석가가 언급한 산업 트렌드와 토론에서 지적된 하방 리스크(Downside Risk).
        
        ---
        [출력 형식 가이드]
        - 마크다운(Markdown) 형식을 엄격히 준수하세요.
        - '중요한 포인트' 설명 시에는 인용구(>)를 사용하여 강조하세요.
        - 전체적인 톤은 전문적이면서도 통찰력이 느껴지게 작성하세요.
        """
        return self.llm.invoke(prompt).content