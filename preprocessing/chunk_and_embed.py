"""
청킹 및 임베딩
data/all_pages_txt/ 의 txt 파일들을 청킹하고 Pinecone에 임베딩
"""
import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def load_all_texts():
    """모든 txt 파일 로드"""
    print("=" * 80)
    print("📂 txt 파일 로드")
    print("=" * 80)
    
    txt_dir = Path("data/all_pages_txt")
    txt_files = sorted(txt_dir.glob("page_*.txt"))
    
    documents = []
    
    for txt_file in txt_files:
        with open(txt_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 메타데이터 포함
        page_num = txt_file.stem.split('_')[1]
        
        documents.append({
            'text': text,
            'metadata': {
                'source': str(txt_file),
                'page': int(page_num)
            }
        })
        
        print(f"✅ {txt_file.name}: {len(text)}자")
    
    print(f"\n총 {len(documents)}개 파일 로드 완료")
    total_chars = sum(len(doc['text']) for doc in documents)
    print(f"총 글자수: {total_chars:,}자")
    
    return documents

def chunk_documents(documents):
    """문서 청킹"""
    print("\n" + "=" * 80)
    print("✂️  텍스트 청킹")
    print("=" * 80)
    
    # 청킹 설정
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,        # 청크 크기
        chunk_overlap=200,      # 중복 크기
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    
    all_chunks = []
    
    for doc in documents:
        # 청킹
        chunks = text_splitter.split_text(doc['text'])
        
        # 메타데이터 포함
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                'text': chunk,
                'metadata': {
                    **doc['metadata'],
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
            })
        
        print(f"페이지 {doc['metadata']['page']}: {len(chunks)}개 청크 생성")
    
    print(f"\n총 {len(all_chunks)}개 청크 생성")
    
    # 청크 크기 분포 확인
    chunk_sizes = [len(chunk['text']) for chunk in all_chunks]
    avg_size = sum(chunk_sizes) / len(chunk_sizes)
    min_size = min(chunk_sizes)
    max_size = max(chunk_sizes)
    
    print(f"\n청크 크기:")
    print(f"  평균: {avg_size:.0f}자")
    print(f"  최소: {min_size}자")
    print(f"  최대: {max_size}자")
    
    return all_chunks

def embed_and_store(chunks):
    """임베딩 및 Pinecone 저장"""
    print("\n" + "=" * 80)
    print("🔢 임베딩 및 Pinecone 저장")
    print("=" * 80)
    
    # OpenAI Embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        dimensions=3072
    )
    
    # Pinecone 초기화
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "student-counseling-0202"
    
    print(f"\n인덱스: {index_name}")
    print(f"임베딩 모델: text-embedding-3-large (3072차원)")
    print(f"청크 수: {len(chunks)}")
    
    # LangChain Document 형식으로 변환
    from langchain.schema import Document
    
    docs = [
        Document(
            page_content=chunk['text'],
            metadata=chunk['metadata']
        )
        for chunk in chunks
    ]
    
    # Pinecone에 저장
    print("\n임베딩 중... (약 30초-1분 소요)")
    
    vectorstore = PineconeVectorStore.from_documents(
        documents=docs,
        embedding=embeddings,
        index_name=index_name
    )
    
    print("✅ Pinecone 저장 완료!")
    
    return vectorstore

def verify_pinecone():
    """Pinecone 저장 확인"""
    print("\n" + "=" * 80)
    print("✓ Pinecone 저장 확인")
    print("=" * 80)
    
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index("student-counseling-0202")
    
    stats = index.describe_index_stats()
    
    print(f"\n인덱스 통계:")
    print(f"  총 벡터 수: {stats['total_vector_count']}")
    print(f"  차원: {stats['dimension']}")
    
    # 테스트 검색
    print("\n" + "=" * 80)
    print("🔍 테스트 검색")
    print("=" * 80)
    
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        dimensions=3072
    )
    
    vectorstore = PineconeVectorStore(
        index_name="student-counseling-0202",
        embedding=embeddings
    )
    
    # 테스트 쿼리
    test_queries = [
        "자살 징후는 무엇인가요?",
        "학생이 죽고 싶다고 말하면 어떻게 해야 하나요?",
        "부모에게 어떻게 알려야 하나요?"
    ]
    
    for query in test_queries:
        print(f"\n질문: {query}")
        results = vectorstore.similarity_search(query, k=2)
        
        for i, doc in enumerate(results, 1):
            print(f"\n  결과 {i}:")
            print(f"    페이지: {doc.metadata.get('page')}")
            print(f"    내용: {doc.page_content[:100]}...")

def main():
    print("=" * 80)
    print("🚀 청킹 및 임베딩 파이프라인")
    print("=" * 80)
    
    # 1. txt 파일 로드
    documents = load_all_texts()
    
    # # 2. 청킹
    chunks = chunk_documents(documents)
    
    # # 3. 임베딩 및 저장
    vectorstore = embed_and_store(chunks)
    
    # 4. 확인
    verify_pinecone()
    
    print("\n" + "=" * 80)
    print("✨ 완료!")
    print("=" * 80)
    print("\n다음 단계:")
    print("  1. Agent 실행")
    print("  2. 테스트")

if __name__ == "__main__":
    main()