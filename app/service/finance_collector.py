# app/service/finance_collector.py

import yfinance as yf
import pandas as pd
import requests as standard_requests
from curl_cffi import requests as curl_requests
import re
import urllib3
from langchain_core.documents import Document

# SSL 경고 끄기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FinanceCollector:
    def __init__(self):
        # 야후 파이낸스 차단 방지용 세션
        self.chrome_session = curl_requests.Session(impersonate="chrome")

    def fetch_financial_summary(self, ticker: str, company_name: str):
        """
        [통합 재무 데이터 수집]
        한국 주식은 네이버에서, 해외 주식은 야후에서 가져와 Document로 반환합니다.
        """
        ticker = ticker.strip().upper()
        print(f"💰 {company_name}({ticker}) 핵심 재무 지표 수집 중...")

        try:
            # 1. 한국 주식 판별 (숫자 6자리 포함 여부)
            if re.search(r'\d{6}', ticker):
                content, source = self._get_naver_finance(ticker), "NAVER_FINANCE"
            else:
                content, source = self._get_yahoo_finance(ticker), "YAHOO_FINANCE"

            if "❌" in content or "⚠️" in content:
                return []

            # 2. Document 객체 생성 (category: finance)
            doc = Document(
                page_content=content,
                metadata={
                    "ticker": ticker,
                    "company": company_name,
                    "source": source,
                    "category": "finance" # 재무 분석가 전용 카테고리
                }
            )
            return [doc]

        except Exception as e:
            print(f"❌ 재무 데이터 수집 중 오류: {e}")
            return []

    def _get_naver_finance(self, ticker: str):
        """[한국] 네이버 금융 크롤링"""
        try:
            code = re.sub(r'[^0-9]', '', ticker)
            url = f"https://finance.naver.com/item/main.naver?code={code}"
            
            response = standard_requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
            dfs = pd.read_html(response.text)
            
            fin_df = next((df for df in dfs if '매출액' in str(df) or '영업이익' in str(df)), None)
            
            if fin_df is None:
                return f"⚠️ [네이버] {code} 데이터를 찾을 수 없습니다."

            # 테이블 가독성 정리
            report = fin_df.fillna('-').to_string()
            return f"### [Naver Financial Summary: {ticker}]\n{report}"
        except Exception as e:
            return f"❌ 네이버 수집 에러: {str(e)}"

    def _get_yahoo_finance(self, ticker: str):
        """[미국/ETF] yfinance 사용"""
        try:
            stock = yf.Ticker(ticker, session=self.chrome_session)
            info = stock.info
            
            if not info or len(info) < 5:
                return f"⚠️ [야후] {ticker} 데이터를 가져올 수 없습니다."

            v = info.get
            return f"""
### [Yahoo Financial Summary: {ticker}]
1. Valuation:
   - Market Cap: {v('marketCap', 'N/A')}
   - Trailing PER: {v('trailingPE', 'N/A')}
   - Forward PER: {v('forwardPE', 'N/A')}
   - PBR: {v('priceToBook', 'N/A')}
2. Profitability:
   - Revenue: {v('totalRevenue', 'N/A')}
   - Net Income: {v('netIncomeToCommon', 'N/A')}
   - ROE: {v('returnOnEquity', 'N/A')}
   - Operating Margin: {v('operatingMargins', 'N/A')}
3. Cash & Debt:
   - Free Cash Flow: {v('freeCashflow', 'N/A')}
   - Total Debt: {v('totalDebt', 'N/A')}
   - Current Ratio: {v('currentRatio', 'N/A')}
            """.strip()
        except Exception as e:
            return f"❌ 야후(yfinance) 에러: {str(e)}"