# app/repository/chroma_db.py

import os
from langchain_chroma import Chroma
from langchain_upstage import UpstageEmbeddings
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = "chroma_db"

def get_vector_db(ticker: str):
    """
    고정된 물리 경로(chroma_db) 내에서 
    종목별 논리 서랍(collection_name)을 생성하여 반환합니다.
    """
    
    # 2. 임베딩 모델 설정 (Upstage 모델 사용)
    # .env에 UPSTAGE_API_KEY가 있어야 합니다.
    embeddings = UpstageEmbeddings(model="embedding-query")
    

    # Chroma 컬렉션 이름은 반드시 알파벳으로 시작해야 하므로 'ticker_'를 붙여줍니다.
    clean_ticker = ticker.replace('.', '_').upper()
    collection_name = f"ticker_{clean_ticker}"

    # 3. Chroma DB 객체 생성 및 반환
    # 폴더가 없으면 새로 생성하고, 있으면 기존 데이터를 로드합니다.
    vector_db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=collection_name
    )
    
    print(f"DB 연결 완료 | 물리 경로: {CHROMA_PATH} | 컬렉션: {collection_name}")

    return vector_db