"""
PDFPlumber 결과 저장
매뉴얼과 대조를 위해
"""
from langchain_community.document_loaders import PDFPlumberLoader
from pathlib import Path
import json

def save_pdfplumber_results():
    """PDFPlumber 결과 저장"""
    print("=" * 80)
    print("📄 PDFPlumber 결과 저장")
    print("=" * 80)
    
    # 로드
    print("\n[1/2] PDF 로딩 중...")
    loader = PDFPlumberLoader("data/manual.pdf")
    pages = loader.load()
    print(f"✅ {len(pages)}페이지 로드 완료")
    
    # 핵심 페이지
    core_pages = [
        10, 11, 12, 13,  # 자살 징후 (p.11-14)
        17, 18, 19,      # 대면 면담 (p.18-20)
        23, 24, 25,      # 위기 개입 (p.24-26)
        26, 27, 28, 29   # 위험요인 (p.27-30)
    ]
    
    # 저장
    print("\n[2/2] 결과 저장 중...")
    output_dir = Path("data/pdfplumber_results")
    output_dir.mkdir(exist_ok=True)
    
    results = {}
    
    for page_num in core_pages:
        page = pages[page_num]
        text = page.page_content
        
        # 페이지 번호 (1-based)
        page_display = page_num + 1
        
        results[page_display] = {
            'text': text,
            'length': len(text),
            'metadata': page.metadata
        }
        
        # 개별 txt 파일 저장
        with open(output_dir / f"page_{page_display:02d}.txt", "w", encoding="utf-8") as f:
            f.write(f"=== 페이지 {page_display} ===\n\n")
            f.write(text)
        
        print(f"  ✅ 페이지 {page_display}: {len(text)}자 저장")
    
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
    
    print(f"\n페이지별 글자수:")
    for page_num in sorted(results.keys()):
        length = results[page_num]['length']
        print(f"  p.{page_num}: {length:,}자")
    
    return results

if __name__ == "__main__":
    results = save_pdfplumber_results()
    
    print("\n" + "=" * 80)
    print("✨ 완료!")
    print("=" * 80)
    print("\n저장 위치: data/pdfplumber_results/")
    print("\n확인 방법:")
    print("  1. Finder에서 data/pdfplumber_results/ 열기")
    print("  2. page_XX.txt 파일 열기")
    print("  3. 매뉴얼 PDF와 비교")
    print("\n예:")
    print("  cat data/pdfplumber_results/page_11.txt")
    print("  cat data/pdfplumber_results/page_12.txt")