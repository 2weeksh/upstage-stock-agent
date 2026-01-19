# tests/test_vector_search.py

from app.repository.chroma_db import get_vector_db

def verify_db_contents(ticker: str):
    print(f"🧐 {ticker} 벡터 DB 조회를 시작합니다...")
    
    # 1. DB 로드
    vector_db = get_vector_db(ticker)
    
    # 2. 저장된 데이터 개수 확인
    # get() 메서드로 모든 데이터를 가져와 개수를 셉니다.
    collection_data = vector_db.get()
    print(f"📊 총 저장된 청크 개수: {len(collection_data['ids'])}개")

    # 3. 실제 검색 테스트 (Similarity Search)
    query = "삼성전자의 주요 제품과 시장 점유율에 대해 알려줘"
    print(f"\n🔍 검색 질문: '{query}'")
    
    # k=2: 가장 유사한 조각 2개를 가져옵니다.
    # filter: 우리가 넣은 'category': 'common' 태그가 잘 작동하는지 확인
    results = vector_db.similarity_search(query, k=3, filter={"category": "common"})

    print("\n[검색 결과]")
    for i, doc in enumerate(results):
        print(f"--- 조각 {i+1} ---")
        print(f"📍 출처: {doc.metadata.get('source')} / 보고서: {doc.metadata.get('report_title')}")
        print(f"📄 내용 미리보기: {doc.page_content[:200]}...")
        print("-" * 30)

from app.repository.chroma_db import get_vector_db

def check_news(ticker: str):
    vector_db = get_vector_db(ticker)
    
    # 1. 뉴스 데이터만 필터링해서 검색
    # 질문은 뉴스 내용과 관련 있을 법한 것으로 던져봅니다.
    query = "삼성전자 최근 소식 및 시장 반응"
    print(f"🔍 뉴스 카테고리 검색 결과 ('{query}'):\n")
    
    results = vector_db.similarity_search(
        query, 
        k=5, 
        filter={"category": "news"} # 뉴스만 골라내기!
    )

    for i, doc in enumerate(results):
        print(f"--- [뉴스 {i+1}] ---")
        print(f"📍 출처: {doc.metadata.get('source')} / URL: {doc.metadata.get('url')}")
        print(f"📄 내용: {doc.page_content[:300]}...") # 앞부분 300자 출력
        print("-" * 50)

if __name__ == "__main__":
    # 아까 저장한 삼성전자 티커로 확인
    #verify_db_contents("005930")
    # 뉴스 데이터만 잘 들어갔는지 확인
    check_news("005930")