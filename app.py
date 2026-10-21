import streamlit as st
from google import genai
from google.genai import types

# ====== CẤU HÌNH ====
MODEL = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = """
Bạn là STAT AI TUTOR, một gia sư Xác suất thống kê thân thiện cho sinh viên.

Yêu cầu:
- Giải thích từng bước, rõ ràng bằng tiếng Việt.
- Nêu công thức trước khi áp dụng.
- Giải thích ý nghĩa các ký hiệu và phép tính.
- Trình bày kết quả cuối cùng rõ ràng.
- Dùng LaTeX với dấu $...$ cho công thức.
- Nếu đề bài thiếu dữ kiện, hãy hỏi lại người dùng.
"""
# ======================

st.set_page_config(
    page_title="STAT AI TUTOR",
    page_icon="📊",
    layout="centered"
)

st.title("📊 STAT AI TUTOR")
st.caption(
    "Nhập một bài toán Xác suất thống kê để được hướng dẫn."
)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
   
    


# Lưu lịch sử hội thoại
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Nhập câu hỏi
if prompt := st.chat_input("Nhập bài toán của bạn..."):

    if not api_key:
        st.warning("Vui lòng nhập Gemini API Key ở thanh bên trái.")
        st.stop()

    # Hiển thị câu hỏi
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chỉ tạo bản sao lịch sử để gửi API.
    # Không lưu câu hỏi vào lịch sử chính thức cho đến khi xử lý xong.
    history = st.session_state.messages + [
        {"role": "user", "content": prompt}
    ]

    contents = [
        types.Content(
            role="user" if message["role"] == "user" else "model",
            parts=[types.Part(text=message["content"])]
        )
        for message in history
    ]

    with st.chat_message("assistant"):
        try:
            client = genai.Client(api_key=api_key)

            with st.spinner("AI đang giải bài toán..."):
                response = client.models.generate_content(
                    model=MODEL,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.3
                    )
                )

            answer = response.text

            if not answer:
                st.warning(
                    "AI chưa tạo được câu trả lời. "
                    "Bạn hãy thử gửi lại đề bài."
                )
            else:
                st.markdown(answer)

                # Chỉ lưu hội thoại khi có câu trả lời
                st.session_state.messages = history + [
                    {"role": "assistant", "content": answer}
                ]

        except Exception as e:
            error_message = str(e)

            if "404" in error_message or "NOT_FOUND" in error_message:
                st.error(
                    f"Không tìm thấy model '{MODEL}' hoặc model "
                    "không khả dụng với API key hiện tại. "
                    "Hãy kiểm tra danh sách model được hỗ trợ."
                )
            elif "API_KEY_INVALID" in error_message or "401" in error_message:
                st.error(
                    "API key không hợp lệ. "
                    "Hãy kiểm tra lại Gemini API Key."
                )
            elif "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
                st.error(
                    "API đã đạt giới hạn sử dụng hoặc hạn mức hiện tại. "
                    "Hãy kiểm tra quota và giới hạn của API key."
                )
            else:
                st.error(f"Có lỗi khi gọi Gemini API: {error_message}")