import os
from dotenv import load_dotenv
from langchain_upstage import ChatUpstage

# .env 파일에 저장된 API 키를 환경 변수로 로드합니다.
load_dotenv()

def get_solar_model(temperature=0.1):
    api_key = os.getenv("UPSTAGE_API_KEY")
    
    if not api_key:
        # 키가 없을 경우 에러를 발생시켜 미리 알려줍니다.
        raise ValueError("UPSTAGE_API_KEY가 .env 파일에 설정되어 있지 않습니다. 확인해주세요!")

    # Solar 모델 설정을 반환합니다.
    return ChatUpstage(
        api_key=api_key,
        model="solar-pro2",
        temperature=temperature
    )