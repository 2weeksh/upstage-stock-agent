import yfinance as yf

def get_financial_summary(ticker: str) -> str:
    """
    특정 종목의 핵심 재무 지표를 가져와 요약된 텍스트로 반환합니다.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # 1. 밸류에이션 지표 (Valuation)
        market_cap = info.get('marketCap', 'N/A')
        per = info.get('trailingPE', 'N/A')
        pbr = info.get('priceToBook', 'N/A')
        
        # 2. 수익성 지표 (Profitability)
        roe = info.get('returnOnEquity', 'N/A')
        profit_margins = info.get('profitMargins', 'N/A') # 순이익률
        
        # 3. 성장성 및 재무 건전성 (Growth & Health)
        revenue_growth = info.get('revenueGrowth', 'N/A')
        debt_to_equity = info.get('debtToEquity', 'N/A') # 부채비율
        free_cashflow = info.get('freeCashflow', 'N/A')

        # LLM이 읽기 편한 포맷으로 정리
        report = f"""
        [Financial Report for {ticker}]
        1. Valuation:
           - Market Cap: {market_cap}
           - PER (Price-to-Earnings): {per}
           - PBR (Price-to-Book): {pbr}
        
        2. Profitability:
           - ROE (Return on Equity): {roe}
           - Net Profit Margin: {profit_margins}
        
        3. Financial Health:
           - Revenue Growth (YoY): {revenue_growth}
           - Debt-to-Equity Ratio: {debt_to_equity}
           - Free Cash Flow: {free_cashflow}
        """
        return report

    except Exception as e:
        return f"Error fetching financial data for {ticker}: {str(e)}"