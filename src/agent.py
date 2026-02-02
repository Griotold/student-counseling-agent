"""
학생 정서 상담 AI Agent
LangChain + Structured Output
"""
import os
import json
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

from .models import CounselingResponse
from .prompts import SYSTEM_PROMPT, CONTEXT_PROMPT, SUMMARY_PROMPT
from .retriever import ManualRetriever

load_dotenv()


class StudentCounselingAgent:
    """학생 정서 상담 Agent"""
    
    def __init__(self):
        """초기화"""
        # Structured Output으로 LLM 설정
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7  # 친구 같은 톤 위해 약간 높게
        ).with_structured_output(CounselingResponse)
        
        # 요약용 LLM (별도)
        self.summary_llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0
        )
        
        # RAG 검색기
        self.retriever = ManualRetriever()
        
        # 대화 히스토리
        self.conversation_history: List[Dict[str, str]] = []
        self.turn_count = 0
    
    def chat(self, user_message: str) -> Dict:
        """
        학생과 대화
        
        Args:
            user_message: 학생의 메시지
            
        Returns:
            Dict: 응답 + (종료 시) 종합 결과
        """
        # 턴 수 증가
        self.turn_count += 1
        
        # 1. 일반 응답 생성
        response = self._generate_response(user_message)
        
        # 2. 히스토리 저장
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": response.답변
        })
        
        # 3. 종료 판단 시 종합 결과 생성
        if response.종료_판단:
            summary = self._generate_summary()
            return {
                **response.model_dump(),
                "종합_결과": summary
            }
        
        return response.model_dump()
    
    def _generate_response(self, user_message: str) -> CounselingResponse:
        """응답 생성"""
        # 1. RAG 검색
        context = self._retrieve_context(user_message)
        
        # 2. 메시지 구성
        messages = self._build_messages(user_message, context)
        
        # 3. LLM 호출 (Structured Output)
        response: CounselingResponse = self.llm.invoke(messages)
        
        return response
    
    def _retrieve_context(self, query: str) -> str:
        """RAG 검색"""
        # 위기 관련 키워드 감지
        crisis_keywords = [
            "죽고", "자살", "사라지", "약", "뛰어내리",
            "유서", "끝내", "살기 싫", "없어지"
        ]
        
        # 위기 키워드 있으면 더 많이 검색
        if any(keyword in query for keyword in crisis_keywords):
            return self.retriever.search(query, k=5)
        else:
            return self.retriever.search(query, k=3)
    
    def _build_messages(self, user_message: str, context: str) -> List:
        """프롬프트 메시지 구성"""
        messages = []
        
        # 1. 시스템 프롬프트
        messages.append(SystemMessage(content=SYSTEM_PROMPT))
        
        # 2. RAG 컨텍스트
        if context:
            messages.append(SystemMessage(
                content=CONTEXT_PROMPT.format(context=context)
            ))
        
        # 3. 대화 히스토리
        for msg in self.conversation_history[-10:]:  # 최근 10턴
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        
        # 4. 현재 메시지
        messages.append(HumanMessage(content=user_message))
        
        # 5. 턴 수 정보 추가
        if self.turn_count >= 10:
            messages.append(SystemMessage(
                content=f"현재 대화 턴: {self.turn_count}회. 10회 이상이므로 자연스럽게 마무리를 고려하세요."
            ))
        
        return messages
    
    def _format_history(self) -> str:
        """대화 히스토리 포맷"""
        formatted = []
        for msg in self.conversation_history:
            role = "학생" if msg["role"] == "user" else "AI"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)
    
    def _generate_summary(self) -> Dict:
        """
        종합 결과 생성 (종료 시 자동 호출)
        
        Returns:
            Dict: 종합 결과
        """
        if not self.conversation_history:
            return {
                "총_대화_턴": 0,
                "대화_요약": "대화 없음"
            }
        
        # 프롬프트 구성
        prompt = SUMMARY_PROMPT.format(
            history=self._format_history(),
            turn_count=self.turn_count
        )
        
        response = self.summary_llm.invoke([
            SystemMessage(content=prompt)
        ])
        
        # JSON 파싱
        try:
            # JSON 추출 (```json ... ``` 제거)
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            summary = json.loads(content.strip())
        except Exception as e:
            # 파싱 실패 시 기본 요약
            summary = {
                "총_대화_턴": self.turn_count,
                "대화_요약": "요약 생성 실패",
                "오류": str(e),
                "원본": response.content[:500]
            }
        
        return summary
    
    def reset(self):
        """대화 초기화"""
        self.conversation_history = []
        self.turn_count = 0


