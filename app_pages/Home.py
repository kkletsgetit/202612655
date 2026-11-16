import base64
import streamlit as st
from openai import OpenAI

st.title("🤖 홈 (Home)")
st.write("질문 응답(gpt-6-luna)과 이미지 생성(gpt-image-2.6-flare) 기능 공간입니다.")

# API 클라이언트 확인
if "openai_client" not in st.session_state:
  st.warning("⚠️ 왼쪽 사이드바에 OpenAI API Key를 먼저 입력해주세요.")
  st.stop()

client = st.session_state["openai_client"]

# --- 1. 텍스트 질문 응답 섹션 ---
st.header("💬 텍스트 질문 응답 (gpt-6-luna)")


@st.cache_data(show_spinner="gpt-6-luna가 답변을 생성 중입니다...")
def get_luna_response(_client: OpenAI, prompt: str) -> str:
  response = _client.responses.create(
      model="gpt-6-luna",
      input=prompt,
  )
  return response.output_text


user_prompt = st.text_area(
    "질문을 입력하세요:",
    placeholder="무엇이든 물어보세요...",
    height=100,
    key="home_text_input",
)

if st.button("질문하기", type="primary"):
  if not user_prompt.strip():
    st.warning("질문 내용을 입력해주세요.")
  else:
    try:
      answer = get_luna_response(_client=client, prompt=user_prompt.strip())
      st.subheader("답변")
      st.markdown(answer)
    except Exception as e:
      st.error(f"API 호출 중 오류가 발생했습니다: {e}")

st.markdown("---")

# --- 2. 이미지 생성 섹션 ---
st.header("🎨 AI 이미지 생성 (gpt-image-2.6-flare)")

image_prompt = st.text_input(
    "생성할 이미지 프롬프트를 입력하세요:",
    placeholder="예: A cute red panda wearing astronaut clothes...",
    key="home_image_input",
)

if st.button("이미지 생성하기", type="primary"):
  if not image_prompt.strip():
    st.warning("이미지 프롬프트를 입력해주세요.")
  else:
    try:
      with st.spinner("이미지를 생성 중입니다... (수십 초가 소요될 수 있습니다)"):
        img = client.images.generate(
            model="gpt-image-2.6-flare",
            prompt=image_prompt.strip(),
        )
        image_bytes = base64.b64decode(img.data[0].b64_json)

      st.subheader("생성된 이미지")
      st.image(image_bytes, caption=image_prompt.strip())
    except Exception as e:
      st.error(f"이미지 생성 중 오류가 발생했습니다: {e}")