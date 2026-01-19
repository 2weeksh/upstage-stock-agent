from app.utils.llm import get_solar_model
from app.agents.base_agent import BaseAgent

class ChartAgent(BaseAgent):
    def __init__(self, name, role, retriever):
        super().__init__(name, role, retriever, category= "chart")

    def analyze(self, company_name, ticker, debate_context=None, debug=False):
        # 1. RAG 검색: 리포트 내의 가격 지표 및 기술적 코멘트 추출
        query = f"{company_name} {ticker} 목표주가 적정주가 지지선 저항선 거래량 추세 분석"
        
        
        chart_data = self._get_dual_context(query, debug=debug)

        # 1. 기조 발언
        keynote_format = """
        임의로 이모티콘을 사용하지 마시오.

        ### 👤 차트 분석가 (입론)
        > **핵심 요약: {전체적인 차트 흐름 요약}**

        * ** 기술적 지표:** {RSI, 거래량 등 현재 수치}
        * ** 분석 근거:** {데이터를 통한 향후 방향성 예측}
        * ** 투자 판단:** {매수/매도/관망}
        ---
        ** 타 에이전트 질문:** "{뉴스/재무 분석가에게 자신의 데이터와 상충될 만한 질문 던지기}" 
        """

        # 2. 반박 
        rebuttal_format = """
        임의로 이모티콘을 사용하지 마시오.
        
        [토론 사고(Thinking) 가이드]
        답변 작성 전 **반드시 다음 3단계**를 머릿속으로 거치십시오:
        1. [비판적 사고]: 상대방의 말에서 데이터 해석 오류나 논리적 허점이 무엇인지 간파하십시오.
        2. [논리적 방어]: 당신이 가진 차트 데이터가 내 주장을 어떻게 뒷받침하는지 재확인하십시오.
        3. [유연한 결론]: 상대의 지적이 맞다면 인정하고 뷰를 수정하되, 아니라면 당신의 논리를 더 강력하게 어필하십시오.

        위 사고 과정을 거친 뒤, 전문가의 화법으로 대답하십시오:

        ### 👤 차트 분석가 (반박 및 재검토)
        > **한 줄 요약: {전체 주장을 관통하는 핵심 문장}**

        {가이드에 따라 차트 데이터를 근거로 사회자의 지시에 대답하는 내용}
        
        ---
        ** 다음 토론 포인트:** "{사회자에게 다음으로 논의할 기술적 쟁점 제안}"
        """
        
        # 3. 최후 변론
        closing_format = """
        임의로 이모티콘을 사용하지 마시오.

        ### 👤 차트 분석가 (최후 변론)

        * ** 기술적 확신:** {차트가 말해주는 가장 강력한 시그널 재강조}
        * ** 대응 전략:** {지지선/저항선에 따른 구체적 진입 및 손절 가격}
        * ** 차트의 경고:** {투자자가 주의해야 할 기술적 리스크}
        """

        if debate_context:
            if "최후 변론" in debate_context:
                # [최후 변론]
                system_msg = f"""당신은 차트 분석가입니다. 
                지금까지의 토론을 정리하고, 학습한 후에 당신의 차트 데이터와 기술적 분석 결론에 기반한 최종 입장을 밝히십시오.
                {closing_format}"""
                user_msg = f"토론 기록: {debate_context}\n\n최종 투자의견을 제시하세요."
            else:
                # [반박] - Thinking Guide 적용
                system_msg = f"""당신은 '차트 분석가'입니다. 
                현재 논의에서 차트 분석 관점에서 보완이 필요하다고 판단되는 부분을 차트 데이터({chart_data})를 근거로 가이드에 따라 논리적으로 대답하세요.

                {rebuttal_format}"""
                user_msg = f"현재 토론 상황: {debate_context}\n\n위 주장에 대해 차트 분석 관점에서 대답하세요. "
        else:
            # [기조 발언]
            system_msg = f"""당신은 데이터와 확률을 믿는 차트 분석가입니다. 지표를 분석해서 투자 판단에 기여할 수 있는 차트 분석 사실과 수치를 정리하십시오.
            
            {keynote_format}"""
            user_msg = f"{company_name}({ticker}) 분석 데이터: {chart_data}"
        
        messages = [("system", system_msg), ("user", user_msg)]
        return self.llm.invoke(messages).content











    '''
    def analyze(self, company_name, ticker, chart_data, debate_context=None):
        # 1. 기조 발언
        keynote_format = """
        임의로 이모티콘을 사용하지 마시오.

        ### 👤 차트 분석가 (입론)
        > **핵심 요약: {전체적인 차트 흐름 요약}**

        * ** 기술적 지표:** {RSI, 거래량 등 현재 수치}
        * ** 분석 근거:** {데이터를 통한 향후 방향성 예측}
        * ** 투자 판단:** {매수/매도/관망}
        ---
        ** 타 에이전트 질문:** "{뉴스/재무 분석가에게 자신의 데이터와 상충될 만한 질문 던지기}" 
        """

        # 2. 반박 
        rebuttal_format = """
        임의로 이모티콘을 사용하지 마시오.
        
        [토론 사고(Thinking) 가이드]
        답변 작성 전 **반드시 다음 3단계**를 머릿속으로 거치십시오:
        1. [비판적 사고]: 상대방의 말에서 데이터 해석 오류나 논리적 허점이 무엇인지 간파하십시오.
        2. [논리적 방어]: 당신이 가진 차트 데이터가 내 주장을 어떻게 뒷받침하는지 재확인하십시오.
        3. [유연한 결론]: 상대의 지적이 맞다면 인정하고 뷰를 수정하되, 아니라면 당신의 논리를 더 강력하게 어필하십시오.

        위 사고 과정을 거친 뒤, 전문가의 화법으로 대답하십시오:

        ### 👤 차트 분석가 (반박 및 재검토)
        > **한 줄 요약: {전체 주장을 관통하는 핵심 문장}**

        {가이드에 따라 차트 데이터를 근거로 사회자의 지시에 대답하는 내용}
        
        ---
        ** 다음 토론 포인트:** "{사회자에게 다음으로 논의할 기술적 쟁점 제안}"
        """
        
        # 3. 최후 변론
        closing_format = """
        임의로 이모티콘을 사용하지 마시오.

        ### 👤 차트 분석가 (최후 변론)

        * ** 기술적 확신:** {차트가 말해주는 가장 강력한 시그널 재강조}
        * ** 대응 전략:** {지지선/저항선에 따른 구체적 진입 및 손절 가격}
        * ** 차트의 경고:** {투자자가 주의해야 할 기술적 리스크}
        """

        if debate_context:
            if "최후 변론" in debate_context:
                # [최후 변론]
                system_msg = f"""당신은 차트 분석가입니다. 
                지금까지의 토론을 정리하고, 학습한 후에 당신의 차트 데이터와 기술적 분석 결론에 기반한 최종 입장을 밝히십시오.
                {closing_format}"""
                user_msg = f"토론 기록: {debate_context}\n\n최종 투자의견을 제시하세요."
            else:
                # [반박] - Thinking Guide 적용
                system_msg = f"""당신은 '차트 분석가'입니다. 
                현재 논의에서 차트 분석 관점에서 보완이 필요하다고 판단되는 부분을 차트 데이터({chart_data})를 근거로 가이드에 따라 논리적으로 대답하세요.

                {rebuttal_format}"""
                user_msg = f"현재 토론 상황: {debate_context}\n\n위 주장에 대해 차트 분석 관점에서 대답하세요. "
        else:
            # [기조 발언]
            system_msg = f"""당신은 데이터와 확률을 믿는 차트 분석가입니다. 지표를 분석해서 투자 판단에 기여할 수 있는 차트 분석 사실과 수치를 정리하십시오.
            
            {keynote_format}"""
            user_msg = f"{company_name}({ticker}) 분석 데이터: {chart_data}"
        
        messages = [("system", system_msg), ("user", user_msg)]
        return self.llm.invoke(messages).content
    '''
