import FinanceDataReader as fdr
import pandas as pd
from typing import Optional

# app/utils/ticker_utils.py 개선

class TickerManager:
    _instance = None
    _ticker_map = {}


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TickerManager, cls).__new__(cls)
            cls._instance._load_stock_data()
        return cls._instance


    def _load_stock_data(self):
        print("🔄 글로벌 종목 데이터(KRX, NASDAQ, NYSE) 동기화 중...")
        # 1. 한국 시장 (KRX)
        df_krx = fdr.StockListing('KRX')
        for _, row in df_krx.iterrows():
            self._ticker_map[row['Code']] = {'market': row['Market']}
            
        # 2. 미국 시장 (NASDAQ, NYSE)
        for market in ['NASDAQ', 'NYSE']:
            df_us = fdr.StockListing(market)
            for _, row in df_us.iterrows():
                self._ticker_map[row['Symbol']] = {'market': market}
        print(f"✅ 총 {len(self._ticker_map)}개의 글로벌 종목 로드 완료.")
            

    def resolve(self, ticker_input: str) -> str:
        ticker = ticker_input.upper().strip()
        info = self._ticker_map.get(ticker)
        
        if not info:
            raise ValueError(f"'{ticker}'은(는) 유효한 티커가 아닙니다.")
            
        market = info['market']
        if market == 'KOSPI': return f"{ticker}.KS"
        if market == 'KOSDAQ': return f"{ticker}.KQ"
        return ticker # 미국 주식(NASDAQ, NYSE)은 그대로 반환

# 싱글톤 인스턴스 생성
ticker_manager = TickerManager()

# 외부에서 import 할 함수 정의 (에러 해결 핵심)
def get_clean_ticker(ticker_input: str) -> str:
    return ticker_manager.resolve(ticker_input)





'''
class TickerManager:
    _instance = None
    _ticker_map = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TickerManager, cls).__new__(cls)
            cls._instance._load_krx_data()
        return cls._instance

    def _load_krx_data(self):
        """한국거래소(KRX) 전체 종목 리스트를 불러와 매핑 테이블을 생성합니다."""
        print("🔄 글로벌 종목 데이터 동기화 중...")
        try:
            # KRX 전체 종목 리스트 (KOSPI, KOSDAQ, KONEX 포함)
            df_krx = fdr.StockListing('KRX')
            
            # 종목명(Name)을 Key로, 티커(Code)와 시장(Market) 정보를 Value로 저장
            # 예: {'삼성전자': {'code': '005930', 'market': 'KOSPI'}}
            for _, row in df_krx.iterrows():
                self._ticker_map[row['Name']] = {
                    'code': row['Code'],
                    'market': row['Market']
                }

            # 2. 미국 시장 로드 (NASDAQ, NYSE)
            # ⚠️ 미국 주식은 종목이 매우 많으므로 주요 시장 위주로 추가합니다.
            for market in ['NASDAQ', 'NYSE']:
                df_us = fdr.StockListing(market)
                for _, row in df_us.iterrows():
                    # 미국 주식은 보통 'Symbol'이 티커, 'Name'이 회사명입니다.
                    self._ticker_map[row['Name']] = {
                        'code': row['Symbol'], 
                        'market': market
                    }

            print(f"✅ 총 {len(self._ticker_map)}개의 종목 로드 완료.")
        except Exception as e:
            print(f"❌ 데이터 로드 중 오류 발생: {e}")

    def get_ticker(self, name: str) -> Optional[str]:
        """종목명을 입력받아 yfinance 포맷의 티커를 반환합니다."""
        stock_info = self._ticker_map.get(name)
        if not stock_info:
            return None
        
        # 시장별 접미사 처리
        code = stock_info['code']
        market = stock_info['market']
        
        # yfinance 호환을 위해 시장 구분자 추가
        if market == 'KOSPI':
            return f"{code}.KS"
        if market == 'KOSDAQ':
            return f"{code}.KQ"
        return code

# 싱글톤 인스턴스 생성
ticker_manager = TickerManager()

def get_clean_ticker(company_name: str) -> str:
    """최종적으로 에이전트들이 사용할 티커를 반환합니다."""
    ticker = ticker_manager.get_ticker(company_name)
    if not ticker:
        raise ValueError(f"'{company_name}'은(는) 상장된 종목이 아니거나 이름을 찾을 수 없습니다.")
    return ticker
'''