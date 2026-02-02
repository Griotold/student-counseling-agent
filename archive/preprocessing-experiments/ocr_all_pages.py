"""
전체 페이지 OCR
핵심 14페이지 처리
"""
from pdf2image import convert_from_path
import pytesseract
from pathlib import Path
import json

def ocr_all_core_pages():
    """핵심 페이지 전체 OCR"""
    print("=" * 80)
    print("📸 전체 페이지 OCR")
    print("=" * 80)
    
    # 핵심 페이지
    core_pages = [
        10, 11, 12, 13,  # 자살 징후
        17, 18, 19,      # 대면 면담
        23, 24, 25,      # 위기 개입
        26, 27, 28, 29   # 위험요인
    ]
    
    results = {}
    
    for page_num in core_pages:
        print(f"\n[{page_num - core_pages[0] + 1}/{len(core_pages)}] 페이지 {page_num + 1} 처리 중...")
        
        try:
            # 이미지 변환
            images = convert_from_path(
                "data/manual.pdf",
                first_page=page_num + 1,
                last_page=page_num + 1,
                dpi=300
            )
            
            # OCR
            text = pytesseract.image_to_string(
                images[0],
                lang='kor+eng',
                config='--psm 6'
            )
            
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
    
    # 결과 저장
    print("\n" + "=" * 80)
    print("💾 결과 저장")
    print("=" * 80)
    
    # JSON 저장
    output_dir = Path("data/ocr_results")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "all_pages.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 페이지별 txt 저장
    for page_num, data in results.items():
        with open(output_dir / f"page_{page_num:02d}.txt", "w", encoding="utf-8") as f:
            f.write(data['text'])
    
    print(f"✅ 저장 완료: {output_dir}")
    
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
    results = ocr_all_core_pages()
    
    print("\n" + "=" * 80)
    print("✨ 완료!")
    print("=" * 80)
    print("\n다음 단계:")
    print("  1. data/ocr_results/ 폴더 확인")
    print("  2. 노이즈 제거: python preprocessing/clean_ocr.py")
