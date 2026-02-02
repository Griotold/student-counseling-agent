import os
import re
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

load_dotenv()

def load_manual_pdf():
    """매뉴얼 PDF 로드"""
    print("\n[STEP 1] 📂 PDF 로딩 중...")
    
    pdf_path = "data/manual.pdf"
    reader = PdfReader(pdf_path)
    
    print(f"✅ PDF 로드 완료: {len(reader.pages)}페이지")
    
    return reader

def clean_text(text):
    """텍스트 전처리"""
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # 1. 숫자만 있는 줄 제거 (페이지 번호)
        if line.strip().isdigit():
            continue
        
        # 2. 너무 짧은 줄 제거 (5자 미만)
        if len(line.strip()) < 5:
            continue
        
        # 3. 특수문자만 있는 줄 제거
        if re.match(r'^[\s\W]+$', line):
            continue
        
        cleaned_lines.append(line.strip())
    
    # 4. 텍스트 재조합
    cleaned_text = '\n'.join(cleaned_lines)
    
    # 5. 다중 개행 정리 (3개 이상 → 2개)
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    # 6. 다중 공백 정리
    cleaned_text = re.sub(r' {2,}', ' ', cleaned_text)
    
    return cleaned_text

def extract_core_pages(reader):
    """핵심 페이지 추출 + 전처리"""
    print("\n[STEP 2] 🔍 핵심 페이지 추출 및 전처리 중...")
    
    # 핵심 페이지 (0-based index)
    core_pages = [
        10, 11, 12, 13,  # 자살 징후 (p.11-14)
        17, 18, 19,      # 대면 면담 예시 (p.18-20)
        23, 24, 25,      # 위기 개입 (p.24-26)
        26, 27, 28, 29   # 위험요인/보호요인 (p.27-30)
    ]
    
    documents = []
    
    for page_num in core_pages:
        try:
            page = reader.pages[page_num]
            text = page.extract_text()
            
            # 텍스트 전처리
            cleaned_text = clean_text(text)
            
            # 최소 길이 체크 (100자 미만은 제외)
            if len(cleaned_text) < 100:
                print(f"⚠️  페이지 {page_num + 1}: 텍스트가 너무 짧음 ({len(cleaned_text)}자) - 건너뜀")
                continue
            
            doc = Document(
                page_content=cleaned_text,
                metadata={
                    "page": page_num + 1,  # 1-based for display
                    "source": "학생자살위기대응매뉴얼"
                }
            )
            documents.append(doc)
            
            print(f"✅ 페이지 {page_num + 1}: {len(cleaned_text)}자 추출")
            
        except Exception as e:
            print(f"⚠️  페이지 {page_num + 1} 추출 실패: {e}")
    
    print(f"\n✅ {len(documents)}개 페이지 추출 완료")
    
    return documents

def chunk_documents(documents):
    """문서 청킹"""
    print("\n[STEP 3] ✂️  청킹 중...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,       # 1000 → 1500 (증가)
        chunk_overlap=200,     # 150 → 200 (증가)
        separators=[
            "\n\n",  # 단락 구분
            "\n",    # 줄바꿈
            "。",    # 한국어 마침표
            ".",     # 영어 마침표
            "!",     # 느낌표
            "?",     # 물음표
            " ",     # 공백
            ""       # 문자
        ]
    )
    
    chunks = text_splitter.split_documents(documents)
    
    print(f"✅ {len(chunks)}개 청크 생성 완료")
    
    # 청크 샘플 확인 (처음 3개)
    if chunks:
        print(f"\n=== 청크 샘플 확인 (처음 3개) ===")
        for i, chunk in enumerate(chunks[:3], 1):
            print(f"\n[청크 {i}]")
            print(f"  페이지: {chunk.metadata.get('page', 'N/A')}")
            print(f"  길이: {len(chunk.page_content)}자")
            print(f"  내용: {chunk.page_content[:150]}...")
    
    return chunks

