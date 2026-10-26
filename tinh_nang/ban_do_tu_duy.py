import streamlit as st
from tien_ich import goi_ai, doc_json, ghi_lich_su, CHUONG

st.title("🗺️ Bản đồ tư duy")
st.caption("AI tóm tắt một chủ đề thành sơ đồ nhánh để dễ nhớ.")

SYSTEM = """Bạn là giảng viên Xác suất thống kê. Tóm tắt chủ đề thành bản đồ tư duy.
Trả về DUY NHẤT một JSON dạng cây: {"ten": "...", "con": [ {"ten": "...", "con": [...]} ]}.
Tối đa 3 cấp, tối đa 6 nhánh cấp 1, mỗi nhánh tối đa 4 con. Tên nút ngắn gọn (dưới 8 từ),
tiếng Việt, không dùng dấu ngoặc kép."""

chuong = st.selectbox("Chủ đề", CHUONG)
ghi_chu = st.text_area("Hoặc dán nội dung bài giảng muốn tóm tắt (không bắt buộc)", height=120)


def tao_dot(goc):
    dong = [
        "digraph G {",
        "rankdir=LR;",
        'node [shape=box, style="rounded,filled", fillcolor="#EAF0FF", color="#2F5BEA", fontname="Helvetica"];',
        'edge [color="#8FA3DA"];',
    ]
    dem = [0]

    def them(n, cha):
        dem[0] += 1
        nid = f"n{dem[0]}"
        ten = str(n.get("ten", "")).replace('"', "'").replace("\\", " ").replace("\n", " ")
        mau = ', fillcolor="#FFB84D"' if cha is None else ""
        dong.append(f'{nid} [label="{ten}"{mau}];')
        if cha:
            dong.append(f"{cha} -> {nid};")
        for c in n.get("con") or []:
            if isinstance(c, dict):
                them(c, nid)

    them(goc, None)
    dong.append("}")
    return "\n".join(dong)


def dan_bai(n, cap=0):
    dong = ["  " * cap + "- " + str(n.get("ten", ""))]
    for c in n.get("con") or []:
        if isinstance(c, dict):
            dong += dan_bai(c, cap + 1)
    return dong


if st.button("Tạo bản đồ tư duy", type="primary"):
    yeu_cau = f"Chủ đề: {chuong}"
    if ghi_chu.strip():
        yeu_cau += f"\nNội dung cần tóm tắt:\n{ghi_chu}"
    with st.spinner("Đang vẽ bản đồ..."):
        raw = goi_ai(yeu_cau, SYSTEM, json_mode=True)
    cay = doc_json(raw)
    if isinstance(cay, dict) and cay.get("ten"):
        st.session_state.cay_tu_duy = cay
        ghi_lich_su("Bản đồ tư duy", chuong)
    else:
        st.error("AI trả về sai định dạng, hãy bấm tạo lại.")

cay = st.session_state.get("cay_tu_duy")
if cay:
    st.graphviz_chart(tao_dot(cay), use_container_width=True)
    with st.expander("Xem dạng danh sách (để chép vào vở)"):
        st.markdown("\n".join(dan_bai(cay)))