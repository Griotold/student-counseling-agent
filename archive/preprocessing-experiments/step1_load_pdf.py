"""
PDF 로더 전체 비교 테스트
"""
from langchain_community.document_loaders import (
    PyPDFLoader,
    PDFPlumberLoader,
    PDFMinerLoader,
    UnstructuredPDFLoader,
)

def evaluate_quality(text, page_num):
    """텍스트 품질 평가"""
    score = 0
    issues = []
    
    # 1. 길이 체크
    if len(text) >= 1000:
        score += 3
    elif len(text) >= 500:
        score += 1
        issues.append(f"⚠️ 텍스트 짧음 ({len(text)}자)")
    else:
        issues.append(f"❌ 텍스트 너무 짧음 ({len(text)}자)")
    
    # 2. 페이지 번호 섞임 체크
    import re
    if re.search(r'^\d+\s+\d+', text):
        issues.append("❌ 페이지 번호 섞임")
    else:
        score += 2
    
    # 3. 핵심 키워드 포함
    keywords = ["자살", "징후", "대면", "면담"]
    found = sum(1 for kw in keywords if kw in text)
    if found >= 3:
        score += 2
    elif found >= 1:
        score += 1
    else:
        issues.append("❌ 핵심 키워드 부족")
    
    # 4. 구조 보존
    if re.search(r'[1-9]\.\s', text) or re.search(r'•', text):
        score += 1
    
    return score, issues

def test_loader(loader_name, loader_class):
    """로더 테스트 통합 함수"""
    print(f"\n{'='*80}")
    print(f"📄 {loader_name}")
    print('='*80)
    
    try:
        loader = loader_class("data/manual.pdf")
        pages = loader.load()
        
        test_pages = [10, 11, 17, 18]  # 핵심 페이지
        total_score = 0
        
        for page_num in test_pages:
            page = pages[page_num]
            text = page.page_content
            
            score, issues = evaluate_quality(text, page_num + 1)
            total_score += score
            
            print(f"\n페이지 {page_num + 1}:")
            print(f"  길이: {len(text)}자")
            print(f"  점수: {score}/8")
            
            if issues:
                for issue in issues:
                    print(f"  {issue}")
            
            print(f"\n  미리보기:")
            print(f"  {text[:200]}...")
        
        avg_score = total_score / len(test_pages)
        print(f"\n📊 평균 점수: {avg_score:.1f}/8")
        
        return pages, avg_score
        
    except ImportError as e:
        print(f"\n⚠️  {loader_name} 사용 불가")
        print(f"에러: {e}")
        print(f"설치 필요!")
        return None, 0
    except Exception as e:
        print(f"\n❌ {loader_name} 실행 실패")
        print(f"에러: {e}")
        return None, 0

def test_pdfminer_direct():
    """PDFMiner 직접 사용 (LangChain 래퍼 우회)"""
    print(f"\n{'='*80}")
    print(f"📄 PDFMiner (직접 호출)")
    print('='*80)
    
    try:
        from pdfminer.high_level import extract_pages
        from pdfminer.layout import LTTextContainer
        
        test_pages = [10, 11, 17, 18]
        total_score = 0
        
        for page_num in test_pages:
            text_parts = []
            
            # 페이지별 추출
            for page_layout in extract_pages(
                "data/manual.pdf", 
                page_numbers=[page_num]
            ):
                for element in page_layout:
                    if isinstance(element, LTTextContainer):
                        text_parts.append(element.get_text())
            
            text = ''.join(text_parts)
            
            score, issues = evaluate_quality(text, page_num + 1)
            total_score += score
            
            print(f"\n페이지 {page_num + 1}:")
            print(f"  길이: {len(text)}자")
            print(f"  점수: {score}/8")
            
            if issues:
                for issue in issues:
                    print(f"  {issue}")
            
            print(f"\n  미리보기:")
            print(f"  {text[:200]}...")
        
        avg_score = total_score / len(test_pages)
        print(f"\n📊 평균 점수: {avg_score:.1f}/8")
        
        return avg_score
        
    except ImportError:
        print("\n⚠️  pdfminer.six 미설치")
        print("설치: pip install pdfminer.six")
        return 0
    except Exception as e:
        print(f"\n❌ PDFMiner 실행 실패: {e}")
        import traceback
        traceback.print_exc()
        return 0
    