def embed_to_pinecone(chunks):
    """Pinecone에 임베딩"""
    print("\n[STEP 4] 🚀 Pinecone에 임베딩 중...")
    
    # 환경 변수 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY가 .env 파일에 없습니다.")
        return None
    
    if not os.getenv("PINECONE_API_KEY"):
        print("❌ PINECONE_API_KEY가 .env 파일에 없습니다.")
        return None
    
    # 임베딩 모델
    embedding = OpenAIEmbeddings(model='text-embedding-3-large')
    
    # Pinecone 인덱스 확인
    index_name = 'student-counseling-manual'
    
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    existing_indexes = [index.name for index in pc.list_indexes()]
    
    if index_name not in existing_indexes:
        print(f"\n❌ 인덱스 '{index_name}'가 존재하지 않습니다.")
        print("\n📝 Pinecone 콘솔에서 인덱스를 생성해주세요:")
        print(f"   - Index Name: {index_name}")
        print(f"   - Dimensions: 3072 (text-embedding-3-large)")
        print(f"   - Metric: cosine")
        print(f"   - Cloud: AWS")
        print(f"   - Region: us-east-1")
        return None
    
    print(f"✅ 인덱스 확인: {index_name}")
    
    # 임베딩 & 업로드
    print(f"⏳ 임베딩 중... (약 10-20초 소요)")
    
    vectorstore = PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embedding,
        index_name=index_name
    )
    
    print(f"✅ {len(chunks)}개 청크 임베딩 완료!")
    
    return vectorstore

def verify_embeddings():
    """임베딩 검증"""
    print("\n[STEP 5] 🔍 임베딩 검증 중...")
    
    embedding = OpenAIEmbeddings(model='text-embedding-3-large')
    index_name = 'student-counseling-manual'
    
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embedding
    )
    
    # 테스트 쿼리
    test_queries = [
        "자살 징후는 무엇인가요?",
        "학생과 대면 면담 시 주의사항",
        "부모님께 어떻게 전달하나요?"
    ]
    
    print("\n=== 검증 테스트 ===")
    for query in test_queries:
        print(f"\n📝 테스트: '{query}'")
        results = vectorstore.similarity_search(query, k=2)
        
        if results:
            print(f"✅ {len(results)}개 결과 발견")
            print(f"   페이지: {results[0].metadata.get('page', 'N/A')}")
            print(f"   길이: {len(results[0].page_content)}자")
            print(f"   내용: {results[0].page_content[:200]}...")
        else:
            print("❌ 결과 없음")
    
    print("\n✅ 검증 완료!")

def main():
    print("=" * 80)
    print("🎓 학생 자살위기 대응 매뉴얼 임베딩 (최종본)")
    print("=" * 80)
    
    try:
        # 1. PDF 로드
        reader = load_manual_pdf()
        
        # 2. 핵심 페이지 추출 + 전처리
        documents = extract_core_pages(reader)
        
        if not documents:
            print("\n❌ 추출된 문서가 없습니다.")
            return
        
        # 3. 청킹
        chunks = chunk_documents(documents)
        
        # 4. Pinecone 임베딩
        vectorstore = embed_to_pinecone(chunks)
        
        if vectorstore:
            # 5. 검증
            verify_embeddings()
            
            print("\n" + "=" * 80)
            print("🎉 완료! 이제 챗봇을 실행할 수 있습니다.")
            print("💡 다음 단계:")
            print("   1. 검증 결과 확인")
            print("   2. Pinecone 콘솔에서 데이터 확인")
            print("   3. streamlit run app.py")
            print("=" * 80)
        
    except FileNotFoundError:
        print("\n❌ PDF 파일을 찾을 수 없습니다:")
        print("   data/manual.pdf")
        print("\n💡 파일을 data/ 폴더에 넣고 다시 시도하세요.")
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()