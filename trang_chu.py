import streamlit as st

st.title("📊 AI Classroom")
st.subheader("Gia sư Xác suất thống kê bằng AI")
st.write("Hỏi bài, luyện đề, vấn đáp và theo dõi tiến bộ ngay trên một trang web duy nhất.")

st.page_link("tinh_nang/chat.py", label="Bắt đầu hỏi AI", icon="💬")
st.divider()

st.markdown("### Học và giải bài")
st.page_link("tinh_nang/quy_trinh.py", label="Quy trình giải bài 4 bước", icon="🧭")
st.caption("Hiểu đề, chọn phương pháp, tự giải, kiểm tra, có AI hướng dẫn từng bước.")
st.page_link("tinh_nang/ipad_live.py", label="Bảng vẽ và giọng nói", icon="🖊️")
st.caption("Viết tay bài giải rồi hỏi AI bằng giọng nói hoặc chữ.")

st.markdown("### Luyện tập")
st.page_link("tinh_nang/1_Cham_bai_barem.py", label="Chấm bài theo barem", icon="📝")
st.caption("AI chấm điểm từng ý và chỉ ra lỗi sai.")
st.page_link("tinh_nang/2_Sinh_bai_tu_luan.py", label="Sinh bài tự luận", icon="✍️")
st.caption("Ra đề theo chương và độ khó, kèm barem và lời giải.")
st.page_link("tinh_nang/trac_nghiem.py", label="Trắc nghiệm và câu hỏi 'Tại sao'", icon="✅")
st.caption("Luyện nhanh và kiểm tra hiểu bản chất.")
st.page_link("tinh_nang/van_dap.py", label="Vấn đáp lý thuyết", icon="🎤")
st.caption("AI hỏi miệng, bạn trả lời bằng chữ hoặc giọng nói.")

st.markdown("### Ôn tập và theo dõi")
st.page_link("tinh_nang/ban_do_tu_duy.py", label="Bản đồ tư duy", icon="🗺️")
st.page_link("tinh_nang/phan_tich_loi.py", label="Phân tích lỗi sai", icon="🔍")
st.page_link("tinh_nang/ho_so.py", label="Hồ sơ cá nhân", icon="👤")

st.markdown("### Cộng đồng")
st.page_link("tinh_nang/dien_dan.py", label="Diễn đàn và trợ giảng", icon="💬")

st.info("AI có thể mắc sai sót. Hãy đối chiếu với giáo trình hoặc giảng viên.")