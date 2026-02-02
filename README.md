# 💙 학생 정서 상담 AI Agent
<img width="1452" height="780" alt="Image" src="https://github.com/user-attachments/assets/ed14edc0-5f56-4005-a299-1e92b22dd649" />

- 학생자살위기대응매뉴얼 기반 AI 상담 에이전트
- 스트림릿 배포 링크: https://student-counseling.streamlit.app/

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
## 🌐 데모

### Streamlit Cloud 배포
**🔗 [학생 정서 상담 AI 체험하기](https://student-counseling.streamlit.app)**

### 자살 신호: 중간 / 정서적 고통: 높음
<img width="1453" height="806" alt="Image" src="https://github.com/user-attachments/assets/a0256820-a2c8-480a-8b74-25526a7c0028" />

### 자살 신호: 높음 / 정서적 고통 : 높음
<img width="1043" height="526" alt="Image" src="https://github.com/user-attachments/assets/2bac3603-b96c-4f51-8a74-886b55076b06" />

### 대화 요약
<img width="1052" height="622" alt="Image" src="https://github.com/user-attachments/assets/6653bf08-e990-4dc9-bb0d-e020b437d26e" />

---

## 📊 워크플로우
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

---

## 🤖 프롬프트 구조

### 시스템 프롬프트 (친구 페르소나)
```python
# src/prompts.py - SYSTEM_PROMPT

역할: 학생 정서 상담 전문 AI
페르소나: 친구에 가깝게 편한 대화를 나누는 상대

핵심 원칙:
1. 따뜻하고 공감적인 태도
2. 판단하지 않고 경청
3. 학생의 감정 존중

자살 신호 판단 기준:
- 낮음: 일상 스트레스, 일시적 감정
- 중간: "죽고 싶다" 반복, 사회적 고립
- 높음: 구체적 계획, 수단 준비, 임박한 시간

대응 원칙:
- 높음: 즉시 개입 (1577-0199)
- 중간: 전문 상담 권유 (1388)
- 낮음: 경청 및 공감

주의사항:
- 절대 판단하거나 비난하지 않기
- 학생의 감정을 최소화하지 않기
- 구체적 자살 방법 절대 언급 금지
```

---

### RAG 컨텍스트 프롬프트
```python
# src/prompts.py - CONTEXT_PROMPT

다음은 학생자살위기대응매뉴얼에서 관련 내용입니다:

{context}

위 매뉴얼을 참고하여 학생과 대화하고 위기를 평가해주세요.
```

---

### 종합 결과 프롬프트
```python
# src/prompts.py - SUMMARY_PROMPT

대화 종료 시 자동 생성:
- 총 대화 턴
- 대화 요약
- 주요 이슈
- 최고 위험 신호
- 감지된 위험요인
- 정서 변화
- 다음 대화 가이드
```

---

## 💬 응답 예시

### 낮은 위험
```json
{
  "답변": "친구한테 무시당하니까 기분이 많이 상했겠다. 무슨 일이 있었는지 얘기해줄 수 있어?",
  "정서적_고통": "중간",
  "자살_신호": "낮음",
  "감지된_위험요인": ["또래 갈등"],
  "권장_대응": "경청 및 공감. 보호요인 탐색",
  "종료_판단": false
}
```

### 높은 위험 (긴급)
```json
{
  "답변": "지금 네가 정말 많이 힘든 걸 알겠어. 혼자 두지 않을게. 지금 당장 선생님이나 부모님께 연락해도 될까?",
  "정서적_고통": "높음",
  "자살_신호": "높음",
  "감지된_위험요인": ["구체적 자살 계획", "수단 준비"],
  "권장_대응": "즉시 개입 필요. 보호자 연락 및 전문기관 (1577-0199) 즉시 연계",
  "종료_판단": true,
  "종합_결과": {
    "총_대화_턴": 1,
    "대화_요약": "학생이 자살 수단을 준비하고 구체적 시간을 밝힘",
    "최고_위험_신호": "높음",
    "다음_대화_가이드": "즉시 전문가 개입, 학생 절대 혼자 두지 말 것"
  }
}
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

## 📚 프로젝트 문서

- [학생자살위기대응매뉴얼(교사용).pdf](data/manual.pdf)
- [전처리 과정 상세 기록](docs/preprocessing_journey.md)
- [src/prompts.py](src/prompts.py) - 전체 프롬프트 
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
