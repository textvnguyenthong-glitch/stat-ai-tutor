import streamlit as st
from google.genai import types
from tien_ich import goi_ai, doc_json, ghi_lich_su, CHUONG

st.title("🎤 Vấn đáp lý thuyết với AI")
st.caption("AI đóng vai giảng viên hỏi miệng. Bạn trả lời bằng chữ hoặc bấm micro để nói.")

SO_CAU = 5
SYSTEM = f"""Bạn là giảng viên Xác suất thống kê đang vấn đáp lý thuyết một sinh viên.
Quy tắc: hỏi từng câu một, tổng cộng {SO_CAU} câu, câu hỏi kiểm tra hiểu bản chất khái niệm.
Sau mỗi câu trả lời của sinh viên: nhận xét ngắn (đúng/thiếu/sai ở đâu), cho điểm x/10,
rồi hỏi câu tiếp theo. Sau câu thứ {SO_CAU} thì chỉ nhận xét và báo đã hết câu hỏi.
Nếu sinh viên gửi ghi âm thì hãy nghe và chấm như câu trả lời bình thường.
Tiếng Việt, ngắn gọn, LaTeX $...$."""

if "vd" not in st.session_state:
    st.session_state.vd = {"dang": False, "msgs": [], "chuong": "", "tong_ket": None}
vd = st.session_state.vd


def thanh_noi_dung(m):
    parts = []
    if m.get("audio"):
        parts.append(types.Part.from_bytes(data=m["audio"], mime_type="audio/wav"))
    if m["content"]:
        parts.append(types.Part(text=m["content"]))
    if not parts:
        parts.append(types.Part(text="(trống)"))
    return types.Content(role="user" if m["role"] == "user" else "model", parts=parts)


def lich_su_ai(chuong):
    mo_dau = types.Content(
        role="user",
        parts=[types.Part(text=f"Chủ đề vấn đáp: {chuong}. Hãy bắt đầu bằng câu hỏi số 1.")],
    )
    return [mo_dau] + [thanh_noi_dung(m) for m in vd["msgs"]]


if not vd["dang"]:
    chuong = st.selectbox("Chủ đề vấn đáp", CHUONG)
    if st.button("Bắt đầu vấn đáp", type="primary"):
        vd.update({"dang": True, "msgs": [], "chuong": chuong, "tong_ket": None})
        with st.spinner("Giảng viên đang chuẩn bị câu hỏi..."):
            cau1 = goi_ai(lich_su_ai(chuong), SYSTEM)
        vd["msgs"].append({"role": "assistant", "content": cau1})
        st.rerun()
else:
    st.markdown(f"**Chủ đề:** {vd['chuong']}")
    for m in vd["msgs"]:
        with st.chat_message(m["role"]):
            if m.get("audio"):
                st.audio(m["audio"], format="audio/wav")
            if m["content"]:
                st.markdown(m["content"])

    if vd["tong_ket"]:
        tk = vd["tong_ket"]
        st.metric("Điểm trung bình", f"{tk.get('diem_tb', '?')}/10")
        st.markdown("**Nhận xét:** " + str(tk.get("nhan_xet", "")))
        for lh in tk.get("lo_hong", []):
            st.markdown("- " + str(lh))
    else:
        prompt = st.chat_input(
            "Trả lời bằng chữ hoặc bấm micro...", accept_audio=True
        )
        if prompt:
            audio = prompt.audio.getvalue() if prompt.audio else None
            tin = {"role": "user", "content": prompt.text or "", "audio": audio}
            vd["msgs"].append(tin)
            with st.chat_message("user"):
                if audio:
                    st.audio(audio, format="audio/wav")
                if tin["content"]:
                    st.markdown(tin["content"])
            with st.chat_message("assistant"):
                with st.spinner("Giảng viên đang chấm..."):
                    tl = goi_ai(lich_su_ai(vd["chuong"]), SYSTEM)
                st.markdown(tl)
            vd["msgs"].append({"role": "assistant", "content": tl})

        if len(vd["msgs"]) >= 3 and st.button("Kết thúc và tổng kết"):
            with st.spinner("Đang tổng kết..."):
                raw = goi_ai(
                    lich_su_ai(vd["chuong"])
                    + [types.Content(role="user", parts=[types.Part(text=(
                        "Hãy kết thúc buổi vấn đáp. Trả về DUY NHẤT một JSON: "
                        '"diem_tb" (số 0-10), "nhan_xet" (chuỗi), '
                        '"lo_hong" (mảng chuỗi ngắn: các phần kiến thức còn yếu).'
                    ))])],
                    SYSTEM,
                    json_mode=True,
                )
            tk = doc_json(raw)
            if isinstance(tk, dict):
                vd["tong_ket"] = tk
                ghi_lich_su(
                    "Vấn đáp lý thuyết", vd["chuong"], tk.get("diem_tb"),
                    [f"[{vd['chuong']}] {x}" for x in tk.get("lo_hong", [])],
                )
                st.rerun()
            else:
                st.error("AI trả về sai định dạng, hãy bấm lại.")

    if st.button("Làm lại vấn đáp mới"):
        st.session_state.vd = {"dang": False, "msgs": [], "chuong": "", "tong_ket": None}
        st.rerun()