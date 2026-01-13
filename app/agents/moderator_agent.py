import re

class ModeratorAgent:
    def __init__(self, llm):
        # [Task 1] Solar Pro 2의 Reasoning Mode 활성화
        # 만약 bind 기능이 지원되지 않는 wrapper라면 model_kwargs={"reasoning_effort": "high"} 등으로 수정 필요
        try:
            self.llm = llm.bind(reasoning_effort="high")
        except:
            self.llm = llm # bind가 안되는 경우 기본 llm 사용

    def get_debate_rules(self):
        """
        [Task 2] 토론 2라운드부터 적용될 엄격한 답변 규칙
        """
        return """
        [⚡️ 토론 답변 프로토콜]
        상대방의 발언을 분석한 후, 반드시 다음 3단계 구조로 답변하십시오:
        1. [지적 (Critique)]: 상대방(이전 발언자)의 데이터 해석 오류, 논리적 비약, 누락된 리스크를 날카롭게 지적하십시오.
        2. [방어 (Defend)]: 지적받은 내용에 대해 당신이 보유한 데이터(차트/뉴스/재무)를 근거로 방어하십시오.
        3. [수정 (Modify)]: 지적이 타당하다면 뷰를 수정하고, 아니라면 기존 논리를 강화하십시오.
        """

    def facilitate(self, company_name, history):
        """
        [Task 3] 사회자의 판단: 계속 할 것인가, 끝낼 것인가?
        """
        prompt = f"""
        당신은 냉철한 주식 토론 사회자입니다.
        현재까지의 기록을 보고 토론을 계속할지, 아니면 결론이 났는지 판단하십시오.

        [분석 대상]: {company_name}
        [토론 기록]:
        {history}

        [사회자의 사고 과정(Reasoning) 및 지시]
        1. **THOUGHT**: 현재 차트, 뉴스, 재무 전문가들의 의견이 하나로 수렴되었는가? 아니면 여전히 쟁점이 있어 더 싸워야 하는가? 깊게 생각하라.
        2. **STATUS**: 
           - 의견이 충분히 교환되었고 수렴되었다면 -> [TERMINATE]
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