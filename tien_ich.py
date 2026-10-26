"""Các hàm dùng chung cho mọi tính năng của AI Classroom."""
import json
import re
from datetime import datetime

import streamlit as st
from google import genai
from google.genai import types

MODEL = "gemini-3.5-flash"

CHUONG = [
    "Xác suất cơ bản",
    "Biến ngẫu nhiên rời rạc",
    "Biến ngẫu nhiên liên tục",
    "Phân phối chuẩn",
    "Mẫu và ước lượng",
    "Kiểm định giả thuyết",
    "Hồi quy và tương quan",
]


def lay_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return st.sidebar.text_input(
            "Gemini API Key", type="password", key="khoa_api_chung"
        )


def goi_ai(noi_dung, system, json_mode=False):
    """Gọi Gemini. noi_dung có thể là chuỗi, danh sách Part hoặc danh sách Content."""
    key = lay_api_key()
    if not key:
        st.warning("Hãy nhập API Key ở thanh bên trái.")
        st.stop()
    try:
        client = genai.Client(api_key=key)
        cfg = types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json" if json_mode else "text/plain",
        )
        r = client.models.generate_content(
            model=MODEL, contents=noi_dung, config=cfg
        )
        return r.text or ""
    except Exception as e:
        st.error(f"Có lỗi: {e}")
        st.stop()


def doc_json(text):
    s = (text or "").strip()
    s = re.sub(r"^```(?:json)?|```$", "", s, flags=re.MULTILINE).strip()
    try:
        return json.loads(s)
    except Exception:
        return None


def ho_so():
    if "ho_so" not in st.session_state:
        st.session_state.ho_so = {
            "ten": "",
            "lop": "",
            "muc_tieu": "",
            "lich_su": [],
        }
    return st.session_state.ho_so


def ghi_lich_su(loai, chu_de, diem=None, loi=None):
    ho_so()["lich_su"].append(
        {
            "thoi_gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "loai": loai,
            "chu_de": chu_de,
            "diem": diem,
            "loi": loi or [],
        }
    )