import yfinance as yf
import pandas as pd
import requests as standard_requests # 네이버용 (일반 requests)
from curl_cffi import requests as curl_requests # 야후용 (강력한 우회 requests)
import re
import sys
import urllib3

# -----------------------------------------------------------
# [블로그 솔루션 적용: curl_cffi]
# 크롬 브라우저(impersonate="chrome")인 척하는 강력한 세션을 만듭니다.
# 이 세션을 yfinance에 주입하면 차단과 SSL 에러를 동시에 뚫습니다.
# -----------------------------------------------------------
chrome_session = curl_requests.Session(impersonate="chrome")

# SSL 경고 끄기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_financial_summary(ticker: str) -> str:
    """
    [최종 솔루션: curl_cffi 적용]
    - 한국 주식: 네이버 금융 (기존 방식 유지)
    - 미국 주식: yfinance + curl_cffi (브라우저 위장술로 차단/에러 해결)
    """
    try:
        ticker = ticker.strip().upper()

        # 1. 한국 주식 (숫자 6자리) -> 네이버
        if re.match(r'^\d{6}(\.KS|\.KQ)?$', ticker):
            return _get_naver_finance(ticker)
        
        # 2. 미국 주식 -> yfinance (curl_cffi 세션 주입)
        else:
            return _get_yahoo_with_curl(ticker)

    except Exception as e:
        print(f"❌ Critical Error: {e}", file=sys.stderr)
        return f"Error analyzing {ticker}: {str(e)}"

def _get_naver_finance(ticker: str):
    """[한국] 네이버 금융"""
    try:
        code = re.sub(r'[^0-9]', '', ticker)
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # 네이버는 일반 requests로 verify=False 해서 가져옴 (가장 안정적)
        response = standard_requests.get(url, headers=headers, verify=False)
        dfs = pd.read_html(response.text)
        
        fin_df = None
        for df in dfs:
            if '매출액' in str(df) or '영업이익' in str(df):
                fin_df = df
                break
        
        if fin_df is None: return f"Error: 데이터 없음 ({code})"

        print(f"✅ [네이버] {code} 데이터 수집 성공")
        return f"[Financial Report for {code} (Naver)]\n{fin_df.fillna('-').to_string()}"
    except Exception as e:
        return f"네이버 에러: {str(e)}"

def _get_yahoo_with_curl(ticker: str):
    """[미국] yfinance + curl_cffi (Chrome 위장)"""
    try:
        # -------------------------------------------------------
        # [핵심] session=chrome_session 전달!
        # 이제 yfinance는 '파이썬'이 아니라 '크롬 브라우저'로서 데이터를 요청합니다.
        # -------------------------------------------------------
        stock = yf.Ticker(ticker, session=chrome_session)
        
        info = stock.info
        
        if not info or len(info) < 5: return f"Error: 데이터 없음 ({ticker})"

        print(f"✅ [야후+Chrome위장] {ticker} 데이터 수집 성공!")

        def get_val(key): return info.get(key, 'N/A')

        return f"""
        [Financial Report for {ticker} (Source: Yahoo Finance)]
        * Method: curl_cffi (TLS Bypass)
        
        1. Valuation:
           - Market Cap: {get_val('marketCap')}
           - PER: {get_val('trailingPE')}
           - PBR: {get_val('priceToBook')}
        
        2. Financials:
           - Total Revenue: {get_val('totalRevenue')}
           - Net Income: {get_val('netIncomeToCommon')}
           - ROE: {get_val('returnOnEquity')}
           
        3. Cash Flow:
           - Free Cash Flow: {get_val('freeCashflow')}
           - Total Debt: {get_val('totalDebt')}
        """
    except Exception as e:
        return f"yfinance(curl) 에러: {str(e)}"