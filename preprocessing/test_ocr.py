"""
OCR 테스트 스크립트
단일 페이지로 먼저 테스트
"""
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

def test_single_page():
    """단일 페이지 OCR 테스트"""
    print("=" * 80)
    print("📸 OCR 테스트 - 페이지 11")
    print("=" * 80)
    
    try:
        # 1. PDF → 이미지 변환
        print("\n[1/3] PDF를 이미지로 변환 중...")
        images = convert_from_path(
            "data/manual.pdf",
            first_page=11,
            last_page=11,
            dpi=300  # 해상도 (높을수록 정확, 느림)
        )
        
        print(f"✅ 이미지 변환 완료: {len(images)}개")
        
        # 2. OCR 실행
        print("\n[2/3] OCR 텍스트 추출 중...")
        print("⏳ 약 5-10초 소요...")
        
        text = pytesseract.image_to_string(
            images[0],
            lang='kor+eng',  # 한국어 + 영어
            config='--psm 6'  # Page Segmentation Mode
        )
        
        print(f"✅ OCR 완료: {len(text)}자 추출")
        
        # 3. 결과 출력
        print("\n[3/3] 결과 확인")
        print("=" * 80)
        print(f"추출 길이: {len(text)}자")
        print("\n미리보기 (처음 500자):")
        print("-" * 80)
        print(text[:500])
        print("-" * 80)
        
        # 4. 품질 평가
        print("\n📊 품질 평가:")
        
        keywords = ["자살", "징후", "대면", "면담", "학생"]
        found = sum(1 for kw in keywords if kw in text)
        
        print(f"  핵심 키워드: {found}/{len(keywords)}개 발견")
        
        if len(text) >= 1500:
            print(f"  ✅ 길이: 충분 ({len(text)}자)")
        elif len(text) >= 1000:
            print(f"  ⚠️  길이: 보통 ({len(text)}자)")
        else:
            print(f"  ❌ 길이: 부족 ({len(text)}자)")
        
        # 5. 파일 저장
        with open("data/ocr_test_page11.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print(f"\n💾 저장: data/ocr_test_page11.txt")
        
        return text
        
    except Exception as e:
        print(f"\n❌ OCR 실패: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_loaders_vs_ocr():
    """기존 로더 vs OCR 비교"""
    print("\n" + "=" * 80)
    print("📊 로더 vs OCR 비교 (페이지 11)")
    print("=" * 80)
    
    # 1. PyPDF
    from langchain_community.document_loaders import PyPDFLoader
    pypdf_loader = PyPDFLoader("data/manual.pdf")
    pypdf_pages = pypdf_loader.load()
    pypdf_text = pypdf_pages[10].page_content
    
    # 2. PDFPlumber
    from langchain_community.document_loaders import PDFPlumberLoader
    plumber_loader = PDFPlumberLoader("data/manual.pdf")
    plumber_pages = plumber_loader.load()
    plumber_text = plumber_pages[10].page_content
    
    # 3. OCR
    ocr_text = test_single_page()
    
    # 비교
    print("\n" + "=" * 80)
    print("📈 비교 결과")
    print("=" * 80)
    
    print(f"\n{'로더':<20} {'길이':<10} {'품질 예상'}")
    print("-" * 50)
    print(f"PyPDFLoader          {len(pypdf_text):<10} 2.0/8")
    print(f"PDFPlumberLoader     {len(plumber_text):<10} 4.0/8")
    print(f"OCR                  {len(ocr_text) if ocr_text else 0:<10} ???")
    
    if ocr_text and len(ocr_text) > len(plumber_text):
        improvement = (len(ocr_text) / len(plumber_text) - 1) * 100
        print(f"\n✅ OCR이 PDFPlumber보다 {improvement:.0f}% 더 많은 텍스트 추출!")
    
    return ocr_text

if __name__ == "__main__":
    result = compare_loaders_vs_ocr()
    
    if result:
        print("\n" + "=" * 80)
        print("💡 결론")
        print("=" * 80)
        print("\nOCR 테스트 성공!")
        print("\n다음 단계:")
        print("  1. 결과 검토 (data/ocr_test_page11.txt)")
        print("  2. 만족스러우면 전체 페이지 OCR 진행")
        print("  3. python preprocessing/ocr_all_pages.py")