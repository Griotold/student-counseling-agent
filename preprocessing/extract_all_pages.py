"""
전체 32페이지 모두 추출
레이아웃 기반 (왼쪽/오른쪽 분리)
"""
import pdfplumber
from pathlib import Path
import json

def extract_page_with_layout(page):
    """레이아웃 기반 추출"""
    width = page.width
    height = page.height
    
    # 왼쪽/오른쪽 분리
    left_bbox = (0, 0, width/2, height)
    right_bbox = (width/2, 0, width, height)
    
    left = page.within_bbox(left_bbox)
    left_text = left.extract_text() or ""
    
    right = page.within_bbox(right_bbox)
    right_text = right.extract_text() or ""
    
    # 합치기
    combined = f"{left_text}\n\n{right_text}".strip()
    
    return combined

def main():
    print("=" * 80)
    print("📄 전체 페이지 추출 (32페이지)")
    print("=" * 80)
    
    with pdfplumber.open("data/manual.pdf") as pdf:
        total_pages = len(pdf.pages)
        print(f"\n총 페이지: {total_pages}개")
        
        # 저장 디렉토리
        output_dir = Path("data/all_pages_txt")
        output_dir.mkdir(exist_ok=True)
        
        results = {}
        
        # 전체 추출
        for i in range(total_pages):
            print(f"\n[{i+1}/{total_pages}] 페이지 {i+1} 추출 중...")
            
            try:
                page = pdf.pages[i]
                text = extract_page_with_layout(page)
                
                results[i+1] = {
                    'text': text,
                    'length': len(text)
                }
                
                # txt 저장
                filename = f"page_{i+1:02d}.txt"
                with open(output_dir / filename, "w", encoding="utf-8") as f:
                    f.write(f"=== 페이지 {i+1} ===\n\n")
                    f.write(text)
                
                print(f"   ✅ {len(text)}자 저장 → {filename}")
                
            except Exception as e:
                print(f"   ❌ 실패: {e}")
                results[i+1] = {
                    'text': '',
                    'length': 0,
                    'error': str(e)
                }
        
        # JSON 저장
        with open(output_dir / "all_pages.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 통계
        print("\n" + "=" * 80)
        print("📊 통계")
        print("=" * 80)
        
        total_chars = sum(d['length'] for d in results.values())
        avg_chars = total_chars / len(results)
        
        print(f"\n총 페이지: {len(results)}개")
        print(f"총 글자수: {total_chars:,}자")
        print(f"평균: {avg_chars:.0f}자/페이지")
        
        # 짧은 페이지 확인 (표지 가능성)
        print(f"\n⚠️  짧은 페이지 (200자 미만):")
        for page_num, data in sorted(results.items()):
            if data['length'] < 200:
                print(f"  page_{page_num:02d}.txt: {data['length']}자")
        
        print("\n" + "=" * 80)
        print("✨ 완료!")
        print("=" * 80)
        
        print(f"\n📁 저장 위치: {output_dir}/")
        print(f"\n다음 단계:")
        print(f"  1. 폴더 열기: open {output_dir}")
        print(f"  2. 각 txt 파일 확인")
        print(f"  3. 불필요한 파일 삭제 (표지, 빈 페이지 등)")
        print(f"  4. 전처리 진행")

if __name__ == "__main__":
    main()