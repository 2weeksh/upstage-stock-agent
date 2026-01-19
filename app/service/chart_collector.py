# app/service/chart_collector.py

import yfinance as yf
import pandas as pd
from langchain_core.documents import Document

class ChartCollector:
    def fetch_technical_data(self, ticker: str, company_name: str):
        """
        yfinance에서 데이터를 가져와 기술적 지표를 계산하고 Document 형태로 반환합니다.
        """
        # 한국 시장 티커 처리 (.KS 또는 .KQ 추가 - 기본값 .KS)
        yf_ticker = f"{ticker}.KS" if not ticker.endswith((".KS", ".KQ")) else ticker
        
        print(f"📊 {company_name}({yf_ticker}) 차트 지표 계산 중...")

        try:
            df = yf.download(yf_ticker, period="3mo", interval="1d", progress=False)
            if df.empty:
                return []

            # 지표 계산 로직 (유저님 코드 그대로 적용)
            df['MA5'] = df['Close'].rolling(window=5).mean()
            df['MA20'] = df['Close'].rolling(window=20).mean()

            # RSI 계산
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            latest = df.iloc[-1]
            
            # 단일 값 추출 (유저님의 MultiIndex 방어 로직)
            def get_val(col):
                val = latest[col]
                return float(val.iloc[0]) if isinstance(val, pd.Series) else float(val)

            close_val = get_val('Close')
            ma5_val = get_val('MA5')
            ma20_val = get_val('MA20')
            rsi_val = get_val('RSI')
            vol_val = get_val('Volume')

            summary = f"""
            [기술적 지표 분석 결과]
            - 현재가: {close_val:,.2f}원
            - 5일 이동평균선: {ma5_val:,.2f}원
            - 20일 이동평균선: {ma20_val:,.2f}원
            - RSI (14일): {rsi_val:.2f} (30이하 과매도, 70이상 과매수)
            - 거래량: {vol_val:,.0f}주
            """

            # DB 저장을 위한 Document 객체 생성
            doc = Document(
                page_content=summary,
                metadata={
                    "ticker": ticker,
                    "company": company_name,
                    "source": "YFINANCE_CHART",
                    "category": "chart" # 차트 에이전트 전용 필터
                }
            )
            return [doc]

        except Exception as e:
            print(f"❌ 차트 데이터 수집 실패: {e}")
            return []