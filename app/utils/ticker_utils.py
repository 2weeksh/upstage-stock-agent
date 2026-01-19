import FinanceDataReader as fdr
import pandas as pd
import os
import time
from pathlib import Path

class TickerManager:
    _instance = None
    _ticker_map = {}
    # 캐시 파일 경로 설정
    CACHE_FILE = Path("tickers_cache.pkl")
    # 캐시 유지 시간 (예: 24시간)
    CACHE_EXPIRY = 24 * 60 * 60 

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TickerManager, cls).__new__(cls)
            cls._instance._initialize_data()
        return cls._instance

    def _initialize_data(self):
        # 1. 캐시 파일이 존재하고 최신인지 확인
        if self.CACHE_FILE.exists():
            file_age = time.time() - self.CACHE_FILE.stat().st_mtime
            if file_age < self.CACHE_EXPIRY:
                print("💾 로컬 캐시에서 종목 데이터를 불러옵니다...")
                self._ticker_map = pd.read_pickle(self.CACHE_FILE)
                print(f"✅ 총 {len(self._ticker_map)}개의 매핑 포인트 로드 완료.")
                return

        # 2. 캐시가 없거나 오래된 경우에만 새로 다운로드
        self._load_stock_data()

    def _load_stock_data(self):
        print("🌐 서버에서 글로벌 종목 데이터 동기화 중 (최초 1회)...")
        new_map = {}
        
        # 한국 시장 (KRX)
        df_krx = fdr.StockListing('KRX')
        for _, row in df_krx.iterrows():
            data = {'symbol': row['Code'], 'market': row['Market']}
            new_map[row['Code']] = data
            new_map[row['Name']] = data
            
        # 2. 미국 시장 확장 (AMEX 및 ETF/US 추가)
        # AMEX에는 TQQQ, SOXL 같은 파생 상품이 많이 포함되어 있습니다.
        for market in ['NASDAQ', 'NYSE', 'AMEX', 'ETF/US']:
            try:
                df_us = fdr.StockListing(market)
                for _, row in df_us.iterrows():
                    # ETF/US 데이터는 컬럼명이 'Symbol'인 경우가 많습니다.
                    symbol = row.get('Symbol', row.get('Code'))
                    name = row.get('Name')
                    
                    if symbol:
                        data = {'symbol': symbol, 'market': market}
                        new_map[symbol] = data
                        if name:
                            new_map[name] = data
            except Exception as e:
                print(f"⚠️ {market} 데이터 로드 건너뜀: {e}")

        # 결과 저장 및 파일 캐싱
        self._ticker_map = new_map
        pd.to_pickle(self._ticker_map, self.CACHE_FILE)
        print(f"✅ 동기화 완료 및 캐시 저장됨. (총 {len(self._ticker_map)}개)")

    def resolve(self, ticker_input: str) -> str:
        # 1. 입력값 정제 (공백 제거 및 대문자화)
        query = ticker_input.upper().strip()
        info = self._ticker_map.get(query)
        
        # 2. 캐시맵에서 검색 (완전 일치 혹은 이름 포함 검색)
        if not info:
            for name, data in self._ticker_map.items():
                if query in name:
                    info = data
                    break
        # 3. [핵심] 매핑 리스트에 없더라도 '티커 형식'이면 통과 (Smart Fallback)
        if not info:
            # 한국 주식 형식: 6자리 숫자 (예: 005930)
            if query.isdigit() and len(query) == 6:
                print(f"ℹ️ '{query}'를 리스트에서 찾지 못했지만 한국 티커 형식으로 간주하여 진행합니다.")
                return f"{query}.KS"
            
            # 미국 주식/ETF 형식: 1~5자리 대문자 (예: TQQQ, AAPL)
            if query.isalpha() and 1 <= len(query) <= 5:
                print(f"ℹ️ '{query}'를 리스트에서 찾지 못했지만 미국 티커 형식으로 간주하여 진행합니다.")
                return query
            
            raise ValueError(f"'{query}'에 해당하는 종목을 찾을 수 없습니다.")
            
        symbol = info['symbol']
        market = info['market']
        if market == 'KOSPI': return f"{symbol}.KS"
        if market in ['KOSDAQ', 'KONEX']: return f"{symbol}.KQ"
        return symbol

# 싱글톤 인스턴스 및 함수 정의는 동일
ticker_manager = TickerManager()
def get_clean_ticker(ticker_input: str) -> str:
    return ticker_manager.resolve(ticker_input)
