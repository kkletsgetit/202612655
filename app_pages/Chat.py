import streamlit as st

st.title("💬 실시간 채팅 (Responses API)")
st.write("gpt-6-luna 모델과 스트리밍 방식으로 실시간 대화를 나누세요.")


# Clear 버튼을 위한 on_click 콜백 함수
def clear_chat():
  st.session_state.messages = []


# API 클라이언트 확인
if "openai_client" not in st.session_state:
  st.warning("⚠️ 왼쪽 사이드바에 OpenAI API Key를 먼저 입력해주세요.")
  st.stop()

client = st.session_state["openai_client"]

# 대화 내용 저장용 세션 상태 초기화
if "messages" not in st.session_state:
  st.session_state.messages = []

# 대화 초기화 버튼 (on_click 콜백 지정)
st.button("🧹 Clear (대화 초기화)", on_click=clear_chat)

# 기존 대화 기록 출력
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# 사용자 입력 및 Responses API 스트리밍 응답 처리
if prompt := st.chat_input("메시지를 입력하세요..."):
  # 1. 사용자 메시지 저장 및 출력
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # 2. 어시스턴트 응답 (Responses API + 스트리밍)
  with st.chat_message("assistant"):
    try:
      stream = client.responses.create(
          model="gpt-6-luna",
          input=st.session_state.messages,
          stream=True,
      )
      # st.write_stream을 통해 스트리밍 텍스트를 실시간으로 렌더링하고 완성된 텍스트 반환
      response = st.write_stream(stream)

      # 3. 완성된 어시스턴트 응답을 대화 기록에 저장
      st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:
      st.error(f"응답 생성 중 오류가 발생했습니다: {e}")