def test_pymupdf():
    """PyMuPDF 테스트 (LangChain 래퍼 없음)"""
    print(f"\n{'='*80}")
    print(f"📄 PyMuPDF (fitz)")
    print('='*80)
    
    try:
        import fitz
        
        doc = fitz.open("data/manual.pdf")
        test_pages = [10, 11, 17, 18]
        total_score = 0
        
        for page_num in test_pages:
            page = doc[page_num]
            text = page.get_text()
            
            score, issues = evaluate_quality(text, page_num + 1)
            total_score += score
            
            print(f"\n페이지 {page_num + 1}:")
            print(f"  길이: {len(text)}자")
            print(f"  점수: {score}/8")
            
            if issues:
                for issue in issues:
                    print(f"  {issue}")
            
            print(f"\n  미리보기:")
            print(f"  {text[:200]}...")
        
        avg_score = total_score / len(test_pages)
        print(f"\n📊 평균 점수: {avg_score:.1f}/8")
        
        doc.close()
        return avg_score
        
    except ImportError:
        print("\n⚠️  PyMuPDF 미설치")
        print("설치: pip install pymupdf")
        return 0
    except Exception as e:
        print(f"\n❌ PyMuPDF 실행 실패: {e}")
        return 0

def compare_all_loaders():
    """모든 로더 비교"""
    print("=" * 80)
    print("🔬 PDF 로더 전체 비교")
    print("=" * 80)
    
    results = {}
    
    # 1. PyPDFLoader
    _, score = test_loader("PyPDFLoader", PyPDFLoader)
    results['PyPDFLoader'] = score
    
    # 2. PDFPlumberLoader
    _, score = test_loader("PDFPlumberLoader", PDFPlumberLoader)
    results['PDFPlumberLoader'] = score
    
    # 3. PDFMinerLoader
    score = test_pdfminer_direct()
    results['PDFMiner'] = score
    
    # 4. UnstructuredPDFLoader
    _, score = test_loader("UnstructuredPDFLoader", UnstructuredPDFLoader)
    results['UnstructuredPDFLoader'] = score
    
    # 5. PyMuPDF
    score = test_pymupdf()
    results['PyMuPDF'] = score
    
    # 최종 비교
    print("\n" + "=" * 80)
    print("🏆 최종 순위")
    print("=" * 80)
    
    # 점수순 정렬
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n{'순위':<5} {'로더':<30} {'점수':<10}")
    print("-" * 50)
    
    for rank, (loader, score) in enumerate(sorted_results, 1):
        if score > 0:
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            print(f"{medal} {rank}위  {loader:<28} {score:.1f}/8")
    
    # 승자 결정
    winner_name, winner_score = sorted_results[0]
    
    print("\n" + "=" * 80)
    print("💡 최종 결정")
    print("=" * 80)
    
    threshold = 6.0
    
    if winner_score >= threshold:
        print(f"\n✅ {winner_name} 채택! (점수: {winner_score:.1f}/8)")
        print("\n품질 우수! 바로 다음 단계 진행")
        print("→ preprocessing/step2_preprocess.py")
    elif winner_score >= 4.0:
        print(f"\n⚠️  {winner_name} 선택 (점수: {winner_score:.1f}/8)")
        print("\n기준 미달이지만 가장 나음")
        print("→ 전처리 강화로 보완 필요")
        print("→ preprocessing/step2_preprocess.py")
    else:
        print(f"\n❌ 모든 로더 품질 불량 (최고: {winner_score:.1f}/8)")
        print("\n대안:")
        print("  1. 전처리 대폭 강화")
        print("  2. OCR 적용")
        print("  3. 수동 텍스트 추출")
    
    return winner_name, winner_score

if __name__ == "__main__":
    winner, score = compare_all_loaders()
    
    print(f"\n✨ 선택된 로더: {winner}")
    print(f"📊 최종 점수: {score:.1f}/8")