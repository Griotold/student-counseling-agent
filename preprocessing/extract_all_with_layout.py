"""
전체 핵심 페이지를 레이아웃 기반으로 추출
"""
import pdfplumber
from pathlib import Path
import json

def extract_page_with_layout(pdf, page_num):
    """단일 페이지를 레이아웃 기반으로 추출"""
    page = pdf.pages[page_num]
    
    # 페이지 크기
    width = page.width
    height = page.height
    
    # 왼쪽/오른쪽 분리
    left_bbox = (0, 0, width/2, height)
    right_bbox = (width/2, 0, width, height)
    
    left = page.within_bbox(left_bbox)
    left_text = left.extract_text() or ""
    
    right = page.within_bbox(right_bbox)
    right_text = right.extract_text() or ""
    
    # 합치기 (왼쪽 → 오른쪽)
    combined = f"{left_text}\n\n{right_text}"
    
    return combined.strip()

def extract_all_core_pages():
    """전체 핵심 페이지 추출"""
    print("=" * 80)
    print("📄 레이아웃 기반 전체 페이지 추출")
    print("=" * 80)
    
    # 핵심 페이지 (0-based)
    core_pages = [
        10, 11, 12, 13,  # 자살 징후 (p.11-14)
        17, 18, 19,      # 대면 면담 (p.18-20)
        23, 24, 25,      # 위기 개입 (p.24-26)
        26, 27, 28, 29   # 위험요인 (p.27-30)
    ]
    
    results = {}
    
    with pdfplumber.open("data/manual.pdf") as pdf:
        for i, page_num in enumerate(core_pages, 1):
            print(f"\n[{i}/{len(core_pages)}] 페이지 {page_num + 1} 추출 중...")
            
            try:
                text = extract_page_with_layout(pdf, page_num)
                
                results[page_num + 1] = {
                    'text': text,
                    'length': len(text)
                }
                
                print(f"   ✅ {len(text)}자 추출")
                
            except Exception as e:
                print(f"   ❌ 실패: {e}")
                results[page_num + 1] = {
                    'text': '',
                    'length': 0,
                    'error': str(e)
                }
    
    # 저장
    print("\n" + "=" * 80)
    print("💾 결과 저장")
    print("=" * 80)
    
    output_dir = Path("data/layout_extracted")
    output_dir.mkdir(exist_ok=True)
    
    # JSON 저장
    with open(output_dir / "all_pages.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 개별 txt 저장
    for page_num, data in results.items():
        with open(output_dir / f"page_{page_num:02d}.txt", "w", encoding="utf-8") as f:
            f.write(f"=== 페이지 {page_num} ===\n\n")
            f.write(data['text'])
    
    print(f"✅ 저장 완료: {output_dir}/")
    
    # 통계
    print("\n" + "=" * 80)
    print("📊 통계")
    print("=" * 80)
    
    total_chars = sum(d['length'] for d in results.values())
    avg_chars = total_chars / len(results)
    
    print(f"\n총 페이지: {len(results)}개")
    print(f"총 글자수: {total_chars:,}자")
    print(f"평균: {avg_chars:.0f}자/페이지")
    
    print(f"\n페이지별 글자수:")
    for page_num in sorted(results.keys()):
        length = results[page_num]['length']
        print(f"  p.{page_num}: {length:,}자")
    
    return results

if __name__ == "__main__":
    results = extract_all_core_pages()
    
    print("\n" + "=" * 80)
    print("✨ 완료!")
    print("=" * 80)
    print("\n다음 단계:")
    print("  1. data/layout_extracted/ 폴더 확인")
    print("  2. 몇 개 페이지 매뉴얼과 대조")
    print("  3. 만족스러우면 전처리 진행")
    print("     → python preprocessing/step2_preprocess.py")