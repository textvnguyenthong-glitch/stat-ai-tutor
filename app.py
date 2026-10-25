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


def hien_thi(m):
    for f in m.get("files", []):
        if f["type"].startswith("image/"):
            st.image(f["data"])
        else:
            st.caption("📎 " + f["name"])
    if m.get("audio"):
        st.audio(m["audio"], format="audio/wav")
    if m["content"]:
        st.markdown(m["content"])


def tao_noi_dung(m):
    parts = []
    for f in m.get("files", []):
        parts.append(types.Part.from_bytes(data=f["data"], mime_type=f["type"]))
    if m.get("audio"):
        parts.append(types.Part.from_bytes(data=m["audio"], mime_type="audio/wav"))
    if m["content"]:
        parts.append(types.Part(text=m["content"]))
    elif m["role"] == "user":
        parts.append(types.Part(text="Hãy xem nội dung đính kèm (ảnh, file hoặc ghi âm) và giải bài toán trong đó."))
    return types.Content(
        role="user" if m["role"] == "user" else "model", parts=parts
    )


# Hiển thị lịch sử
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        hien_thi(m)

# Khung nhập: gõ chữ, kéo thả ảnh/file, hoặc ghi âm
prompt = st.chat_input(
    "Nhập bài toán, kéo thả ảnh/file, hoặc bấm micro để nói...",
    accept_file="multiple",
    file_type=["png", "jpg", "jpeg", "webp", "pdf", "txt"],
    accept_audio=True,
)

if prompt:
    if not api_key:
        st.warning("Hãy nhập API Key ở thanh bên trái trước.")
        st.stop()

    files = [
        {"name": f.name, "type": f.type, "data": f.getvalue()}
        for f in (prompt.files or [])
    ]
    audio = prompt.audio.getvalue() if prompt.audio else None
    tong = sum(len(f["data"]) for f in files) + (len(audio) if audio else 0)
    if tong > 15 * 1024 * 1024:
        st.error("Tệp quá lớn (tối đa khoảng 15 MB mỗi lần gửi).")
        st.stop()

    tin_nhan = {
        "role": "user",
        "content": prompt.text or "",
        "files": files,
        "audio": audio,
    }
    st.session_state.messages.append(tin_nhan)
    with st.chat_message("user"):
        hien_thi(tin_nhan)

    contents = [tao_noi_dung(m) for m in st.session_state.messages]

    with st.chat_message("assistant"):
        try:
            client = genai.Client(api_key=api_key)
            with st.spinner("AI đang suy nghĩ..."):
                response = client.models.generate_content(
                    model=MODEL,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT
                    ),
                )
            answer = response.text
            st.markdown(answer)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
        except Exception as e:
            st.error(f"Có lỗi: {e}")