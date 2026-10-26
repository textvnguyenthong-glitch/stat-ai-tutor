import json
import streamlit as st
from google import genai
from google.genai import types

MODEL = "gemini-3.5-flash"

CHUONG = [
    "Xác suất cơ bản",
    "Biến ngẫu nhiên rời rạc",
    "Biến ngẫu nhiên liên tục",
    "Phân phối chuẩn",
    "Mẫu và ước lượng",
    "Kiểm định giả thuyết",
    "Hồi quy và tương quan",
]

PROMPT = """
Bạn là giảng viên Xác suất thống kê, chuyên ra đề tự luận cho sinh viên.
Hãy ra đề theo yêu cầu. Số liệu phải hợp lý, đề phải giải được.
Trả về DUY NHẤT một mảng JSON. Mỗi phần tử có đúng 3 khóa:
- "de_bai": nội dung đề bài (có thể nhiều ý a, b, c)
- "barem": barem chấm điểm theo thang 10, ghi rõ điểm từng ý
- "loi_giai": lời giải chi tiết từng bước
Viết bằng tiếng Việt, dùng LaTeX với dấu $...$ cho công thức.
"""

st.set_page_config(page_title="Sinh bài tự luận", page_icon="✍️")
st.title("✍️ Sinh bài tự luận")
st.caption("Lời giải do AI tạo, hãy kiểm tra lại trước khi dùng chính thức.")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

chuong = st.selectbox("Chương / chủ đề", CHUONG)
do_kho = st.select_slider("Độ khó", ["Dễ", "Trung bình", "Khó"], value="Trung bình")
so_cau = st.slider("Số câu", 1, 5, 2)
bai_mau = st.text_area(
    "Bài mẫu để sinh bài tương tự (không bắt buộc)", height=100
)

if st.button("Sinh đề", type="primary"):
    if not api_key:
        st.warning("Hãy nhập API Key ở thanh bên trái.")
        st.stop()

    yeu_cau = f"Chủ đề: {chuong}\nĐộ khó: {do_kho}\nSố câu: {so_cau}"
    if bai_mau.strip():
        yeu_cau += f"\nHãy ra bài tương tự bài mẫu sau:\n{bai_mau}"

    try:
        client = genai.Client(api_key=api_key)
        with st.spinner("Đang ra đề..."):
            response = client.models.generate_content(
                model=MODEL,
                contents=yeu_cau,
                config=types.GenerateContentConfig(
                    system_instruction=PROMPT,
                    response_mime_type="application/json",
                ),
            )
        try:
            st.session_state.de_tu_luan = json.loads(response.text)
            st.session_state.de_tho = None
        except Exception:
            st.session_state.de_tu_luan = None
            st.session_state.de_tho = response.text
    except Exception as e:
        st.error(f"Có lỗi: {e}")

# Hiển thị kết quả
de = st.session_state.get("de_tu_luan")
if de:
    for i, c in enumerate(de, start=1):
        st.markdown(f"### Câu {i}")
        st.markdown(c.get("de_bai", ""))
        with st.expander("Xem barem và lời giải"):
            st.markdown("**Barem:**")
            st.markdown(c.get("barem", ""))
            st.markdown("**Lời giải:**")
            st.markdown(c.get("loi_giai", ""))
elif st.session_state.get("de_tho"):
    st.markdown(st.session_state.de_tho)