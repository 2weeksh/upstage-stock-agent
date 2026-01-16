import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_historical_chart_indicators(symbol: str, target_date: str):
    """
    특정 과거 날짜(target_date)를 기준으로 기술적 지표를 계산합니다.
    target_date 형식: 'YYYY-MM-DD'
    """
    ticker_symbol = symbol
    
    try:
        # 지표 계산(MA20, RSI14)을 위해 타겟 날짜보다 약 60일 전부터 데이터를 가져옵니다.
        end_dt = datetime.strptime(target_date, '%Y-%m-%d')
        start_dt = end_dt - timedelta(days=60)
        
        # yfinance는 end 날짜를 포함하지 않으므로 +1일을 해줍니다.
        fetch_end = (end_dt + timedelta(days=1)).strftime('%Y-%m-%d')
        fetch_start = start_dt.strftime('%Y-%m-%d')

        df = yf.download(ticker_symbol, start=fetch_start, end=fetch_end, progress=False)
        
        if df.empty:
            return f"'{ticker_symbol}'의 {target_date} 당시 데이터를 불러올 수 없습니다."

        # 기존 툴과 동일한 지표 계산 로직
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()

        # RSI 계산
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # 입력한 target_date와 가장 가까운 마지막 행(타겟 날짜 당일) 추출
        latest = df.iloc[-1]
        
        # MultiIndex 대응 및 단일 값 추출
        close_val = float(latest['Close'].iloc[0]) if isinstance(latest['Close'], pd.Series) else float(latest['Close'])
        ma5_val = float(latest['MA5'].iloc[0]) if isinstance(latest['MA5'], pd.Series) else float(latest['MA5'])
        ma20_val = float(latest['MA20'].iloc[0]) if isinstance(latest['MA20'], pd.Series) else float(latest['MA20'])
        rsi_val = float(latest['RSI'].iloc[0]) if isinstance(latest['RSI'], pd.Series) else float(latest['RSI'])
        vol_val = float(latest['Volume'].iloc[0]) if isinstance(latest['Volume'], pd.Series) else float(latest['Volume'])

        summary = f"""
        [{target_date} 당시 차트 데이터 정보]
        - 종가: {close_val:.2f}
        - 5일 이동평균선: {ma5_val:.2f}
        - 20일 이동평균선: {ma20_val:.2f}
        - RSI (14일): {rsi_val:.2f}
        - 거래량: {vol_val:,.0f}
        """
        return summary

    except Exception as e:
        return f"과거 차트 분석 중 오류 발생: {str(e)}"

if __name__ == "__main__":
    print(get_historical_chart_indicators("035720.KS", "2021-06-24")) # 카카오 고점일
    # print(get_historical_chart_indicators("000660.KS", "2023-02-01")) # SK하이닉스 저점일