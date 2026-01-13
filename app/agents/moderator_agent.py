class ModeratorAgent:
    def __init__(self, llm):
        self.llm = llm

    def facilitate(self, company_name, reports):
        prompt = f"""
        당신은 주식 전문 토론회의 사회자입니다. {company_name}에 대한 전문가들의 기조 발언을 분석하여 가장 큰 논리적 충돌 지점을 찾으세요.
        
        [전문가 리포트]
        {reports}
        
        [지시사항]
        1. 의견이 가장 대립하는 두 전문가를 선정하세요.
        2. 한 전문가의 논리를 인용하며 다른 전문가에게 그에 대한 재반박을 요청하세요.
        3. **반드시 마지막 줄에 다음 발언자를 지정하세요.**
           형식: [NEXT]: Chart 또는 [NEXT]: News 또는 [NEXT]: Finance
        
        예시: "...해서 차트 분석가님의 의견이 궁금합니다. [NEXT]: Chart"
        """
        return self.llm.invoke(prompt).content

    def summarize(self, company_name, full_history):
        """2단계: 모든 토론 과정을 지켜보고 최종 결론을 내림"""
        prompt = f"""
        당신은 최종 의사결정권자입니다. 아래의 치열한 토론 과정을 듣고 
        {company_name}에 대한 최종 투자 등급과 그 이유를 결정하세요.
        
        [전체 토론 기록]
        {full_history}
        
        반드시 [강력 매수 / 매수 / 중립 / 매도 / 강력 매도] 중 하나를 선택하세요.
        """
        return self.llm.invoke(prompt).content
