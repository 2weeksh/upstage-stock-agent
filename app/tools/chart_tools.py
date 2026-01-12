import yfinance as yf
import pandas as pd

def get_chart_indicators(symbol: str):
    """
    yfinance 데이터를 가져와 기술적 지표를 계산합니다.
    MultiIndex 에러를 방지하기 위해 단일 값 추출 로직을 강화했습니다.
    """
    ticker_symbol = f"{symbol}.KS" if not symbol.endswith((".KS", ".KQ")) else symbol
    
    try:
        # group_by='ticker' 설정을 피하고 단일 종목 데이터를 깔끔하게 가져옵니다.
        df = yf.download(ticker_symbol, period="3mo", interval="1d", progress=False)
        
        if df.empty:
            return "차트 데이터를 불러올 수 없습니다."

        # 지표 계산
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()

        # RSI 계산
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # 마지막 날의 데이터를 가져와 각 값을 명확하게 float으로 변환합니다.
        latest = df.iloc[-1]
        
        # Series 객체가 반환될 경우를 대비해 첫 번째 요소를 float으로 추출합니다.
        close_val = float(latest['Close'].iloc[0]) if isinstance(latest['Close'], pd.Series) else float(latest['Close'])
        ma5_val = float(latest['MA5'].iloc[0]) if isinstance(latest['MA5'], pd.Series) else float(latest['MA5'])
        ma20_val = float(latest['MA20'].iloc[0]) if isinstance(latest['MA20'], pd.Series) else float(latest['MA20'])
        rsi_val = float(latest['RSI'].iloc[0]) if isinstance(latest['RSI'], pd.Series) else float(latest['RSI'])
        vol_val = float(latest['Volume'].iloc[0]) if isinstance(latest['Volume'], pd.Series) else float(latest['Volume'])

        summary = f"""
        [최근 차트 데이터 정보]
        - 현재가: {close_val:.2f}
        - 5일 이동평균선: {ma5_val:.2f}
        - 20일 이동평균선: {ma20_val:.2f}
        - RSI (14일): {rsi_val:.2f}
        - 거래량: {vol_val:,.0f}
        """
        return summary

    except Exception as e:
        return f"차트 분석 도구 실행 중 오류 발생: {str(e)}"