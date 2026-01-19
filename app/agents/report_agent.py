import json
import re

class InsightReportAgent:
    def __init__(self, llm):
        self.llm = llm


    def generate_report(self, company_name, ticker, full_history):
        # 1. 마크다운의 깊이를 모두 담은 고도화된 JSON 스키마
        report_schema = {
            "report_info": { "title": f"{company_name} 인사이트 리포트", "symbol": ticker, "date": "2026-01" },
            "header_summary": {
                "rating": { "label": "Buy/Hold/Sell", "status": "중립적 관망 등", "color": "red/gray/blue" },
                "target_price": 0, "current_price": 0, "upside_ratio": "0.0%",
                "key_metrics": { "PER": "0x", "PBR": "0x", "ROE": "0%", "Beta": "0.0" }
            },
            "investment_thesis": {
                "buy_side": [ { "point": "제목", "detail": "상세 논리" } ],
                "sell_side": [ { "point": "제목", "detail": "상세 논리" } ],
                "consensus_clash": {
                    "market_view": "일반적인 시장의 우려",
                    "agent_view": "우리 에이전트들만의 차별화된 해석"
                }
            },
            "qna_insights": [
                {
                    "question": "토론의 향방을 가른 결정적 질문",
                    "debate_context": [ { "role": "분석가", "content": "답변 핵심" } ],
                    "strategic_importance": "이 질문이 왜 이번 투자 판단의 키포인트인가?"
                }
            ],
            "financials": {
                "columns": ["2023", "2024(E)", "2025(E)"],
                "rows": [ { "category": "매출/영업이익 등", "values": [] } ],
                "earnings_insight": "실적 추이에 대한 심층 분석"
            },
            "valuation_logic": {
                "method": "목표주가 산출 근거 및 적용 멀티플",
                "peer_group": [ { "company": "경쟁사", "per": "0x", "pbr": "0x" } ]
            },
            "risk_scenarios": [
                { "event": "가상 악재 상황", "impact": "예상되는 주가/실적 타격" }
            ],
            "final_verdict": {
                "short_term": "단기 전망 및 조정 가능성",
                "long_term": "중장기 성장성 판정",
                "action_plan": "구체적인 매수/매도 대응 전략",
                "closing_thought": "투자자가 새겨야 할 최종 한 줄평"
            }
        }

        # 2. JSON 전용 시스템 프롬프트
        prompt = f"""
        당신은 월스트리트 수석 전략가입니다. 제공된 [전체 토론 기록]을 바탕으로 현업 펀드매니저 수준의 고퀄리티 JSON 리포트를 작성하세요.
        
        [작성 원칙]:
        1. **입체적 분석**: 단순히 사실을 요약하지 말고 '매수 측면'과 '매도 측면'의 논리적 대립을 심도 있게 다루세요.
        2. **수치 기반**: 토론에 나온 PER, RSI, 목표가, 실적 추정치 등 모든 정량적 데이터를 누락 없이 포함하세요.
        3. **통찰력 주입**: 'strategic_importance'와 'consensus_clash' 필드에는 멘토님이 강조하신 '이게 왜 중요한가'에 대한 당신의 날카로운 해석을 담으세요.
        4. **시나리오 설계**: 특정 변수(가격 하락 등) 발생 시의 영향도를 구체적으로 추정하여 risk_scenarios를 작성하세요.

        [출력 형식]:
        - 반드시 아래 JSON 스키마 구조를 엄격히 준수하세요.
        - JSON 데이터 외에 어떠한 인사말이나 마크다운 태그도 포함하지 마세요.
        {json.dumps(report_schema, ensure_ascii=False, indent=2)}

        [토론 기록]:
        {full_history}
        """
        
        # LLM 호출
        raw_content = self.llm.invoke(prompt).content

        # 2단계: 정제 및 유효성 검사 호출
        return self.validate_json(raw_content)
    

    def validate_json(self, json_string):
        """json 형식 유효성 검사 및 정제 함수
        - LLM이 마크다운 태그나 불필요한 텍스트를 섞어 반환할 수 있어 이를 걸러내기 위함"""
        try:
            # 1. 마크다운 태그 제거용 정규식 사용
            json_match = re.search(r"(\{.*\})", json_string, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = json_string

            # 2. 파싱 테스트 (실제로 데이터가 잘 뽑혔는지 확인)
            json_dict = json.loads(json_str)
            
            # 3. 다시 문자열로 주거나, 아예 딕셔너리로 리턴 (팀 협의에 따름)
            return json.dumps(json_dict, ensure_ascii=False, indent=2)

        except Exception as e:
            # 실패 시 백엔드가 에러를 인지할 수 있도록 구조화된 에러 리턴 혹은 로깅
            print(f"Critial Parsing Error: {e}")
            # 에러 상황임을 알리는 최소한의 JSON 구조 반환 (선택 사항)
            return json.dumps({
                "error": "JSON_PARSING_FAILED",
                "raw_response": json_string[:100] # 일부만 로깅
            }, ensure_ascii=False)


# 테스트용 실행 코드

if __name__ == "__main__":
    # 1. 테스트용 LLM 로드 (Solar 모델 또는 사용 중인 모델)
    from app.utils.llm import get_solar_model
    llm = get_solar_model()
    
    agent = InsightReportAgent(llm)

    # 2. 테스트용 가상 토론 데이터 (수치와 논쟁이 포함된 풍부한 데이터)
    test_company = "삼성전자"
    test_ticker = "005930"
    test_history = """
    [사회자]: 삼성전자의 HBM 경쟁력과 현재 밸류에이션에 대해 토론을 시작합니다.
    
    [차트 분석가]: 현재 주가는 75,000원 선에서 강력한 지지를 받고 있습니다. RSI는 45로 중립 수준이며, 최근 거래량이 실린 골든크로스가 발생했습니다. 기술적으로는 단기 반등 구간입니다. 목표가는 90,000원 제시합니다.
    
    [재무 분석가]: 하지만 PER이 56배에 달합니다. 2023년 매출 258조, 영업이익 6.5조로 부진했습니다. 2024년 예상 매출은 300조, 영업이익 35조로 턴어라운드가 예상되지만, 여전히 PBR 2.0배는 역사적 고점 부근입니다. SK하이닉스(PBR 1.8배)와 비교해도 밸류에이션 부담이 큽니다.
    
    [뉴스 분석가]: 엔비디아향 HBM3E 공급 승인 뉴스가 임박했다는 소식이 들립니다. 2026년 HBM 시장이 350억 달러까지 커질 전망인데 삼성전자가 소외될 리 없습니다. 업황 트렌드는 명백한 호황기 진입입니다.
    
    [사회자]: (결정적 질문) 재무 분석가님, 턴어라운드가 확실하다면 현재의 높은 PER은 정당화될 수 있지 않을까요?
    
    [재무 분석가]: (답변) 실적 개선폭이 시장 기대치를 상회해야만 가능합니다. 만약 HBM 승인이 지연된다면 고PER은 바로 하방 압력으로 작용할 것입니다. 이게 이번 토론의 가장 핵심적인 리스크 포인트입니다.
    
    [뉴스 분석가]: 리스크는 있지만 AI 반도체 수요 폭증이라는 대세는 꺾이지 않을 것입니다.
    """

    # 3. 리포트 생성 실행
    print(f"🚀 {test_company} 리포트 생성 시작...")
    try:
        json_result = agent.generate_report(test_company, test_ticker, test_history)
        
        # 4. 결과 출력 및 JSON 유효성 검사
        print("\n=== [생성된 JSON 리포트] ===")
        print(json_result)
        
        # 실제 JSON 객체로 변환되는지 확인
        import json
        parsed_data = json.loads(json_result)
        print("\n✅ 성공: JSON 파싱에 문제가 없습니다.")
        print(f"최종 투자의견: {parsed_data['header_summary']['rating']}")
        
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")







# 이건 마크다운 형식 
'''
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
        '''