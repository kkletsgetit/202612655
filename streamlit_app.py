import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="OpenAI Multi-page App", page_icon="🤖", layout="wide"
)

# 사이드바: 어느 페이지에서나 공통으로 보이며 값이 유지됨
with st.sidebar:
  st.header("🔑 설정")
  api_key = st.text_input("OpenAI API Key", type="password")

  if api_key:
    st.session_state["openai_client"] = OpenAI(api_key=api_key)
    st.success("API Key가 등록되었습니다.")
  else:
    if "openai_client" not in st.session_state:
      st.info("사이드바에 OpenAI API Key를 입력해주세요.")

# 네비게이션 설정 (app_pages 폴더 지정)
pg = st.navigation([
    st.Page("app_pages/Home.py", title="Home", icon=":material/home:"),
    st.Page("app_pages/Chat.py", title="Chat", icon=":material/chat:"),
    st.Page(
        "app_pages/Chatbot.py", title="도서관 챗봇", icon=":material/library_books:"
    ),
    st.Page("app_pages/ChatPDF.py", title="ChatPDF", icon=":material/picture_as_pdf:"),
])

# 네비게이션 실행
pg.run()