# 테스트
if __name__ == "__main__":
    print("=" * 80)
    print("학생 정서 상담 Agent 테스트")
    print("=" * 80)
    
    agent = StudentCounselingAgent()
    
    # 테스트 시나리오 1: 낮은 위험
    print("\n[시나리오 1: 낮은 위험]")
    print("-" * 80)
    
    message1 = "오늘 친구가 나를 무시했어. 기분이 너무 안 좋아."
    response1 = agent.chat(message1)
    
    print(f"학생: {message1}")
    print(f"\nAI 답변: {response1['답변']}")
    print(f"정서적 고통: {response1['정서적_고통']}")
    print(f"자살 신호: {response1['자살_신호']}")
    print(f"감지된 위험요인: {response1['감지된_위험요인']}")
    print(f"권장 대응: {response1['권장_대응']}")
    print(f"종료 판단: {response1['종료_판단']}")
    
    # 테스트 시나리오 2: 중간 위험
    print("\n" + "=" * 80)
    print("[시나리오 2: 중간 위험]")
    print("-" * 80)
    
    agent.reset()  # 새 대화
    
    message2 = "요즘 너무 힘들어. 죽고 싶다는 생각이 자주 들어."
    response2 = agent.chat(message2)
    
    print(f"학생: {message2}")
    print(f"\nAI 답변: {response2['답변']}")
    print(f"정서적 고통: {response2['정서적_고통']}")
    print(f"자살 신호: {response2['자살_신호']}")
    print(f"감지된 위험요인: {response2['감지된_위험요인']}")
    print(f"권장 대응: {response2['권장_대응']}")
    print(f"종료 판단: {response2['종료_판단']}")
    
    # 테스트 시나리오 3: 높은 위험 (종료 조건 만족)
    print("\n" + "=" * 80)
    print("[시나리오 3: 높은 위험 - 긴급 (종료 조건 만족)]")
    print("-" * 80)
    
    agent.reset()  # 새 대화
    
    message3 = "약 모아뒀어. 내일 다 먹으려고."
    response3 = agent.chat(message3)
    
    print(f"학생: {message3}")
    print(f"\nAI 답변: {response3['답변']}")
    print(f"정서적 고통: {response3['정서적_고통']}")
    print(f"자살 신호: {response3['자살_신호']}")
    print(f"감지된 위험요인: {response3['감지된_위험요인']}")
    print(f"권장 대응: {response3['권장_대응']}")
    print(f"종료 판단: {response3['종료_판단']}")
    
    # 종합 결과 (자동 생성됨!)
    if response3.get('종합_결과'):
        print("\n" + "=" * 80)
        print("🎯 종합 결과 (자동 생성)")
        print("=" * 80)
        
        summary = response3['종합_결과']
        print(f"\n총 대화 턴: {summary.get('총_대화_턴')}")
        print(f"대화 요약: {summary.get('대화_요약')}")
        print(f"주요 이슈: {summary.get('주요_이슈')}")
        print(f"최고 위험 신호: {summary.get('최고_위험_신호')}")
        print(f"감지된 위험요인: {summary.get('감지된_위험요인')}")
        print(f"정서 변화: {summary.get('정서_변화')}")
        print(f"다음 대화 가이드: {summary.get('다음_대화_가이드')}")