class JudgeAgent:
    def __init__(self, llm):
        # [수정] Judge에게도 Solar Pro 2 Reasoning Mode 적용 및 확인 메시지 출력
        try:
            self.llm = llm.bind(reasoning_effort="high")
            print(f"✅ Judge Agent Reasoning Mode 설정됨: {self.llm.kwargs}")
        except:
            self.llm = llm
            print("⚠️ Judge Agent: 기본 LLM 모드로 실행됩니다.")

    def adjudicate(self, company_name, full_history):
        """
        [Task 3] 최종 투자 전략 수립
        """
        prompt = f"""
        여러 전문가의 토론 내용을 종합하여 현재 시점에서 가장 합리적인 판단을 내리는 최종 의사결정권자(Judge)입니다.
        아래는 {company_name}에 대한 각 분야 전문가(차트, 뉴스, 재무)들의 치열한 토론 기록입니다.
        
        이 내용을 바탕으로 모호하지 않은 '실전 투자 전략 보고서'를 작성하십시오.

        [전체 토론 기록]
        {full_history}

        [작성 요구사항]
        1. [최종 등급 기준표]
        - 8.0 ~ 10.0: [강력 매수] - 압도적 호재와 상승 모멘텀
        - 6.0 ~ 7.9: [매수] - 전반적 우상향 기대 및 긍정적 지표
        - 4.0 ~ 5.9: [중립] - 방향성 불분명, 관망 필요
        - 2.0 ~ 3.9: [매도] - 하방 압력 존재 및 리스크 관리 필요
        - 0.0 ~ 1.9: [강력 매도] - 심각한 악재 또는 하락 추세 뚜렷

        2. 핵심 승리 논리 3가지 (토론 과정에서 가장 설득력 있었던 근거)
        [승리 논리 1]
        [승리 논리 2]
        [승리 논리 3]

        3. 주요 리스크 (토론에서 지적된 치명적 약점)
        [주요 리스크 1]
        [주요 리스크 2]
        [주요 리스크 3]

        4. **구체적 트레이딩 시나리오** (가장 중요):
           - 적정 진입 가격대 (구체적 숫자 제시)
           - 1차 목표가 / 2차 목표가
           - 손절가 (Stop Loss)
        
        결과는 가독성 좋은 Markdown 형식으로 출력하세요.
        """
        return self.llm.invoke(prompt).content