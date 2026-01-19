"""
data에 있는 pdf파일을 임베딩 후 벡터 DB에 저장하는 모듈
"""

import os
import shutil

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_upstage import UpstageEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv() # .env 파일에서 환경변수 로드

# 설정 (API 키 등)
api_key = os.getenv("UPSTAGE_API_KEY")
# API 키가 없으면 에러 발생
if not api_key:
    raise ValueError("UPSTAGE_API_KEY 환경변수가 설정되지 않았습니다.")

DATA_PATH = "data/"
DB_PATH = "chroma_db/"

embeddings = UpstageEmbeddings(model="solar-embedding-1-large")

def ingest_docs():
    """PDF 문서를 로드, 분할, 임베딩 후 벡터 DB에 저장하는 함수"""

    # 1. 기존 DB 폴더 삭제 (초기화)
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
        print(f"기존 DB 폴더 '{DB_PATH}'가 삭제되었습니다.")

    # PDF 파일 목록 및 타입 정의 (메타데이터용)
    files = [
        {"name": "[삼성전자]분기보고서(2025.11.14).pdf", "type": "official", "date": "2025-09-30"},
        {"name": "20260109_Eugene_Samsung.pdf", "type": "analyst", "date": "2026-01-09"},
        {"name": "20260108_Meritz_Samsung.pdf", "type": "analyst", "date": "2026-01-08"},
    ]

    all_splits = []
    
    # 텍스트 분할기 (Chunk 크기 조절)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    for file_info in files:
        loader = PyPDFLoader(os.path.join(DATA_PATH, file_info["name"]))
        docs = loader.load()

        # 메타데이터 주입
        for doc in docs:
            doc.metadata["source_type"] = file_info["type"]
            doc.metadata["publish_date"] = file_info["date"]
        
        splits = text_splitter.split_documents(docs)
        all_splits.extend(splits)
        print(f"✅ {file_info['name']} 로드 완료 (Chunks: {len(splits)})")

    # 3. Vector DB 저장
    vectorstore = Chroma.from_documents(
        documents=all_splits,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    print(f"\n모든 데이터가 {DB_PATH}에 저장되었습니다!")

if __name__ == "__main__":
    ingest_docs()