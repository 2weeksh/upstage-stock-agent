import FinanceDataReader as fdr
import pandas as pd
from typing import Optional

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
        print("🔄 한국거래소(KRX) 종목 데이터 동기화 중...")
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
            print(f"✅ 총 {len(self._ticker_map)}개의 종목 로드 완료.")
        except Exception as e:
            print(f"❌ KRX 데이터 로드 중 오류 발생: {e}")

    def get_ticker(self, name: str) -> Optional[str]:
        """종목명을 입력받아 yfinance 포맷의 티커를 반환합니다."""
        stock_info = self._ticker_map.get(name)
        if not stock_info:
            return None
        
        code = stock_info['code']
        market = stock_info['market']
        
        # yfinance 호환을 위해 시장 구분자 추가
        if market == 'KOSPI':
            return f"{code}.KS"
        elif market == 'KOSDAQ':
            return f"{code}.KQ"
        else:
            return f"{code}.KS" # 기본값

# 싱글톤 인스턴스 생성
ticker_manager = TickerManager()

def get_clean_ticker(company_name: str) -> str:
    """최종적으로 에이전트들이 사용할 티커를 반환합니다."""
    ticker = ticker_manager.get_ticker(company_name)
    if not ticker:
        raise ValueError(f"'{company_name}'은(는) 상장된 종목이 아니거나 이름을 찾을 수 없습니다.")
    return ticker