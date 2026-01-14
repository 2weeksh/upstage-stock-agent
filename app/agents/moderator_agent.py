import re

class ModeratorAgent:
    def __init__(self, llm):
        try:
            self.llm = llm.bind(reasoning_effort="high")
            print(f"✅ Moderator Reasoning Mode 설정됨: {self.llm.kwargs}") 
        except:
            self.llm = llm 
            print("⚠️ Moderator: 기본 LLM 모드로 실행됩니다.")
            
    def facilitate(self, company_name, history):
        prompt = f"""
        당신은 주식 토론의 사회자입니다.
        현재까지의 기록을 보고 토론을 계속할지, 아니면 결론이 났는지 판단하십시오.

        [분석 대상]: {company_name}
        [토론 기록]:
        {history}

        [사회자의 사고 과정]
        1. **THOUGHT**: 현재 차트, 뉴스, 재무 전문가들의 의견이 하나로 수렴되었는가? 아니면 여전히 쟁점이 있어 더 싸워야 하는가?
        2. **STATUS**: 
           - 의견이 충분히 교환되었거나, 정해진 시간이 지났다면 -> [TERMINATE]
           - 여전히 다툼이 필요하다면 -> [CONTINUE]
        3. **NEXT_SPEAKER**: [CONTINUE]일 경우, 다음 발언자(Chart, News, Finance 중 1) 지목.
        4. **INSTRUCTION**: 그 발언자에게 시킬 구체적인 반박 질문.

        반드시 아래 포맷으로 답변하세요:
        ---
        THOUGHT: (상황 판단 내용)
        STATUS: [TERMINATE] 또는 [CONTINUE]
        NEXT_SPEAKER: [Chart 또는 News 또는 Finance]
        INSTRUCTION: (질문 내용)
        ---
        """
        return self.llm.invoke(prompt).content

    def summarize_debate(self, company_name, history):
        """
        [Task 4 수정] 사회자의 중립적 요약 (판단 X, 정리 O)
        """
        prompt = f"""
        당신은 주식 토론의 사회자입니다. 치열했던 토론이 이제 막 끝났습니다.
        
        최종 판결(Judge)과 최후 변론(Agent)으로 넘어가기 전에,
        지금까지 오고 간 대화 내용을 **객관적이고 중립적인 입장**에서 간략히 요약해 주세요.

        [분석 대상]: {company_name}
        [전체 토론 기록]:
        {history}

        [작성 가이드]
        1. **평가하지 마십시오.** (누가 이겼는지 판단 금지)
        2. 각 전문가(차트, 뉴스, 재무)가 어떤 핵심 주장을 펼쳤는지 한 줄씩 정리하세요.
        3. 서로 충돌했던 핵심 쟁점(Conflict)이 무엇이었는지 언급하세요.
        4. "이상으로 토론을 마치고, 각 전문가의 최후 변론을 듣겠습니다."라는 멘트로 마무리하세요.
        """
        return self.llm.invoke(prompt).content
