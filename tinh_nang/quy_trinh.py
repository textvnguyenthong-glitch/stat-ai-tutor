import streamlit as st
from google.genai import types
from tien_ich import goi_ai, doc_json, ghi_lich_su

st.title("🧭 Quy trình giải bài 4 bước")
st.caption("Hiểu đề → Chọn phương pháp → Tự giải → Kiểm tra")

CAC_BUOC = ["Bước 1: Hiểu đề", "Bước 2: Chọn phương pháp", "Bước 3: Tự giải", "Bước 4: Kiểm tra"]
LOAI_TEP = ["png", "jpg", "jpeg", "webp", "pdf"]

P1 = """Bạn là gia sư Xác suất thống kê. Giúp sinh viên HIỂU ĐỀ:
liệt kê dữ kiện đã cho (kèm ký hiệu), đại lượng cần tìm, dạng bài, điều kiện ngầm.
Đề bài có thể nằm trong ảnh hoặc PDF đính kèm, hãy đọc kỹ.
Tuyệt đối KHÔNG giải và KHÔNG nêu đáp án. Tiếng Việt, LaTeX $...$."""

P2 = """Bạn là gia sư Xác suất thống kê. Dựa trên đề và phần phân tích, gợi ý PHƯƠNG PHÁP:
công thức/định lý cần dùng, vì sao chọn, các bước giải ở mức phác thảo.
KHÔNG thay số, KHÔNG nêu đáp án. Tiếng Việt, LaTeX $...$."""

P3 = """Bạn là gia sư Xác suất thống kê. Nhận xét bài làm của sinh viên từng bước
(bài làm có thể là chữ hoặc ảnh/PDF đính kèm):
bước nào đúng, bước nào sai và vì sao. Nếu bài chưa đúng, chỉ gợi ý hướng sửa,
KHÔNG đưa đáp án cuối. Tiếng Việt, LaTeX $...$."""

P4 = """Bạn là gia sư Xác suất thống kê. Đưa lời giải chuẩn, kiểm tra tính hợp lý của kết quả,
và đánh giá bài làm của sinh viên. Trả về DUY NHẤT một JSON gồm:
"loi_giai" (chuỗi markdown), "kiem_tra" (chuỗi markdown: kết quả có hợp lý không, cách kiểm tra lại),
"diem" (số 0-10), "loi_sai" (mảng chuỗi ngắn mô tả lỗi của sinh viên, rỗng nếu không có).
Tiếng Việt, LaTeX $...$."""

if "qt" not in st.session_state:
    st.session_state.qt = {
        "buoc": 0, "de": "", "tep": [], "b1": "", "b2": "",
        "b3": "", "bai": "", "bai_tep": [], "b4": None,
    }
qt = st.session_state.qt
qt.setdefault("tep", [])
qt.setdefault("bai_tep", [])
lan = st.session_state.get("qt_lan", 0)


def luu_tep(ds):
    return [{"name": f.name, "type": f.type, "data": f.getvalue()} for f in ds]


def phan_tep(ds):
    return [types.Part.from_bytes(data=f["data"], mime_type=f["type"]) for f in ds]


def hien_tep(ds):
    for f in ds:
        if f["type"].startswith("image/"):
            st.image(f["data"], width=400)
        else:
            st.caption("📎 " + f["name"])


def de_day_du():
    return phan_tep(qt["tep"]) + [
        types.Part(text=f"ĐỀ BÀI:\n{qt['de'] or '(xem tệp đính kèm)'}")
    ]


def hien_de():
    if qt["de"]:
        st.markdown("**Đề bài:** " + qt["de"])
    hien_tep(qt["tep"])


st.progress((qt["buoc"] + 1) / 4, text=CAC_BUOC[qt["buoc"]])

if qt["buoc"] == 0:
    de = st.text_area("Nhập đề bài", value=qt["de"], height=150)
    tep = st.file_uploader(
        "Hoặc đính kèm ảnh / PDF đề bài",
        type=LOAI_TEP,
        accept_multiple_files=True,
        key=f"tep_de_{lan}",
    )
    if st.button("Phân tích đề", type="primary"):
        if not (de.strip() or tep):
            st.warning("Hãy nhập đề bài hoặc đính kèm ảnh/PDF.")
        elif sum(f.size for f in tep) > 15 * 1024 * 1024:
            st.error("Tệp quá lớn (tối đa khoảng 15 MB).")
        else:
            qt["de"] = de
            qt["tep"] = luu_tep(tep)
            with st.spinner("Đang phân tích..."):
                qt["b1"] = goi_ai(de_day_du(), P1)
    if qt["b1"]:
        st.markdown(qt["b1"])
        if st.button("Sang bước 2 →"):
            qt["buoc"] = 1
            st.rerun()

elif qt["buoc"] == 1:
    hien_de()
    if not qt["b2"]:
        with st.spinner("Đang gợi ý phương pháp..."):
            qt["b2"] = goi_ai(
                de_day_du() + [types.Part(text=f"PHÂN TÍCH:\n{qt['b1']}")], P2
            )
    st.markdown(qt["b2"])
    if st.button("Sang bước 3 →"):
        qt["buoc"] = 2
        st.rerun()

elif qt["buoc"] == 2:
    hien_de()
    bai = st.text_area("Bài làm của bạn", value=qt["bai"], height=200)
    anh = st.file_uploader(
        "Hoặc tải ảnh / PDF bài làm",
        type=LOAI_TEP,
        accept_multiple_files=True,
        key=f"tep_bai_{lan}",
    )
    if st.button("Nhận xét bài làm", type="primary"):
        if not (bai.strip() or anh):
            st.warning("Hãy nhập bài làm hoặc đính kèm ảnh/PDF.")
        elif sum(f.size for f in anh) > 15 * 1024 * 1024:
            st.error("Tệp quá lớn (tối đa khoảng 15 MB).")
        else:
            qt["bai"] = bai
            qt["bai_tep"] = luu_tep(anh)
            parts = (
                de_day_du()
                + [types.Part(text=f"BÀI LÀM:\n{bai}")]
                + phan_tep(qt["bai_tep"])
            )
            with st.spinner("Đang nhận xét..."):
                qt["b3"] = goi_ai(parts, P3)
    if qt["b3"]:
        st.markdown(qt["b3"])
        if st.button("Sang bước 4 →"):
            qt["buoc"] = 3
            st.rerun()

else:
    if qt["b4"] is None:
        parts = (
            de_day_du()
            + [types.Part(text=f"BÀI LÀM:\n{qt['bai']}")]
            + phan_tep(qt["bai_tep"])
            + [types.Part(text=f"NHẬN XÉT TRƯỚC ĐÓ:\n{qt['b3']}")]
        )
        with st.spinner("Đang kiểm tra..."):
            raw = goi_ai(parts, P4, json_mode=True)
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
    st.session_state.qt_lan = lan + 1
    st.rerun()