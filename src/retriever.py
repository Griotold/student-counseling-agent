"""
Pinecone RAG 검색
"""
import os
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

load_dotenv()


class ManualRetriever:
    """매뉴얼 검색기"""
    
    def __init__(self, index_name: str = "student-counseling-0202"):
        """
        초기화
        
        Args:
            index_name: Pinecone 인덱스 이름
        """
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            dimensions=3072
        )
        
        self.vectorstore = PineconeVectorStore(
            index_name=index_name,
            embedding=self.embeddings
        )
    
    def search(self, query: str, k: int = 3) -> str:
        """
        매뉴얼 검색
        
        Args:
            query: 검색 쿼리
            k: 검색할 문서 수
            
        Returns:
            str: 검색된 컨텍스트 (포맷팅됨)
        """
        # 유사도 검색
        results = self.vectorstore.similarity_search(query, k=k)
        
        if not results:
            return ""
        
        # 컨텍스트 조합
        context_parts = []
        
        for i, doc in enumerate(results, 1):
            page = doc.metadata.get('page', '?')
            content = doc.page_content
            
            # 페이지 헤더 제거
            content = content.replace("=== 페이지", "\n페이지")
            content = content.replace("===", "").strip()
            
            context_parts.append(
                f"[참고 자료 {i} - 페이지 {page}]\n{content}"
            )
        
        return "\n\n---\n\n".join(context_parts)


# 테스트
if __name__ == "__main__":
    print("=" * 80)
    print("매뉴얼 검색 테스트")
    print("=" * 80)
    
    retriever = ManualRetriever()
    
    # 테스트 쿼리
    test_queries = [
        "죽고 싶다는 말을 들었을 때",
        "자살 징후는 무엇인가요",
        "부모님께 어떻게 알려야 하나요"
    ]
    
    for query in test_queries:
        print(f"\n질문: {query}")
        print("-" * 80)
        
        context = retriever.search(query, k=2)
        print(context[:300] + "...")
        print()