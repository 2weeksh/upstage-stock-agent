import re

class DebateManager:
    def __init__(self, company_name, ticker, moderator, agents):
        """
        company_name: 분석 대상 기업명 (예: 삼성전자)
        ticker: 종목 코드 (예: 005930)
        moderator: ModeratorAgent 인스턴스
        agents: {"Finance": FinanceAgent, "News": NewsAgent, "Chart": ChartAgent} 형태의 딕셔너리
        """
        self.company_name = company_name
        self.ticker = ticker
        self.moderator = moderator
        self.agents = agents  # {"Finance": FinanceAgent(...), ...}
        self.history = ""

    def _add_to_history(self, role_name, speech):
        """토론 기록을 누적합니다."""
        self.history += f"\n[{role_name}]\n{speech}\n"

    def _parse_decision(self, response):
        """사회자의 답변에서 STATUS, NEXT_SPEAKER, INSTRUCTION을 추출"""
        status = re.search(r"STATUS:\s*\[(.*?)\]", response)
        speaker = re.search(r"NEXT_SPEAKER:\s*\[(.*?)\]", response)
        instruction = re.search(r"INSTRUCTION:\s*(.*)", response)
        
        return {
            "status": status.group(1) if status else "CONTINUE",
            "next_speaker": speaker.group(1) if speaker else None,
            "instruction": instruction.group(1) if instruction else ""
        }

    def start_debate(self, max_turns=3):
        print(f"🔔 {self.company_name}({self.ticker}) 주식 끝장 토론을 시작합니다.\n")

        # --- [1단계] 입론 (Keynote Speeches) ---
        print("--- [STEP 1] 전문가별 기조 발언 ---")
        # 정해진 순서대로 입론 진행
        for role in ["Finance", "News", "Chart"]:
            if role in self.agents:
                agent = self.agents[role]
                # 입론 시에는 debate_context를 None으로 전달
                speech = agent.analyze(self.company_name, self.ticker, debate_context=None)
                self._add_to_history(role, speech)
                print(f"\n{speech}")

        # --- [2단계] 토론 루프 (Discussion Loop) ---
        print("\n--- [STEP 2] 자유 토론 및 사회자 중재 ---")
        for turn in range(max_turns):
            # 사회자에게 현재까지의 기록을 주고 다음 진행 판단 요청
            moderator_response = self.moderator.facilitate(self.company_name, self.history)
            decision = self._parse_decision(moderator_response)
            
            print(f"\n[🎤 사회자]: {decision['status']} - 다음 발언자: {decision['next_speaker']}")
            print(f"👉 지시: {decision['instruction']}\n")

            # 토론 종료 조건 확인
            if decision["status"] == "TERMINATE":
                print("⚠️ 사회자가 토론 종료를 선언했습니다.")
                break

            # 지목된 에이전트가 발언
            next_role = decision["next_speaker"]
            if next_role and next_role in self.agents:
                agent = self.agents[next_role]
                # 반박 모드용 컨텍스트 전달
                context = f"사회자 지시: {decision['instruction']}\n이전 토론 요약: {self.history[-1000:]}" # 최근 맥락 위주
                speech = agent.analyze(self.company_name, self.ticker, debate_context=context)
                self._add_to_history(next_role, speech)
                print(f"\n{speech}")
            else:
                print("⚠️ 사회자가 지목한 에이전트를 찾을 수 없어 토론을 종료합니다.")
                break

        # --- [3단계] 마무리 (Closing & Summary) ---
        print("\n--- [STEP 3] 최종 변론 및 요약 ---")
        
        # 1. 사회자의 중립적 요약
        summary = self.moderator.summarize_debate(self.company_name, self.history)
        print(f"\n[📝 토론 요약]\n{summary}")

        # 2. 각 에이전트의 최후 변론 (Closing Statement)
        for role, agent in self.agents.items():
            closing_context = "최후 변론: 지금까지의 토론을 바탕으로 최종 결론을 내주세요."
            closing_speech = agent.analyze(self.company_name, self.ticker, debate_context=closing_context)
            print(f"\n{closing_speech}")

        print("\n✅ 모든 토론이 완료되었습니다.")