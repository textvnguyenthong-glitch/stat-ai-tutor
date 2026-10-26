import streamlit as st
from tien_ich import goi_ai, doc_json, ghi_lich_su, CHUONG

st.title("✅ Trắc nghiệm và câu hỏi 'Tại sao'")

chuong = st.selectbox("Chương / chủ đề", CHUONG)
do_kho = st.select_slider("Độ khó", ["Dễ", "Trung bình", "Khó"], value="Trung bình")

tab1, tab2 = st.tabs(["Trắc nghiệm", "Câu hỏi 'Tại sao'"])

P_TN = """Bạn là giảng viên Xác suất thống kê. Ra câu hỏi trắc nghiệm 4 lựa chọn.
Trả về DUY NHẤT một mảng JSON, mỗi phần tử có: "cau_hoi" (chuỗi),
"lua_chon" (mảng đúng 4 chuỗi, không ghi A/B/C/D ở đầu), "dap_an" (số nguyên 0-3, vị trí đáp án đúng),
"giai_thich" (chuỗi ngắn). Chỉ một đáp án đúng. Tiếng Việt, LaTeX $...$."""

P_TS = """Bạn là giảng viên Xác suất thống kê. Ra MỘT câu hỏi dạng 'Tại sao...' kiểm tra
hiểu bản chất khái niệm. Chỉ trả về nội dung câu hỏi, không kèm đáp án. Tiếng Việt, LaTeX $...$."""

P_CHAM = """Bạn là giảng viên Xác suất thống kê. Chấm câu trả lời của sinh viên cho câu hỏi 'Tại sao'.
Trả về DUY NHẤT một JSON: "diem" (số 0-10), "nhan_xet" (chuỗi), "dap_an_mau" (chuỗi).
Tiếng Việt, LaTeX $...$."""

with tab1:
    so_cau = st.slider("Số câu", 3, 10, 5)
    if st.button("Tạo bộ câu hỏi", type="primary"):
        with st.spinner("Đang tạo câu hỏi..."):
            raw = goi_ai(
                f"Chủ đề: {chuong}\nĐộ khó: {do_kho}\nSố câu: {so_cau}", P_TN, json_mode=True
            )
        ds = doc_json(raw)
        if isinstance(ds, list) and ds:
            st.session_state.tn = ds
            st.session_state.tn_id = st.session_state.get("tn_id", 0) + 1
            st.session_state.tn_chuong = chuong
        else:
            st.error("AI trả về sai định dạng, hãy bấm tạo lại.")

    tn = st.session_state.get("tn")
    if tn:
        idq = st.session_state.tn_id
        with st.form(f"form_tn_{idq}"):
            tra_loi = []
            for i, c in enumerate(tn):
                tra_loi.append(
                    st.radio(
                        f"**Câu {i + 1}.** {c.get('cau_hoi', '')}",
                        c.get("lua_chon", []),
                        index=None,
                        key=f"tn_{idq}_{i}",
                    )
                )
            nop = st.form_submit_button("Nộp bài")
        if nop:
            dung, loi, ket_qua = 0, [], []
            for i, c in enumerate(tn):
                lc = c.get("lua_chon", [])
                try:
                    dap_an = lc[int(c.get("dap_an", 0)) % len(lc)]
                except Exception:
                    dap_an = ""
                ok = tra_loi[i] == dap_an
                dung += 1 if ok else 0
                if ok:
                    ket_qua.append((True, f"Câu {i + 1}: đúng. {c.get('giai_thich', '')}"))
                else:
                    ket_qua.append((False, f"Câu {i + 1}: chưa đúng. Đáp án: {dap_an}. {c.get('giai_thich', '')}"))
                    loi.append(
                        f"[{st.session_state.get('tn_chuong', chuong)}] {c.get('cau_hoi', '')} | Bạn chọn: {tra_loi[i]} | Đúng: {dap_an}"
                    )
            diem = round(10 * dung / len(tn), 1)
            st.session_state.tn_kq = {"id": idq, "ket_qua": ket_qua, "diem": diem, "dung": dung, "tong": len(tn)}
            ghi_lich_su("Trắc nghiệm", st.session_state.get("tn_chuong", chuong), diem, loi)
        kq_tn = st.session_state.get("tn_kq")
        if kq_tn and kq_tn["id"] == idq:
            for ok, nd in kq_tn["ket_qua"]:
                (st.success if ok else st.error)(nd)
            st.metric("Điểm", f"{kq_tn['diem']}/10", f"{kq_tn['dung']}/{kq_tn['tong']} câu đúng")

with tab2:
    if st.button("Cho tôi một câu hỏi 'Tại sao'"):
        with st.spinner("Đang ra câu hỏi..."):
            st.session_state.ts_q = goi_ai(f"Chủ đề: {chuong}\nĐộ khó: {do_kho}", P_TS)
        st.session_state.ts_id = st.session_state.get("ts_id", 0) + 1
        st.session_state.ts_kq = None
        st.session_state.ts_chuong = chuong
    if st.session_state.get("ts_q"):
        st.markdown("### " + st.session_state.ts_q)
        tl = st.text_area("Câu trả lời của bạn", height=150, key=f"ts_tl_{st.session_state.ts_id}")
        if st.button("Chấm câu trả lời"):
            if not tl.strip():
                st.warning("Hãy nhập câu trả lời.")
            else:
                with st.spinner("Đang chấm..."):
                    raw = goi_ai(
                        f"CÂU HỎI: {st.session_state.ts_q}\n\nTRẢ LỜI:\n{tl}", P_CHAM, json_mode=True
                    )
                kq = doc_json(raw)
                if isinstance(kq, dict):
                    st.session_state.ts_kq = kq
                    d = kq.get("diem")
                    loi = [] if (d or 0) >= 7 else [f"[{st.session_state.get('ts_chuong', chuong)}] Câu 'Tại sao': {st.session_state.ts_q}"]
                    ghi_lich_su("Câu hỏi Tại sao", st.session_state.get("ts_chuong", chuong), d, loi)
                else:
                    st.error("AI trả về sai định dạng, hãy bấm chấm lại.")
        kq = st.session_state.get("ts_kq")
        if kq:
            st.metric("Điểm", f"{kq.get('diem', '?')}/10")
            st.markdown("**Nhận xét:** " + str(kq.get("nhan_xet", "")))
            with st.expander("Đáp án mẫu"):
                st.markdown(str(kq.get("dap_an_mau", "")))