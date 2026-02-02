"""
OCR 결과 노이즈 제거
"""
import json
import re
from pathlib import Path

def clean_ocr_text(text):
    """OCR 노이즈 제거"""
    
    # 1. 단일 문자 라인 제거
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # 빈 줄
        if not stripped:
            continue
        
        # 단일 문자 (a, |, —, 등)
        if len(stripped) == 1 and not stripped.isalnum():
            continue
        
        # 짧은 노이즈 (2-3자의 의미없는 문자)
        if len(stripped) <= 3 and re.match(r'^[^가-힣a-zA-Z0-9]+$', stripped):
            continue
        
        # 레이아웃 문자만 있는 줄
        if re.match(r'^[\s\|:;—_\-=]+$', stripped):
            continue
        
        cleaned_lines.append(stripped)
    
    text = '\n'.join(cleaned_lines)
    
    # 2. 특정 노이즈 패턴 제거
    # 레이아웃 기호
    text = re.sub(r'\s+[|:;—_]+\s+', ' ', text)
    
    # 단일 알파벳 (단어 중간 제외)
    text = re.sub(r'\s+[a-zA-Z]\s+', ' ', text)
    
    # 특수문자 반복
    text = re.sub(r'[©¢€£¥]+', '', text)
    
    # 이상한 조합 ("ee", "oe" 등)
    text = re.sub(r'\b(ee|oe|ae)\b', '', text)
    
    # 숫자 + 특수문자 조합 (의미 없는)
    text = re.sub(r'\d+\s*[<>|]+', '', text)
    
    # 3. 다중 공백/개행 정리
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    # 4. 앞뒤 공백 제거
    text = text.strip()
    
    return text

def evaluate_cleaning(original, cleaned):
    """정리 효과 평가"""
    reduction = len(original) - len(cleaned)
    reduction_pct = (reduction / len(original)) * 100
    
    return {
        'original_length': len(original),
        'cleaned_length': len(cleaned),
        'removed': reduction,
        'reduction_pct': reduction_pct
    }

def clean_all_pages():
    """전체 페이지 정리"""
    print("=" * 80)
    print("🧹 OCR 노이즈 제거")
    print("=" * 80)
    
    input_dir = Path("data/ocr_results")
    output_dir = Path("data/ocr_cleaned")
    output_dir.mkdir(exist_ok=True)
    
    # JSON 로드
    with open(input_dir / "all_pages.json", "r", encoding="utf-8") as f:
        ocr_data = json.load(f)
    
    cleaned_data = {}
    stats = []
    
    for page_num, data in ocr_data.items():
        print(f"\n페이지 {page_num} 정리 중...")
        
        original_text = data['text']
        cleaned_text = clean_ocr_text(original_text)
        
        # 통계
        stat = evaluate_cleaning(original_text, cleaned_text)
        stat['page'] = page_num
        stats.append(stat)
        
        print(f"  원본: {stat['original_length']:,}자")
        print(f"  정리: {stat['cleaned_length']:,}자")
        print(f"  제거: {stat['removed']:,}자 ({stat['reduction_pct']:.1f}%)")
        
        # 저장
        cleaned_data[page_num] = {
            'text': cleaned_text,
            'length': len(cleaned_text),
            'original_length': len(original_text)
        }
        
        # 텍스트 파일 저장
        with open(output_dir / f"page_{page_num}.txt", "w", encoding="utf-8") as f:
            f.write(cleaned_text)
    
    # JSON 저장
    with open(output_dir / "all_pages_cleaned.json", "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    
    # 전체 통계
    print("\n" + "=" * 80)
    print("📊 전체 통계")
    print("=" * 80)
    
    total_original = sum(s['original_length'] for s in stats)
    total_cleaned = sum(s['cleaned_length'] for s in stats)
    total_removed = total_original - total_cleaned
    total_reduction_pct = (total_removed / total_original) * 100
    
    print(f"\n원본 총 글자수: {total_original:,}자")
    print(f"정리 후: {total_cleaned:,}자")
    print(f"제거: {total_removed:,}자 ({total_reduction_pct:.1f}%)")
    
    # 샘플 확인
    print("\n" + "=" * 80)
    print("📝 샘플 확인 (페이지 11)")
    print("=" * 80)
    
    sample_text = cleaned_data['11']['text']
    print(f"\n정리된 텍스트 (처음 500자):")
    print("-" * 80)
    print(sample_text[:500])
    print("-" * 80)
    
    return cleaned_data, stats

if __name__ == "__main__":
    cleaned_data, stats = clean_all_pages()
    
    print("\n" + "=" * 80)
    print("✨ 완료!")
    print("=" * 80)
    print("\n다음 단계:")
    print("  1. data/ocr_cleaned/ 폴더 확인")
    print("  2. 샘플 텍스트 검토")
    print("  3. 만족스러우면 임베딩 진행")