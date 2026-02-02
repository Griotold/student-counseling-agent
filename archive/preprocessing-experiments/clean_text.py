"""
txt 파일 전처리
- 세로 텍스트 제거
- 페이지 번호 제거
- 불필요한 개행 정리
"""
from pathlib import Path
import re

def clean_text(text):
    """텍스트 정리"""
    
    # 1. 헤더 제거 ("=== 페이지 X ===")
    text = re.sub(r'=== 페이지 \d+ ===\n*', '', text)
    
    # 2. 세로 텍스트 패턴 제거
    # "1\n자\n살" 또는 "위\n험\n이" 패턴
    lines = text.split('\n')
    cleaned_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 단일 문자 (한글/숫자) 라인 연속 체크
        if len(line) <= 2 and i + 2 < len(lines):
            next1 = lines[i+1].strip()
            next2 = lines[i+2].strip()
            
            # 3개 연속 단일 문자 → 세로 텍스트로 판단
            if len(next1) <= 2 and len(next2) <= 2:
                i += 3  # 건너뛰기
                continue
        
        # 숫자만 있는 줄 (페이지 번호)
        if line.isdigit() and len(line) <= 3:
            i += 1
            continue
        
        # 빈 줄이 아니면 추가
        if line:
            cleaned_lines.append(line)
        
        i += 1
    
    # 3. 재조합
    text = '\n'.join(cleaned_lines)
    
    # 4. 다중 개행 정리
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 5. 앞뒤 공백 제거
    text = text.strip()
    
    return text

def process_all_files():
    """전체 txt 파일 처리"""
    print("=" * 80)
    print("🧹 텍스트 전처리")
    print("=" * 80)
    
    input_dir = Path("data/all_pages_txt")
    output_dir = Path("data/cleaned_txt")
    output_dir.mkdir(exist_ok=True)
    
    # txt 파일들
    txt_files = sorted(input_dir.glob("page_*.txt"))
    
    print(f"\n처리할 파일: {len(txt_files)}개")
    
    total_before = 0
    total_after = 0
    
    for txt_file in txt_files:
        # 원본 읽기
        with open(txt_file, 'r', encoding='utf-8') as f:
            original = f.read()
        
        # 정리
        cleaned = clean_text(original)
        
        # 저장
        output_file = output_dir / txt_file.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        
        # 통계
        total_before += len(original)
        total_after += len(cleaned)
        
        reduction = len(original) - len(cleaned)
        print(f"{txt_file.name}: {len(original)}자 → {len(cleaned)}자 ({reduction:+}자)")
    
    # 전체 통계
    print("\n" + "=" * 80)
    print("📊 통계")
    print("=" * 80)
    
    print(f"\n원본 총 글자수: {total_before:,}자")
    print(f"정리 후: {total_after:,}자")
    print(f"제거: {total_before - total_after:,}자 ({(total_before - total_after) / total_before * 100:.1f}%)")
    
    # 샘플 확인
    print("\n" + "=" * 80)
    print("📝 샘플 확인 (page_07.txt)")
    print("=" * 80)
    
    sample = output_dir / "page_07.txt"
    if sample.exists():
        with open(sample, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"\n정리된 텍스트 (처음 500자):")
        print("-" * 80)
        print(content[:500])
        print("-" * 80)
    
    print("\n✨ 완료!")
    print(f"\n저장 위치: {output_dir}/")

if __name__ == "__main__":
    process_all_files()