## 가짜 값

class ModeratorAgent:
    def process_request(self, user_input: str):
        # 여기서 나중에 Upstage LLM이나 주가 검색 API 등을 호출합니다.
        # 지금은 단순하게 입력된 텍스트에 응답을 붙여 반환합니다.
        result = f"Agent가 '{user_input}'에 대해 분석한 결과입니다: [상승세 예상]"
        return result
