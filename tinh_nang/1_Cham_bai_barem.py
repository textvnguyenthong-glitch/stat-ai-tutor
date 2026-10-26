import streamlit as st
from google import genai
from google.genai import types

MODEL = "gemini-3.5-flash"

CHAM_PROMPT = """
Bạn là giảng viên Xác suất thống kê chấm bài theo barem.
Bạn nhận: đề bài, barem (nếu có) và bài làm của sinh viên.
Hãy:
1. Chấm điểm từng ý theo barem (nếu không có barem, tự đề xuất barem thang 10 rồi chấm).
2. Chỉ rõ lỗi sai: sai công thức, sai tính toán, thiếu lập luận.
3. Đưa ra lời giải đúng ngắn gọn từng bước.
4. Gợi ý chiến lược làm bài và những lỗi cần tránh.
Trả lời bằng tiếng Việt, dùng LaTeX $...$ cho công thức.
"""

st.set_page_config(page_title="Chấm bài theo barem", page_icon="📝")
st.title("📝 Chấm bài theo barem")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

de_bai = st.text_area("Đề bài", height=120)
barem = st.text_area("Barem / đáp án (không bắt buộc)", height=120)
bai_lam = st.text_area("Bài làm của sinh viên", height=200)
anh = st.file_uploader(
    "Hoặc tải ảnh bài làm", type=["png", "jpg", "jpeg", "webp"]
)

if st.button("Chấm bài", type="primary"):
    if not api_key:
        st.warning("Hãy nhập API Key ở thanh bên trái.")
        st.stop()
    if not (bai_lam.strip() or anh):
        st.warning("Hãy nhập bài làm hoặc tải ảnh.")
        st.stop()

    parts = [
        types.Part(
            text=f"ĐỀ BÀI:\n{de_bai}\n\nBAREM:\n{barem or '(không có)'}\n\nBÀI LÀM:\n{bai_lam}"
        )
    ]
    if anh:
        parts.append(
            types.Part.from_bytes(data=anh.getvalue(), mime_type=anh.type)
        )

    try:
        client = genai.Client(api_key=api_key)
        with st.spinner("Đang chấm..."):
            response = client.models.generate_content(
                model=MODEL,
                contents=parts,
                config=types.GenerateContentConfig(
                    system_instruction=CHAM_PROMPT
                ),
            )
        st.markdown(response.text)
    except Exception as e:
        st.error(f"Có lỗi: {e}")