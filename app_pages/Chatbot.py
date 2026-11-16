import streamlit as st

st.title("📚 국립부경대학교 도서관 챗봇")
st.write(
    "국립부경대학교 도서관 규정을 바탕으로 질문에 답변해 주는 AI 챗봇입니다."
)

# Clear 버튼을 위한 on_click 콜백 함수
def clear_library_chat():
  st.session_state.library_messages = []


# API 클라이언트 확인
if "openai_client" not in st.session_state:
  st.warning("⚠️ 왼쪽 사이드바에 OpenAI API Key를 먼저 입력해주세요.")
  st.stop()

client = st.session_state["openai_client"]

# 국립부경대학교 도서관 규정 문자열 정의 (Instructions 주입용)
LIBRARY_REGULATIONS = """
[국립부경대학교 도서관 규정 및 운영세칙 요약]
제1조(목적) 이 규정은 국립부경대학교 도서관의 조직과 운영에 관한 사항을 규정함을 목적으로 합니다.
제2조(휴관일) 도서관의 휴관일은 다음 각 호와 같습니다.
1. 정부가 지정한 공휴일
2. 개교기념일 (5월 10일)
3. 도서관장이 필요하다고 인정하는 임시 휴관일 (장서 점검 및 시설 보수 등)
제3조(대출 자격 및 권수) 도서관 자료의 대출 자격 및 권수는 다음과 같습니다.
1. 전임교원: 대출 20권 / 기간 30일
2. 직원 및 조교: 대출 10권 / 기간 15일
3. 대학원생 (석·박사): 대출 15권 / 기간 20일
4. 학부생 (학사과정 재학생): 대출 5권 / 기간 10일 (※ 도서관 운영세칙에 따라 학부생은 일반적으로 5권까지 대출 가능)
제4조(반납 연기) 대출한 자료는 반납예정일 전 2회까지 연기가 가능합니다. (단, 예약 도서가 있는 경우는 제외)
"""

# 도서관 전용 대화 기록 저장용 세션 상태 초기화
if "library_messages" not in st.session_state:
  st.session_state.library_messages = []

# 대화 초기화 버튼
st.button("🧹 대화 내용 초기화", on_click=clear_library_chat)

# 기존 대화 기록 출력
for message in st.session_state.library_messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# 사용자 입력 받기
if prompt := st.chat_input(
    "도서관 규정에 대해 무엇이든 물어보세요 (예: 휴관일, 대출 권수 등)..."
):
  # 1. 사용자 메시지 저장 및 출력
  st.session_state.library_messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # 2. 어시스턴트 응답 (Responses API + instructions 규정 주입 + 스트리밍)
  with st.chat_message("assistant"):
    try:
      stream = client.responses.create(
          model="gpt-6-luna",
          input=st.session_state.library_messages,
          instructions=LIBRARY_REGULATIONS,  # 규정 데이터 주입
          stream=True,
      )
      # 실시간 스트리밍 출력 및 완성본 반환
      response = st.write_stream(stream)

      # 3. 어시스턴트 응답 저장
      st.session_state.library_messages.append(
          {"role": "assistant", "content": response}
      )

    except Exception as e:
      st.error(f"응답 생성 중 오류가 발생했습니다: {e}")