import pandas as pd
import streamlit as st
from tien_ich import goi_ai, doc_json, ho_so, ghi_lich_su, CHUONG

st.title("🔍 Phân tích lỗi sai")
st.caption("AI gom các lỗi bạn đã mắc (từ trắc nghiệm, vấn đáp, quy trình giải bài...) để chỉ ra điểm yếu và kế hoạch ôn tập.")

SYSTEM = """Bạn là giảng viên Xác suất thống kê phân tích lỗi sai của sinh viên.
Nhận danh sách lỗi. Gom thành các nhóm (ví dụ: nhầm khái niệm, sai công thức, sai tính toán,
đọc sai đề, thiếu lập luận) hoặc theo chương. Trả về DUY NHẤT một JSON:
"nhom_loi": mảng, mỗi phần tử có "ten", "so_lan" (số nguyên), "mo_ta", "cach_khac_phuc";
"tong_ket": chuỗi nhận xét chung; "ke_hoach": mảng chuỗi các việc nên ôn trong tuần tới.
Tiếng Việt."""

hs = ho_so()
tat_ca = [l for e in hs["lich_su"] for l in e.get("loi", [])]

st.markdown(f"Đã ghi nhận **{len(tat_ca)}** lỗi trong phiên này.")

with st.expander("Thêm lỗi thủ công"):
    chu_de = st.selectbox("Chương", CHUONG)
    ghi_chu = st.text_area("Mô tả lỗi / dán bài làm bị sai và lý do")
    if st.button("Thêm vào danh sách lỗi"):
        if ghi_chu.strip():
            ghi_lich_su("Nhập tay", chu_de, None, [f"[{chu_de}] {ghi_chu.strip()}"])
            st.rerun()
        else:
            st.warning("Hãy mô tả lỗi.")

if tat_ca:
    with st.expander("Xem danh sách lỗi"):
        for l in tat_ca:
            st.markdown("- " + l)

if st.button("Phân tích lỗi sai", type="primary"):
    if not tat_ca:
        st.info("Chưa có lỗi nào. Hãy làm vài bài trắc nghiệm hoặc thêm lỗi thủ công.")
    else:
        with st.spinner("Đang phân tích..."):
            raw = goi_ai("DANH SÁCH LỖI:\n" + "\n".join(tat_ca), SYSTEM, json_mode=True)
        kq = doc_json(raw)
        if isinstance(kq, dict):
            st.session_state.kq_loi = kq
        else:
            st.error("AI trả về sai định dạng, hãy bấm lại.")

kq = st.session_state.get("kq_loi")
if kq:
    nhom = kq.get("nhom_loi", [])
    if nhom:
        df = pd.DataFrame(nhom)
        if "ten" in df and "so_lan" in df:
            st.bar_chart(df.set_index("ten")["so_lan"])
        for n in nhom:
            with st.expander(f"{n.get('ten', '')} ({n.get('so_lan', '?')} lần)"):
                st.markdown(str(n.get("mo_ta", "")))
                st.markdown("**Cách khắc phục:** " + str(n.get("cach_khac_phuc", "")))
    st.markdown("### Nhận xét chung")
    st.markdown(str(kq.get("tong_ket", "")))
    st.markdown("### Kế hoạch ôn tập")
    for v in kq.get("ke_hoach", []):
        st.markdown("- " + str(v))