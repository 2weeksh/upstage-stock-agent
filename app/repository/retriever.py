from langchain_openai import ChatOpenAI
from langchain_upstage import UpstageEmbeddings
from langchain_community.vectorstores import Chroma

class StockRetriever:
    def __init__(self, db_path="chroma_db/"):
        self.embeddings = UpstageEmbeddings(model="solar-embedding-1-large")
        self.db = Chroma(persist_directory=db_path, embedding_function=self.embeddings)

    def search(self, query, source_type=None, k=3):
        """
        source_type: 'official' (재무), 'analyst' (뉴스/분석) 등 필터링
        """
        search_kwargs = {}
        if source_type:
            search_kwargs["filter"] = {"source_type": source_type}
        
        # 유사도 기반 검색 수행
        docs = self.db.similarity_search(query, k=k, **search_kwargs)
        return docs