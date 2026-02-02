# 🧠 학생 정서 상담 AI Agent

학생자살위기대응매뉴얼 기반 AI 상담 에이전트

## 🎯 프로젝트 개요
- **목적**: 학생 자살 위기 조기 감지 및 대응
- **기술**: LangChain + OpenAI GPT-4 + Pinecone
- **특징**: 실시간 위기도 평가 및 구조화된 JSON 출력

## 🛠️ 기술 스택
- **LLM**: OpenAI GPT-4o
- **Vector DB**: Pinecone
- **Framework**: LangChain
- **UI**: Streamlit

## 📦 설치
```bash
pyenv virtualenv 3.12 counseling-agent
pyenv local counseling-agent
pip install -r requirements.txt
```

## 🔐 환경 변수
```bash
OPENAI_API_KEY=your-key
PINECONE_API_KEY=your-key
```

## 🚀 실행
```bash
streamlit run app.py
```

## 📁 프로젝트 구조
```
student-counseling-agent/
├── src/
│   ├── models.py
│   ├── prompts.py
│   ├── agent.py
│   └── vector_store.py
├── data/
├── app.py
└── requirements.txt
```

## 📝 주요 기능
- ✅ 실시간 위기도 평가 (낮음/중간/높음)
- ✅ 대화 맥락 기억
- ✅ 구조화된 JSON 출력
- ✅ 매뉴얼 기반 RAG (고위험 시)

---

**개발자**: 조해성
**제출일**: 2025-02-01