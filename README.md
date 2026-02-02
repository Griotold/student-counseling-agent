# 💙 학생 정서 상담 AI Agent

학생자살위기대응매뉴얼 기반 AI 상담 에이전트

---

## 🎯 프로젝트 개요

**목적**: 학생과 친구처럼 대화하며 자살 위기를 조기 감지하고 적절한 대응 안내

**핵심 기능**:
- 친구 같은 페르소나로 공감적 대화
- 실시간 위기도 평가 (낮음/중간/높음)
- 매뉴얼 기반 RAG 검색으로 정확한 대응 안내
- 대화 종료 시 종합 결과 자동 생성
- 구조화된 JSON 출력

**기술 스택**:
- LLM: OpenAI GPT-4o (Structured Output)
- Vector DB: Pinecone (text-embedding-3-large, 3072차원)
- Framework: LangChain
- UI: Streamlit

---

## 📊 시스템 아키텍처
```
사용자 입력
    ↓
Streamlit UI
    ↓
Agent (agent.py)
    ↓
RAG 검색 (retriever.py) → Pinecone
    ↓
LLM (GPT-4o + 매뉴얼 컨텍스트)
    ↓
Structured Output (models.py)
    ↓
JSON 응답
    ↓
UI 표시 + 위험도 평가
```

---

## 🗂️ 프로젝트 구조
```
student-counseling-agent/
├── src/
│   ├── agent.py           # 메인 Agent (chat, summary 생성)
│   ├── models.py          # Pydantic 스키마 (CounselingResponse)
│   ├── prompts.py         # 시스템 프롬프트 (친구 페르소나)
│   └── retriever.py       # Pinecone RAG 검색
│
├── preprocessing/
│   ├── extract_all_pages.py    # PDF → txt 추출
│   └── chunk_and_embed.py       # 청킹 + 임베딩
│
├── data/
│   ├── manual.pdf              # 원본 매뉴얼
│   └── all_pages_txt/          # 전처리된 txt (21페이지)
│
├── archive/
│   ├── preprocessing-experiments/  # 전처리 실험 파일들
│   └── data-experiments/           # 데이터 실험 폴더들
│
├── docs/
│   └── preprocessing_journey.md    # 전처리 과정 상세 기록
│
├── app.py                  # Streamlit UI
├── requirements.txt
└── README.md
```

---

## 📦 설치 및 실행

### 1. 환경 설정
```bash
# Python 가상환경 생성
pyenv virtualenv 3.12 counseling-agent
pyenv local counseling-agent

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일 생성:
```bash
OPENAI_API_KEY=your-openai-api-key
PINECONE_API_KEY=your-pinecone-api-key
```

### 3. 실행

#### Streamlit UI (추천)
```bash
streamlit run app.py
```

#### CLI 테스트
```bash
python -m src.agent
```

---

## 🎯 주요 기능

### 1. **친구 페르소나** 🤝
- 따뜻하고 공감적인 대화
- 판단하지 않고 경청
- 학생의 감정 존중

### 2. **3단계 위기 평가** 📊

| 위기 수준 | 징후 | 대응 |
|----------|------|------|
| 🚨 높음 | 구체적 계획, 수단 준비, 임박한 시간 | 즉시 개입, 1577-0199 연계 |
| ⚠️ 중간 | "죽고 싶다" 반복, 사회적 고립 | 전문 상담 권유 (1388) |
| ✅ 낮음 | 일상 스트레스, 일시적 감정 기복 | 경청 및 공감 |

### 3. **RAG 기반 매뉴얼 검색** 🔍
- 위기 키워드 감지 시 자동 검색
- 21페이지 매뉴얼, 30개 청크
- 관련 대응 방법 정확히 제공

### 4. **대화 종료 시 종합 결과** 📋
```json
{
  "총_대화_턴": 5,
  "대화_요약": "...",
  "주요_이슈": ["자살 계획", "우울"],
  "최고_위험_신호": "높음",
  "감지된_위험요인": ["구체적 계획", "수단 준비"],
  "정서_변화": "...",
  "다음_대화_가이드": "..."
}
```

### 5. **Structured JSON 출력** 📄
```json
{
  "답변": "많이 힘들었구나. 죽고 싶다는 생각이 든다니...",
  "정서적_고통": "높음",
  "자살_신호": "중간",
  "감지된_위험요인": ["자살 사고", "반복적 우울"],
  "권장_대응": "지속 관찰 필요. 전문 상담 권유 (1388)",
  "종료_판단": false
}
```

---

## 🧪 테스트 시나리오

### 시나리오 1: 낮은 위험
```
입력: "오늘 친구가 나를 무시했어. 기분이 너무 안 좋아."
출력:
- 자살 신호: 낮음
- 정서적 고통: 중간
- 권장 대응: 경청 및 공감
```

### 시나리오 2: 중간 위험
```
입력: "요즘 너무 힘들어. 죽고 싶다는 생각이 자주 들어."
출력:
- 자살 신호: 중간
- 정서적 고통: 높음
- 권장 대응: 전문 상담 권유 (1388)
```

### 시나리오 3: 높은 위험 (긴급)
```
입력: "약 모아뒀어. 내일 다 먹으려고."
출력:
- 자살 신호: 높음
- 정서적 고통: 높음
- 종료_판단: true
- 권장 대응: 즉시 개입 (1577-0199)
- 종합 결과 자동 생성 ✅
```

---

## 📈 성능 지표

### 전처리
- 원본: 32페이지 PDF
- 추출: 21페이지 (~18,000자)
- 청킹: 30개 청크 (평균 636자)
- 임베딩: text-embedding-3-large (3072차원)

### RAG 검색 품질
```
테스트 쿼리:
✅ "자살 징후는?" → 페이지 8 (징후 목록)
✅ "죽고 싶다고 말하면?" → 페이지 11 (대면 면담)
✅ "부모에게 알리기" → 페이지 22 (가정통신문)
```

### 응답 시간
- 일반 응답: ~2-3초
- 종합 결과 생성: ~3-5초

---

## 🔧 개발 과정

### 전처리 과정 (자세한 내용: `docs/preprocessing_journey.md`)

1. **PDF 로더 비교** → PDFPlumber 선택
2. **OCR 시도** → 노이즈 70%, 포기
3. **레이아웃 분리** → `within_bbox()` 사용
4. **수동 최적화** → 구조화, 포맷팅 (2시간)
5. **청킹 & 임베딩** → Pinecone 저장

### Agent 개발

1. **LangChain + Structured Output** (LangGraph ✗)
2. **친구 페르소나 프롬프트** 작성
3. **RAG 통합** (위기 키워드 감지)
4. **종료 조건 & 종합 결과** 자동 생성
5. **Streamlit UI** 구현

---

## 🚨 긴급 연락처

| 서비스 | 번호 | 설명 |
|--------|------|------|
| 자살예방상담 | **1393** | 24시간 자살 위기 상담 |
| 청소년상담 | **1388** | 청소년 전문 상담 |
| 정신건강위기 | **1577-0199** | 정신건강 위기 개입 |
| 응급 | **112, 119** | 경찰, 소방 |

---

## 📚 참고 자료

- [학생자살위기대응매뉴얼(교사용).pdf](data/manual.pdf)
- [전처리 과정 상세 기록](docs/preprocessing_journey.md)

---

## 👤 개발자

**조해성**

**제출일**: 2026-02-02

**GitHub**: [student-counseling-agent](https://github.com/griotold/student-counseling-agent)

---

## 📝 라이선스

교육 목적 프로젝트

---

## 🙏 감사의 말

학생자살위기대응매뉴얼을 제공해주신 교육부에 감사드립니다.