import json
import os
import uuid
from datetime import datetime

import streamlit as st
from tien_ich import goi_ai, ho_so

st.title("💬 Diễn đàn và trợ giảng")
st.caption("Đặt câu hỏi cho cả lớp. Bấm 'Hỏi trợ giảng AI' trong bài viết để AI trả lời.")
st.warning(
    "Bản đầu lưu bài trên máy chủ nên có thể bị xóa khi ứng dụng khởi động lại. "
    "Muốn lưu lâu dài cần dùng cơ sở dữ liệu."
)

THU_MUC = "du_lieu"
FILE = os.path.join(THU_MUC, "dien_dan.json")
TG_PROMPT = """Bạn là trợ giảng môn Xác suất thống kê trên diễn đàn của lớp.
Trả lời câu hỏi của sinh viên rõ ràng, thân thiện, từng bước, bằng tiếng Việt, LaTeX $...$.
Nếu đã có các trả lời khác, hãy bổ sung hoặc chỉnh lại cho chính xác, đừng lặp lại."""


def doc():
    try:
        with open(FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def ghi(ds):
    os.makedirs(THU_MUC, exist_ok=True)
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(ds, f, ensure_ascii=False, indent=1)


def bay_gio():
    return datetime.now().strftime("%d/%m/%Y %H:%M")


hs = ho_so()
ds = doc()

with st.form("bai_moi", clear_on_submit=True):
    st.markdown("### Đặt câu hỏi mới")
    ten = st.text_input("Tên hiển thị", value=hs.get("ten") or "")
    tieu_de = st.text_input("Tiêu đề")
    noi_dung = st.text_area("Nội dung câu hỏi")
    gui = st.form_submit_button("Đăng bài")
if gui:
    if tieu_de.strip() and noi_dung.strip():
        ds.append(
            {
                "id": uuid.uuid4().hex[:8],
                "ten": ten.strip() or "Ẩn danh",
                "tieu_de": tieu_de.strip(),
                "noi_dung": noi_dung.strip(),
                "luc": bay_gio(),
                "tra_loi": [],
            }
        )
        ghi(ds)
        st.rerun()
    else:
        st.warning("Hãy nhập tiêu đề và nội dung.")

st.divider()
if not ds:
    st.info("Chưa có bài viết nào. Hãy là người đầu tiên đặt câu hỏi.")

for bai in reversed(ds):
    tieu = f"{bai['tieu_de']} · {bai['ten']} · {bai['luc']} · {len(bai['tra_loi'])} trả lời"
    with st.expander(tieu):
        st.markdown(bai["noi_dung"])
        for r in bai["tra_loi"]:
            st.markdown(f"**{r['ten']}** ({r['luc']}):")
            st.markdown(r["noi_dung"])
            st.divider()
        with st.form(f"rep_{bai['id']}", clear_on_submit=True):
            tl = st.text_area("Trả lời của bạn", key=f"tl_{bai['id']}")
            gui_tl = st.form_submit_button("Gửi trả lời")
        if gui_tl and tl.strip():
            bai["tra_loi"].append(
                {"ten": hs.get("ten") or "Ẩn danh", "noi_dung": tl.strip(), "luc": bay_gio()}
            )
            ghi(ds)
            st.rerun()
        if st.button("🤖 Hỏi trợ giảng AI", key=f"ai_{bai['id']}"):
            cac_tl = "\n".join(f"- {r['ten']}: {r['noi_dung']}" for r in bai["tra_loi"])
            with st.spinner("Trợ giảng đang trả lời..."):
                tra_loi_ai = goi_ai(
                    f"TIÊU ĐỀ: {bai['tieu_de']}\nCÂU HỎI: {bai['noi_dung']}\nCÁC TRẢ LỜI HIỆN CÓ:\n{cac_tl or '(chưa có)'}",
                    TG_PROMPT,
                )
            bai["tra_loi"].append({"ten": "🤖 Trợ giảng AI", "noi_dung": tra_loi_ai, "luc": bay_gio()})
            ghi(ds)
            st.rerun()