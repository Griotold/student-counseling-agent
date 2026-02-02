"""
페이지 번호 검증 (수정판)
"""
import pdfplumber

def verify_pages():
    print("=" * 80)
    print("📄 페이지 번호 검증")
    print("=" * 80)
    
    with pdfplumber.open("data/manual.pdf") as pdf:
        print(f"\n총 페이지 수: {len(pdf.pages)}")
        
        # 주요 챕터 시작 페이지
        chapters = {
            "1단계": "자살의 징후 알아차리기",
            "2단계": "자살위험 정도 평가하기", 
            "3단계": "자살 위기 개입하기",
            "사후개입": "학생 자살사건의 사후",
            "상시관리": "악성 자살예방을 위한",
        }
        
        results = {}
        
        # 목차 이후부터 검색 (p.5부터)
        for i in range(5, len(pdf.pages)):
            page = pdf.pages[i]
            text = page.extract_text()
            
            if not text:
                continue
            
            # 각 챕터 확인
            for chapter_name, keyword in chapters.items():
                if chapter_name not in results:
                    # 챕터 시작 패턴 확인
                    # "1단계" 또는 큰 제목으로 시작
                    lines = text.split('\n')[:10]  # 처음 10줄만
                    first_text = '\n'.join(lines)
                    
                    if keyword in first_text and (chapter_name in first_text or "단계" in first_text[:50]):
                        results[chapter_name] = i
                        print(f"\n✅ {chapter_name}: {keyword}")
                        print(f"   Python index: {i}")
                        print(f"   (1-based: {i+1})")
                        print(f"   첫 200자:\n{text[:200]}")
        
        # 수동 확인이 필요한 주요 페이지들
        print("\n" + "=" * 80)
        print("🔍 주요 페이지 확인 (수동)")
        print("=" * 80)
        
        check_pages = [6, 10, 13, 18, 22, 28, 32]
        
        for i in check_pages:
            if i < len(pdf.pages):
                page = pdf.pages[i]
                text = page.extract_text()
                if text:
                    print(f"\n--- pages[{i}] (1-based: {i+1}) ---")
                    print(text[:150])
        
        print("\n" + "=" * 80)
        print("📊 챕터 시작 페이지")
        print("=" * 80)
        
        for chapter, index in sorted(results.items(), key=lambda x: x[1] if x[1] else 999):
            if index:
                print(f"{chapter}: pages[{index}] (1-based: {index+1})")

if __name__ == "__main__":
    verify_pages()