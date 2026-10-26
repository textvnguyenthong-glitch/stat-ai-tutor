import streamlit as st
from google.genai import types
from tien_ich import goi_ai, doc_json, ghi_lich_su

st.title("🧭 Quy trình giải bài 4 bước")
st.caption("Hiểu đề → Chọn phương pháp → Tự giải → Kiểm tra")

CAC_BUOC = ["Bước 1: Hiểu đề", "Bước 2: Chọn phương pháp", "Bước 3: Tự giải", "Bước 4: Kiểm tra"]

P1 = """Bạn là gia sư Xác suất thống kê. Giúp sinh viên HIỂU ĐỀ:
liệt kê dữ kiện đã cho (kèm ký hiệu), đại lượng cần tìm, dạng bài, điều kiện ngầm.
Tuyệt đối KHÔNG giải và KHÔNG nêu đáp án. Tiếng Việt, LaTeX $...$."""

P2 = """Bạn là gia sư Xác suất thống kê. Dựa trên đề và phần phân tích, gợi ý PHƯƠNG PHÁP:
công thức/định lý cần dùng, vì sao chọn, các bước giải ở mức phác thảo.
KHÔNG thay số, KHÔNG nêu đáp án. Tiếng Việt, LaTeX $...$."""

P3 = """Bạn là gia sư Xác suất thống kê. Nhận xét bài làm của sinh viên từng bước:
bước nào đúng, bước nào sai và vì sao. Nếu bài chưa đúng, chỉ gợi ý hướng sửa,
KHÔNG đưa đáp án cuối. Tiếng Việt, LaTeX $...$."""

P4 = """Bạn là gia sư Xác suất thống kê. Đưa lời giải chuẩn, kiểm tra tính hợp lý của kết quả,
và đánh giá bài làm của sinh viên. Trả về DUY NHẤT một JSON gồm:
"loi_giai" (chuỗi markdown), "kiem_tra" (chuỗi markdown: kết quả có hợp lý không, cách kiểm tra lại),
"diem" (số 0-10), "loi_sai" (mảng chuỗi ngắn mô tả lỗi của sinh viên, rỗng nếu không có).
Tiếng Việt, LaTeX $...$."""

if "qt" not in st.session_state:
    st.session_state.qt = {"buoc": 0, "de": "", "b1": "", "b2": "", "b3": "", "bai": "", "b4": None}
qt = st.session_state.qt

st.progress((qt["buoc"] + 1) / 4, text=CAC_BUOC[qt["buoc"]])

if qt["buoc"] == 0:
    de = st.text_area("Nhập đề bài", value=qt["de"], height=150)
    if st.button("Phân tích đề", type="primary"):
        if not de.strip():
            st.warning("Hãy nhập đề bài.")
        else:
            qt["de"] = de
            with st.spinner("Đang phân tích..."):
                qt["b1"] = goi_ai(f"ĐỀ BÀI:\n{de}", P1)
    if qt["b1"]:
        st.markdown(qt["b1"])
        if st.button("Sang bước 2 →"):
            qt["buoc"] = 1
            st.rerun()

elif qt["buoc"] == 1:
    st.markdown("**Đề bài:** " + qt["de"])
    if not qt["b2"]:
        with st.spinner("Đang gợi ý phương pháp..."):
            qt["b2"] = goi_ai(f"ĐỀ BÀI:\n{qt['de']}\n\nPHÂN TÍCH:\n{qt['b1']}", P2)
    st.markdown(qt["b2"])
    if st.button("Sang bước 3 →"):
        qt["buoc"] = 2
        st.rerun()

elif qt["buoc"] == 2:
    st.markdown("**Đề bài:** " + qt["de"])
    bai = st.text_area("Bài làm của bạn", value=qt["bai"], height=200)
    anh = st.file_uploader("Hoặc tải ảnh bài làm", type=["png", "jpg", "jpeg", "webp"])
    if st.button("Nhận xét bài làm", type="primary"):
        if not (bai.strip() or anh):
            st.warning("Hãy nhập bài làm hoặc tải ảnh.")
        else:
            qt["bai"] = bai
            parts = [types.Part(text=f"ĐỀ BÀI:\n{qt['de']}\n\nBÀI LÀM:\n{bai}")]
            if anh:
                parts.append(types.Part.from_bytes(data=anh.getvalue(), mime_type=anh.type))
            with st.spinner("Đang nhận xét..."):
                qt["b3"] = goi_ai(parts, P3)
    if qt["b3"]:
        st.markdown(qt["b3"])
        if st.button("Sang bước 4 →"):
            qt["buoc"] = 3
            st.rerun()

else:
    if qt["b4"] is None:
        with st.spinner("Đang kiểm tra..."):
            raw = goi_ai(
                f"ĐỀ BÀI:\n{qt['de']}\n\nBÀI LÀM:\n{qt['bai']}\n\nNHẬN XÉT:\n{qt['b3']}",
                P4,
                json_mode=True,
            )
        kq = doc_json(raw) or {"loi_giai": raw, "kiem_tra": "", "diem": None, "loi_sai": []}
        qt["b4"] = kq
        ghi_lich_su("Quy trình 4 bước", "Giải bài", kq.get("diem"), kq.get("loi_sai"))
    kq = qt["b4"]
    if kq.get("diem") is not None:
        st.metric("Điểm bài làm", f"{kq['diem']}/10")
    st.markdown("### Lời giải chuẩn")
    st.markdown(kq.get("loi_giai", ""))
    st.markdown("### Kiểm tra kết quả")
    st.markdown(kq.get("kiem_tra", ""))

st.divider()
if st.button("Làm bài mới"):
    del st.session_state["qt"]
    st.rerun()