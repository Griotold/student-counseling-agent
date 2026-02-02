"""
2단 레이아웃 추출 테스트
"""
import pdfplumber
from pathlib import Path

def test_layout_extraction():
    """레이아웃 기반 추출 테스트"""
    print("=" * 80)
    print("📄 레이아웃 기반 추출 테스트 (페이지 11)")
    print("=" * 80)
    
    with pdfplumber.open("data/manual.pdf") as pdf:
        page = pdf.pages[10]  # p.11
        
        # 페이지 크기
        width = page.width
        height = page.height
        
        print(f"\n페이지 크기: {width} x {height}")
        
        # 왼쪽/오른쪽 영역 정의
        left_bbox = (0, 0, width/2, height)
        right_bbox = (width/2, 0, width, height)
        
        # 왼쪽 추출
        print("\n[1/2] 왼쪽 영역 추출 중...")
        left = page.within_bbox(left_bbox)
        left_text = left.extract_text()
        
        # 오른쪽 추출
        print("[2/2] 오른쪽 영역 추출 중...")
        right = page.within_bbox(right_bbox)
        right_text = right.extract_text()
        
        # 결과
        print("\n" + "=" * 80)
        print("📊 결과")
        print("=" * 80)
        
        print(f"\n왼쪽: {len(left_text)}자")
        print(f"오른쪽: {len(right_text)}자")
        print(f"합계: {len(left_text) + len(right_text)}자")
        
        # 샘플 출력
        print("\n" + "=" * 80)
        print("왼쪽 샘플 (처음 300자)")
        print("=" * 80)
        print(left_text[:300])
        
        print("\n" + "=" * 80)
        print("오른쪽 샘플 (처음 300자)")
        print("=" * 80)
        print(right_text[:300])
        
        # 저장
        output_dir = Path("data/layout_test")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "page_11_left.txt", "w", encoding="utf-8") as f:
            f.write(left_text)
        
        with open(output_dir / "page_11_right.txt", "w", encoding="utf-8") as f:
            f.write(right_text)
        
        # 합치기 (왼쪽 → 오른쪽)
        combined = f"{left_text}\n\n{'='*80}\n\n{right_text}"
        
        with open(output_dir / "page_11_combined.txt", "w", encoding="utf-8") as f:
            f.write(combined)
        
        print("\n" + "=" * 80)
        print("💾 저장 완료")
        print("=" * 80)
        print(f"\n위치: {output_dir}")
        print("\n파일:")
        print("  - page_11_left.txt (왼쪽)")
        print("  - page_11_right.txt (오른쪽)")
        print("  - page_11_combined.txt (합본)")
        
        return left_text, right_text

if __name__ == "__main__":
    left, right = test_layout_extraction()
    
    print("\n" + "=" * 80)
    print("💡 다음 단계")
    print("=" * 80)
    print("\n1. data/layout_test/ 폴더 확인")
    print("2. 매뉴얼과 비교")
    print("3. 만족스러우면 전체 페이지 적용")
    print("4. 불만족이면 수동 추출")