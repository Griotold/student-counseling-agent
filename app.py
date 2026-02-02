"""
app.py - 학생 정서 상담 Agent UI
"""
import streamlit as st
from src.agent import StudentCounselingAgent

# 페이지 설정
st.set_page_config(
    page_title="학생 정서 상담 AI",
    page_icon="💙",
    layout="wide"
)

# 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.agent = StudentCounselingAgent()
    st.session_state.is_ended = False

# 사이드바 - 정보
with st.sidebar:
    st.title("💙 학생 정서 상담 AI")
    
    st.markdown("---")
    
    st.markdown("### 📌 안내")
    st.info("""
    친구처럼 편하게 대화하면서
    감정 상태를 파악하고
    필요한 도움을 안내합니다.
    """)
    
    st.markdown("### 🚨 긴급 연락처")
    st.warning("""
    **자살예방상담**: 1393
    
    **청소년상담**: 1388
    
    **정신건강위기**: 1577-0199
    
    **응급**: 112, 119
    """)
    
    st.markdown("---")
    
    # 대화 초기화
    if st.button("🔄 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent.reset()
        st.session_state.is_ended = False
        st.rerun()
    
    # 통계
    st.markdown("### 📊 대화 정보")
    st.metric("대화 턴 수", st.session_state.agent.turn_count)

# 메인 화면
st.title("💙 학생 정서 상담 AI")
st.caption("친구처럼 편하게 이야기해보세요. 혼자가 아니에요.")

# 대화 종료 상태
if st.session_state.is_ended:
    st.error("⚠️ 대화가 종료되었습니다. 새로운 대화를 시작하려면 '대화 초기화'를 눌러주세요.")

# 대화 히스토리 표시
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    
    with st.chat_message(role):
        st.write(content)
        
        # Assistant 응답일 때 메타데이터 표시
        if role == "assistant" and "metadata" in msg:
            metadata = msg["metadata"]
            
            # 위험도 평가
            with st.expander("🔍 위험도 평가", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    # 자살 신호
                    signal = metadata.get("자살_신호", "낮음")
                    if signal == "높음":
                        st.error(f"🚨 자살 신호: **{signal}**")
                    elif signal == "중간":
                        st.warning(f"⚠️ 자살 신호: **{signal}**")
                    else:
                        st.success(f"✅ 자살 신호: **{signal}**")
                    
                    # 정서적 고통
                    pain = metadata.get("정서적_고통", "낮음")
                    if pain == "높음":
                        st.error(f"😢 정서적 고통: **{pain}**")
                    elif pain == "중간":
                        st.warning(f"😔 정서적 고통: **{pain}**")
                    else:
                        st.success(f"😊 정서적 고통: **{pain}**")
                
                with col2:
                    # 감지된 위험요인
                    risks = metadata.get("감지된_위험요인", [])
                    if risks:
                        st.write("**감지된 위험요인:**")
                        for risk in risks:
                            st.write(f"• {risk}")
                    else:
                        st.write("**감지된 위험요인:** 없음")
                
                # 권장 대응
                st.markdown("---")
                action = metadata.get("권장_대응", "")
                st.info(f"**권장 대응:** {action}")
            
            # 종합 결과
            if "종합_결과" in msg:
                st.markdown("---")
                st.success("### ✅ 대화 종료 - 종합 결과")
                
                summary = msg.get("종합_결과")  # ← .get() 추가
                
                if summary:  # ← 추가!
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("총 대화 턴", summary.get("총_대화_턴", 0))
                        st.write(f"**최고 위험 신호:** {summary.get('최고_위험_신호', '-')}")
                    
                    with col2:
                        st.write("**주요 이슈:**")
                        for issue in summary.get("주요_이슈", []):
                            st.write(f"• {issue}")
                    
                    st.markdown("**대화 요약:**")
                    st.write(summary.get("대화_요약", ""))
                    
                    st.markdown("**감지된 위험요인:**")
                    for risk in summary.get("감지된_위험요인", []):
                        st.write(f"• {risk}")
                    
                    if summary.get("정서_변화"):
                        st.markdown("**정서 변화:**")
                        st.write(summary.get("정서_변화"))
                    
                    st.markdown("**다음 대화 가이드:**")
                    st.write(summary.get("다음_대화_가이드", ""))
                else:
                    st.error("종합 결과를 생성하지 못했습니다.")


# 채팅 입력
if not st.session_state.is_ended:
    if prompt := st.chat_input("메시지를 입력하세요..."):
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.write(prompt)
        
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Agent 응답
        with st.spinner("생각 중..."):
            response = st.session_state.agent.chat(prompt)
        
        # Assistant 응답 표시
        with st.chat_message("assistant"):
            st.write(response["답변"])
            
            # 위험도 평가
            with st.expander("🔍 위험도 평가", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    signal = response.get("자살_신호", "낮음")
                    if signal == "높음":
                        st.error(f"🚨 자살 신호: **{signal}**")
                    elif signal == "중간":
                        st.warning(f"⚠️ 자살 신호: **{signal}**")
                    else:
                        st.success(f"✅자살 신호: **{signal}**")
                    
                    pain = response.get("정서적_고통", "낮음")
                    if pain == "높음":
                        st.error(f"😢 정서적 고통: **{pain}**")
                    elif pain == "중간":
                        st.warning(f"😔 정서적 고통: **{pain}**")
                    else:
                        st.success(f"😊 정서적 고통: **{pain}**")
                
                with col2:
                    risks = response.get("감지된_위험요인", [])
                    if risks:
                        st.write("**감지된 위험요인:**")
                        for risk in risks:
                            st.write(f"• {risk}")
                    else:
                        st.write("**감지된 위험요인:** 없음")
                
                st.markdown("---")
                action = response.get("권장_대응", "")
                st.info(f"**권장 대응:** {action}")
            
            # 종합 결과
            if response.get("종합_결과"):
                st.markdown("---")
                st.success("### ✅ 대화 종료 - 종합 결과")
                
                summary = response.get("종합_결과")  # ← 이미 .get() 사용
                
                if summary:  # ← 추가!
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("총 대화 턴", summary.get("총_대화_턴", 0))
                        st.write(f"**최고 위험 신호:** {summary.get('최고_위험_신호', '-')}")
                    
                    with col2:
                        st.write("**주요 이슈:**")
                        for issue in summary.get("주요_이슈", []):
                            st.write(f"• {issue}")
                    
                    st.markdown("**대화 요약:**")
                    st.write(summary.get("대화_요약", ""))
                    
                    st.markdown("**감지된 위험요인:**")
                    for risk in summary.get("감지된_위험요인", []):
                        st.write(f"• {risk}")
                    
                    if summary.get("정서_변화"):
                        st.markdown("**정서 변화:**")
                        st.write(summary.get("정서_변화"))
                    
                    st.markdown("**다음 대화 가이드:**")
                    st.write(summary.get("다음_대화_가이드", ""))
                else:
                    st.error("종합 결과를 생성하지 못했습니다.")
        
        # 메시지 저장
        message_data = {
            "role": "assistant",
            "content": response["답변"],
            "metadata": response
        }
        
        # 종합_결과가 실제로 있을 때만 추가
        if response.get("종합_결과"):
            message_data["종합_결과"] = response["종합_결과"]
        
        st.session_state.messages.append(message_data)
        
        # 종료 판단
        if response.get("종료_판단"):
            st.session_state.is_ended = True
        
        st.rerun()
else:
    st.chat_input("대화가 종료되었습니다. 초기화 버튼을 눌러주세요.", disabled=True)