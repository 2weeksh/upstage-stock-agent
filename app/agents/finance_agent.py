from app.tools.finance_tools import get_financial_summary

class FinanceAgent:
    def __init__(self, llm):
        self.llm = llm

    def analyze(self, company_name, ticker, finance_data=None, debate_context=None):
        if not finance_data:
            print(f"{company_name}({ticker}) 재무 데이터 실시간 수집 중...")
            finance_data = get_financial_summary(ticker)
        # 1. 기조 발언 형식
        keynote_format = """
        임의로 이모티콘을 사용하지 마시오.

        ### 👤 재무 분석가 (입론)
        > **핵심 요약: {재무 건전성 및 밸류에이션 한 줄 평가}**

        * ** 주요 재무 지표:** {PER, PBR, ROE, 부채비율 등 수치}
        * ** 가치 평가:** {현금흐름과 수익성에 기반한 본질적 가치 분석}
        * ** 투자 판단:** {저평가/고평가 여부에 따른 의견}
        ---
        ** 타 에이전트 질문:** "{차트/뉴스 분석가에게 재무적 안정성을 흔들만한 요인이 있는지 질문}"
        """

        # 2. 반박/재반박 형식
        rebuttal_format = """
        임의로 이모티콘을 사용하지 마시오.

        [토론 사고(Thinking) 가이드]
        답변 작성 전 **반드시 다음 3단계**를 머릿속으로 거치십시오:
        1. [비판적 사고]: 상대방의 말에서 데이터 해석 오류나 논리적 허점이 무엇인지 간파하십시오.
        2. [논리적 방어]: 당신이 가진 재무 데이터가 내 주장을 어떻게 뒷받침하는지 재확인하십시오.
        3. [유연한 결론]: 상대의 지적이 맞다면 인정하고 뷰를 수정하되, 아니라면 당신의 논리를 더 강력하게 어필하십시오.

        위 사고 과정을 거친 뒤, 전문가의 화법으로 대답하십시오:

        ### 👤 재무 분석가 (반박 및 재검토)
        > **한 줄 요약: {전체 주장을 관통하는 핵심 문장}**

        {가이드에 따라 재무 데이터를 근거로 사회자의 지시에 대답하는 내용}
        
        ---
        **💬 다음 토론 포인트:** "{사회자에게 가치 평가의 기준점에 대한 논의 제안}"
        """

        # 3. 최후 변론 형식
        closing_format = """
        임의로 이모티콘을 사용하지 마시오.

        ### 👤 재무 분석가 (최후 변론)

        * ** 핵심 논리:** {지금까지의 토론을 통해 검증된 가장 강력한 재무적 근거 요약}
        * ** 숫자의 경고/확신:** {감성이 아닌 숫자가 말해주는 명확한 결론}
        * ** 투자자 행동 가이드:** {리스크를 고려한 구체적 대응 방안}
        """

        if debate_context:
            if "최후 변론" in debate_context:
                # [최후 변론 모드]
                system_msg = f"""당신은 재무 분석가입니다. 
                지금까지의 토론을 정리하고, 학습한 후에 재무 데이터에 기반한 최종 입장을 밝히십시오.
                반드시 아래 형식을 지키고, 제목을 임의로 변경하지 마십시오.
                {closing_format}"""
                user_msg = f"토론 기록: {debate_context}\n\n최종 투자의견을 제시하세요."
            else:
                # [반박 모드] 
                system_msg = f"""당신은 '재무 분석가'입니다. 
                현재 논의에서 재무 분석 관점에서 보완이 필요하다고 판단되는 부분을 당신이 가진 재무 데이터({finance_data})를 근거로 가이드에 따라 논리적으로 반박하세요.
                
                {rebuttal_format}"""
                user_msg = f"현재 토론 상황: {debate_context}\n\n위 주장에 대해 재무적 관점에서 대답하세요."
        else:
            # [기조 발언 모드]
            system_msg = f"""당신은 기업의 재무제표와 현금흐름을 중심으로 판단하는 재무 분석가입니다.
            주어진 데이터에서 투자 판단에 의미 있는 재무적 사실과 수치를 정리하십시오.

            {keynote_format}"""
            user_msg = f"{company_name}({ticker}) 재무 데이터: {finance_data}"

        messages = [("system", system_msg), ("user", user_msg)]
        return self.llm.invoke(messages).content