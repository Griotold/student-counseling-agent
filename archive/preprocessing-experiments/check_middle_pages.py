"""
중간 페이지 확인
"""
import pdfplumber

with pdfplumber.open("data/manual.pdf") as pdf:
    # 3단계 내용 (pages[13-21])
    print("="*80)
    print("3단계 내용 확인 (pages[13-21])")
    print("="*80)
    
    for i in range(13, 22):
        page = pdf.pages[i]
        text = page.extract_text()
        
        # 제목/헤더만 추출 (처음 3줄)
        lines = text.split('\n')[:5] if text else []
        header = '\n'.join(lines)
        
        print(f"\npages[{i}] (화면: {i+1}):")
        print(header)
        print(f"전체 길이: {len(text) if text else 0}자")
    
    # 사후개입 내용 (pages[20-27])
    print("\n"+"="*80)
    print("사후개입 내용 확인 (pages[20-27])")
    print("="*80)
    
    for i in range(20, 28):
        page = pdf.pages[i]
        text = page.extract_text()
        
        lines = text.split('\n')[:5] if text else []
        header = '\n'.join(lines)
        
        print(f"\npages[{i}] (화면: {i+1}):")
        print(header)
        print(f"전체 길이: {len(text) if text else 0}자")