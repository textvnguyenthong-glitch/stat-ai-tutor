import streamlit as st

st.set_page_config(page_title="AI Classroom", page_icon="📊")

pg = st.navigation(
    {
        "AI Classroom": [
            st.Page("tinh_nang/trang_chu.py", title="Trang chủ", icon="🏠", default=True),
            st.Page("tinh_nang/chat.py", title="Chat với AI", icon="💬"),
        ],
        "Học và giải bài": [
            st.Page("tinh_nang/quy_trinh.py", title="Quy trình 4 bước", icon="🧭"),
            st.Page("tinh_nang/ipad_live.py", title="Bảng vẽ và giọng nói", icon="🖊️"),
        ],
        "Luyện tập": [
            st.Page("tinh_nang/1_Cham_bai_barem.py", title="Chấm bài theo barem", icon="📝"),
            st.Page("tinh_nang/2_Sinh_bai_tu_luan.py", title="Sinh bài tự luận", icon="✍️"),
            st.Page("tinh_nang/trac_nghiem.py", title="Trắc nghiệm và Tại sao", icon="✅"),
            st.Page("tinh_nang/van_dap.py", title="Vấn đáp lý thuyết", icon="🎤"),
        ],
        "Ôn tập và theo dõi": [
            st.Page("tinh_nang/ban_do_tu_duy.py", title="Bản đồ tư duy", icon="🗺️"),
            st.Page("tinh_nang/phan_tich_loi.py", title="Phân tích lỗi sai", icon="🔍"),
            st.Page("tinh_nang/ho_so.py", title="Hồ sơ cá nhân", icon="👤"),
        ],
        "Cộng đồng": [
            st.Page("tinh_nang/dien_dan.py", title="Diễn đàn và trợ giảng", icon="💬"),
        ],
    }
)
pg.run()