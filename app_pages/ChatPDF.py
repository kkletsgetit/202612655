import streamlit as st

st.title("📄 ChatPDF (File Search)")
st.write(
    "PDF 파일을 업로드하고, OpenAI File Search를 통해 문서 내용에 대해 대화를"
    " 나누세요."
)

# API 클라이언트 확인
if "openai_client" not in st.session_state:
  st.warning("⚠️ 왼쪽 사이드바에 OpenAI API Key를 먼저 입력해주세요.")
  st.stop()

client = st.session_state["openai_client"]

# 세션 상태 초기화
if "pdf_messages" not in st.session_state:
  st.session_state.pdf_messages = []
if "vector_store_id" not in st.session_state:
  st.session_state.vector_store_id = None
if "uploaded_file_name" not in st.session_state:
  st.session_state.uploaded_file_name = None

# 1. 파일이 아직 업로드되지 않았거나 'Leave'를 눌러 초기화된 경우 -> 업로드 화면
if not st.session_state.vector_store_id:
  st.info(
      "대화할 PDF 파일을 업로드하세요. (예: 논문, 보고서, 매뉴얼 등)"
  )
  uploaded_file = st.file_uploader(
      "PDF 파일 업로드 (1개)", type=["pdf"], key="pdf_uploader"
  )

  if uploaded_file is not None:
    if st.button("🚀 문서 색인(Vector Store) 생성하기", type="primary"):
      with st.spinner(
          "PDF 파일을 OpenAI에 업로드하고 벡터 스토어를 생성 중입니다..."
      ):
        try:
          # 1단계: OpenAI Files API에 파일 업로드
          file_response = client.files.create(
              file=uploaded_file, purpose="assistants"
          )
          file_id = file_response.id

          # 2단계: Vector Store 생성 및 파일 등록
          vector_store = client.beta.vector_stores.create(
              name=f"PDF_Store_{uploaded_file.name}"
          )
          vector_store_id = vector_store.id

          # 파일 첨부 및 처리 완료 대기
          client.beta.vector_stores.files.create_and_poll(
              vector_store_id=vector_store_id, file_id=file_id
          )

          # 세션에 저장 (한 번만 만들도록 유지)
          st.session_state.vector_store_id = vector_store_id
          st.session_state.uploaded_file_name = uploaded_file.name
          st.session_state.pdf_messages = []

          st.success(
              f"'{uploaded_file.name}' 문서 분석이 완료되었습니다! 아래 채팅창을"
              " 이용해주세요."
          )
          st.rerun()

        except Exception as e:
          st.error(f"벡터 스토어 생성 중 오류가 발생했습니다: {e}")

# 2. Vector Store가 준비된 경우 -> 대화 화면 및 컨트롤 버튼
else:
  st.success(f"현재 대화 중인 문서: **{st.session_state.uploaded_file_name}**")

  # 상단 컨트롤 버튼 (Clear & Leave)
  col1, col2, _ = st.columns([1, 1, 4])
  with col1:
    if st.button("🧹 Clear"):
      st.session_state.pdf_messages = []
      st.rerun()
  with col2:
    if st.button("🚪 Leave (파일 재선택)"):
      # 세션 초기화 및 벡터 스토어 정보 삭제 처리
      st.session_state.vector_store_id = None
      st.session_state.uploaded_file_name = None
      st.session_state.pdf_messages = []
      st.rerun()

  st.markdown("---")

  # 기존 대화 기록 출력
  for message in st.session_state.pdf_messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # 사용자 질의 입력 (File Search 도구 활용 Responses API 호출)
  if prompt := st.chat_input("PDF 문서 내용에 대해 질문하세요..."):
    # 사용자 메시지 저장 및 출력
    st.session_state.pdf_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    # 어시스턴트 응답 (File Search tool + 스트리밍)
    with st.chat_message("assistant"):
      try:
        stream = client.responses.create(
            model="gpt-4o",  # File Search 기능을 지원하는 모델 지정
            input=st.session_state.pdf_messages,
            tools=[{
                "type": "file_search",
                "vector_store_ids": [st.session_state.vector_store_id],
            }],
            stream=True,
        )
        # 스트리밍 실시간 출력 및 결과 반환
        response = st.write_stream(stream)

        # 어시스턴트 응답 저장
        st.session_state.pdf_messages.append(
            {"role": "assistant", "content": response}
        )

      except Exception as e:
        st.error(f"응답 생성 중 오류가 발생했습니다: {e}")