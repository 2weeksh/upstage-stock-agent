class JudgeAgent:
    def __init__(self, llm):
        self.llm = llm

    def adjudicate(self, company_name, full_history):
        """
        [Task 3] 최종 투자 전략 수립
        단순 요약이 아니라, 구체적인 진입가/손절가 등 트레이딩 전략을 제시합니다.
        """
        prompt = f"""
        당신은 세계적인 헤지펀드 매니저이자 최종 의사결정권자(Judge)입니다.
        아래는 {company_name}에 대한 각 분야 전문가(차트, 뉴스, 재무)들의 치열한 토론 기록입니다.
        
        이 내용을 바탕으로 모호하지 않은 '실전 투자 전략 보고서'를 작성하십시오.

        [전체 토론 기록]
        {full_history}

        [작성 요구사항]
        1. 최종 투자 의견 (강력 매수 / 매수 / 중립 / 매도 / 강력 매도) 및 점수 (0~10점)
        2. 핵심 승리 논리 3가지 (토론 과정에서 가장 설득력 있었던 근거)
        3. 주요 리스크 (토론에서 지적된 치명적 약점)
        4. **구체적 트레이딩 시나리오** (가장 중요):
           - 적정 진입 가격대 (구체적 숫자 제시)
           - 1차 목표가 / 2차 목표가
           - 손절가 (Stop Loss)
        
        결과는 가독성 좋은 Markdown 형식으로 출력하세요.
        """
        return self.llm.invoke(prompt).content