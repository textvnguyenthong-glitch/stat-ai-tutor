import json

import pandas as pd
import streamlit as st
from tien_ich import ho_so

st.title("👤 Hồ sơ cá nhân")
hs = ho_so()

hs["ten"] = st.text_input("Họ tên", value=hs.get("ten", ""))
hs["lop"] = st.text_input("Lớp / trường", value=hs.get("lop", ""))
hs["muc_tieu"] = st.text_area("Mục tiêu học tập", value=hs.get("muc_tieu", ""), height=80)

st.divider()
st.markdown("### Tiến độ học tập")
ls = hs.get("lich_su", [])
if ls:
    df = pd.DataFrame(ls)
    diem = df["diem"].dropna() if "diem" in df else pd.Series(dtype=float)
    c1, c2, c3 = st.columns(3)
    c1.metric("Số lượt luyện tập", len(df))
    c2.metric("Điểm trung bình", f"{diem.astype(float).mean():.1f}" if len(diem) else "–")
    c3.metric("Số lỗi đã ghi nhận", int(df["loi"].apply(len).sum()) if "loi" in df else 0)

    co_diem = df[df["diem"].notna()] if "diem" in df else df.iloc[0:0]
    if len(co_diem):
        st.markdown("**Điểm theo thời gian**")
        st.line_chart(co_diem.reset_index()[["diem"]])
    st.markdown("**Lịch sử**")
    st.dataframe(
        df[["thoi_gian", "loai", "chu_de", "diem"]].iloc[::-1],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Chưa có hoạt động nào. Hãy thử làm trắc nghiệm hoặc vấn đáp.")

st.divider()
st.markdown("### Lưu và nạp hồ sơ")
st.caption("Dữ liệu chỉ nằm trong phiên làm việc. Hãy tải hồ sơ về máy để lần sau nạp lại.")
st.download_button(
    "⬇️ Tải hồ sơ về máy",
    json.dumps(hs, ensure_ascii=False, indent=1),
    file_name="ho_so_ai_classroom.json",
    mime="application/json",
)
tep = st.file_uploader("Nạp lại hồ sơ đã lưu", type=["json"])
if tep and st.button("Nạp hồ sơ"):
    try:
        du_lieu = json.load(tep)
        if isinstance(du_lieu, dict) and "lich_su" in du_lieu:
            du_lieu.setdefault("ten", "")
            du_lieu.setdefault("lop", "")
            du_lieu.setdefault("muc_tieu", "")
            st.session_state.ho_so = du_lieu
            st.rerun()
        else:
            st.error("Tệp hồ sơ không hợp lệ.")
    except Exception:
        st.error("Không đọc được tệp.")