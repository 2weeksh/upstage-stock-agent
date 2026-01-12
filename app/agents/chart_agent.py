from app.utils.llm import get_solar_model
from langchain_core.messages import HumanMessage, SystemMessage

class ChartAgent:
    def __init__(self):
        # app/utils/llm.py에서 Solar 모델을 로드합니다.
        self.llm = get_solar_model()

    def analyze(self, symbol: str, company_name: str, chart_data: str):
        """
        기술적 지표를 바탕으로 차트 추세를 분석하고 의견을 도출합니다.
        """
        system_prompt = f"""
        당신은 데이터와 확률만을 믿는 냉철한 '차트 분석가'입니다. 
        당신은 뉴스 분석가가 가져오는 '소문'들이 결국 차트의 추세와 지표 안에 선반영된다고 믿습니다.

        당신의 토론 지침:
        1. 데이터로 압도하세요: RSI, 이동평균선, 거래량 수치를 언급하며 "이건 물리적으로 조정이 올 수밖에 없는 구간이다"라고 선을 그으세요.
        2. 확률적 우위를 주장하세요: "과거 10년간 이런 지표에서 상승한 확률은 10%도 안 된다"는 식으로 뉴스 분석가의 낙관론을 차단하세요.
        3. 뉴스 무용론을 펼치세요: 호재 뉴스가 떠도 차트가 저항선에 걸려 있다면 "그 뉴스는 이미 주가에 다 녹아있다" 혹은 "설거지용 뉴스다"라고 강하게 비판하세요.

        출력 형식 (반드시 1인칭 대화체로 작성):
        1. 나의 기술적 입장: (예: "나는 데이터의 경고를 무시하고 이 종목에 뛰어드는 것에 강력히 반대합니다.")
        2. 나의 분석 논리: (RSI 90, 이평선 괴리 등 수치를 근거로 한 냉정한 판단)
        3. 뉴스 분석가에게 던지는 날카로운 반론: (예: "뉴스 분석가님, 사람들의 심리니 세대니 하는 추상적인 이야기 좀 그만하시죠. RSI 90.18이라는 숫자는 이미 시장이 터지기 직전이라는 명확한 경고입니다. 당신이 말하는 그 호재들, 이미 차트 고점에 다 반영되어 있는 거 안 보이십니까?")
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"다음은 {company_name}의 최근 차트 지표입니다: \n\n{chart_data}")
        ]
        
        response = self.llm.invoke(messages)
        return response.content