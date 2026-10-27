import json
import re

import streamlit as st
import streamlit.components.v1 as components
from google.genai import types
from tien_ich import goi_ai, doc_json, ghi_lich_su

st.title("🖊️ Bảng vẽ và đối thoại giọng nói")
st.caption("Viết tay bài giải, rồi trò chuyện với AI: bấm micro để nói, AI trả lời và đọc to cho bạn nghe. AI nhớ cả cuộc trò chuyện.")

BANG_VE = """
<div style="font-family:sans-serif">
  <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:8px">
    <button id="but">✏️ Bút</button>
    <button id="tay">🧽 Tẩy</button>
    <input type="color" id="mau" value="#1a1a1a">
    <input type="range" id="co" min="1" max="14" value="3">
    <button id="xoa">🗑️ Xóa hết</button>
    <a id="tai" download="bai-ve.png" href="#"><button>⬇️ Lưu ảnh</button></a>
  </div>
  <canvas id="c" height="420" style="border:1px solid #888;border-radius:8px;width:100%;height:420px;touch-action:none;background:#fff"></canvas>
</div>
<script>
const c = document.getElementById('c');
c.width = c.clientWidth || 700;
const ctx = c.getContext('2d');
ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height);
ctx.lineCap = 'round'; ctx.lineJoin = 'round';
let ve = false, chedo = 'but';
const mau = document.getElementById('mau'), co = document.getElementById('co');
document.getElementById('but').onclick = () => chedo = 'but';
document.getElementById('tay').onclick = () => chedo = 'tay';
document.getElementById('xoa').onclick = () => { ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height); };
document.getElementById('tai').onclick = function () { this.href = c.toDataURL('image/png'); };
function toado(e) { const r = c.getBoundingClientRect(); return [(e.clientX - r.left) * c.width / r.width, (e.clientY - r.top) * c.height / r.height]; }
c.addEventListener('pointerdown', e => { ve = true; c.setPointerCapture(e.pointerId); const [x, y] = toado(e); ctx.beginPath(); ctx.moveTo(x, y); });
c.addEventListener('pointermove', e => {
  if (!ve) return;
  const [x, y] = toado(e);
  ctx.strokeStyle = chedo === 'tay' ? '#fff' : mau.value;
  ctx.lineWidth = chedo === 'tay' ? co.value * 4 : co.value;
  ctx.lineTo(x, y); ctx.stroke();
});
c.addEventListener('pointerup', () => ve = false);
c.addEventListener('pointercancel', () => ve = false);
</script>
"""

DOC_TO = """
<div style="font-family:sans-serif;display:flex;gap:10px;align-items:center;flex-wrap:wrap">
  <button id="doc">🔊 Đọc to</button>
  <button id="dung">⏹️ Dừng</button>
  <label>Tốc độ <input type="range" id="tocdo" min="0.7" max="1.3" step="0.1" value="1"></label>
</div>
<script>
const text = __TEXT__;
const tuDong = __AUTO__;
function chonGiong() {
  const ds = speechSynthesis.getVoices();
  return ds.find(v => v.lang && v.lang.toLowerCase().startsWith('vi'));
}
function doc() {
  speechSynthesis.cancel();
  const cau = text.match(/[^.!?\\n]+[.!?]*/g) || [text];
  const giong = chonGiong();
  const toc = parseFloat(document.getElementById('tocdo').value);
  cau.forEach(s => {
    if (!s.trim()) return;
    const u = new SpeechSynthesisUtterance(s.trim());
    u.lang = 'vi-VN';
    if (giong) u.voice = giong;
    u.rate = toc;
    speechSynthesis.speak(u);
  });
}
document.getElementById('doc').onclick = doc;
document.getElementById('dung').onclick = () => speechSynthesis.cancel();
if (tuDong) setTimeout(doc, 400);
</script>
"""

with st.expander("Bảng vẽ", expanded=True):
    components.html(BANG_VE, height=520)
    st.info("Bấm **Lưu ảnh** (ảnh nằm trong thư mục Tải xuống), rồi tải ảnh lên ở ô bên dưới để AI xem. Nếu nút lưu không hoạt động, hãy chụp màn hình khung vẽ.")

SYSTEM = """Bạn là gia sư Xác suất thống kê đang trò chuyện trực tiếp với sinh viên.
Sinh viên có thể gửi ảnh bài viết tay, ghi âm hoặc chữ. Đọc kỹ chữ viết tay, nhận xét từng bước,
chỉ ra lỗi và hướng dẫn bước tiếp theo. Nhớ nội dung các lượt trước.
Trả về DUY NHẤT một JSON gồm hai khóa:
"chi_tiet": câu trả lời bằng markdown, dùng LaTeX $...$ cho công thức;
"loi_noi": bản rút gọn 2 đến 5 câu để ĐỌC TO, viết như đang nói chuyện,
tuyệt đối không dùng ký hiệu, markdown hay LaTeX, đọc công thức bằng lời
(ví dụ: xác suất của A bằng một phần sáu). Cuối câu có thể hỏi lại sinh viên một câu ngắn.
Tiếng Việt."""

if "dt" not in st.session_state:
    st.session_state.dt = {"msgs": [], "moi": False, "lan": 0}
dt = st.session_state.dt


def lam_sach(t):
    t = re.sub(r"[$*#`_]", "", t)
    t = t.replace("\\", " ")
    return re.sub(r"\s+", " ", t).strip()


def thanh_noi_dung(m):
    parts = []
    if m.get("anh"):
        parts.append(types.Part.from_bytes(data=m["anh"]["data"], mime_type=m["anh"]["type"]))
    if m.get("audio"):
        parts.append(types.Part.from_bytes(data=m["audio"], mime_type="audio/wav"))
    if m["content"]:
        parts.append(types.Part(text=m["content"]))
    elif m["role"] == "user" and not m.get("audio"):
        parts.append(types.Part(text="Hãy xem nội dung đính kèm và giúp mình."))
    if not parts:
        parts.append(types.Part(text="(trống)"))
    return types.Content(role="user" if m["role"] == "user" else "model", parts=parts)


c1, c2 = st.columns([3, 2])
with c1:
    anh = st.file_uploader(
        "Ảnh bài viết tay / hình vẽ (gửi kèm lượt nói tiếp theo)",
        type=["png", "jpg", "jpeg", "webp"],
        key=f"dt_anh_{dt['lan']}",
    )
with c2:
    tu_doc = st.checkbox("Tự động đọc to câu trả lời", value=True)
    if st.button("Cuộc trò chuyện mới"):
        st.session_state.dt = {"msgs": [], "moi": False, "lan": dt["lan"] + 1}
        st.rerun()

for m in dt["msgs"]:
    with st.chat_message(m["role"]):
        if m.get("anh"):
            st.image(m["anh"]["data"], width=300)
        if m.get("audio"):
            st.audio(m["audio"], format="audio/wav")
        if m["content"]:
            st.markdown(m["content"])

if dt["msgs"] and dt["msgs"][-1]["role"] == "assistant":
    tu_dong = dt["moi"] and tu_doc
    dt["moi"] = False
    loi_noi = dt["msgs"][-1].get("loi_noi") or lam_sach(dt["msgs"][-1]["content"])
    html = (
        DOC_TO.replace("__TEXT__", json.dumps(loi_noi).replace("</", "<\\/"))
        .replace("__AUTO__", "true" if tu_dong else "false")
    )
    components.html(html, height=60)
    st.caption("Nếu không nghe thấy tiếng, bấm nút Đọc to. Máy cần có giọng đọc tiếng Việt.")
elif not dt["msgs"]:
    st.info("Bấm micro ở khung bên dưới để nói, hoặc gõ câu hỏi. Có thể tải ảnh bài viết tay lên trước.")

prompt = st.chat_input("Bấm micro để nói, hoặc gõ câu hỏi...", accept_audio=True)
if prompt:
    audio = prompt.audio.getvalue() if prompt.audio else None
    tin = {
        "role": "user",
        "content": prompt.text or "",
        "audio": audio,
        "anh": {"data": anh.getvalue(), "type": anh.type} if anh else None,
    }
    if audio and len(audio) > 15 * 1024 * 1024:
        st.error("Ghi âm quá dài, hãy nói ngắn hơn.")
        st.stop()
    with st.spinner("AI đang nghe và suy nghĩ..."):
        raw = goi_ai([thanh_noi_dung(m) for m in dt["msgs"] + [tin]], SYSTEM, json_mode=True)
    kq = doc_json(raw)
    if not isinstance(kq, dict):
        kq = {"chi_tiet": raw, "loi_noi": lam_sach(raw)}
    if not dt["msgs"]:
        ghi_lich_su("Đối thoại giọng nói", "Bài viết tay")
    dt["msgs"].append(tin)
    dt["msgs"].append(
        {
            "role": "assistant",
            "content": kq.get("chi_tiet", ""),
            "loi_noi": kq.get("loi_noi", ""),
        }
    )
    dt["moi"] = True
    if anh:
        dt["lan"] += 1
    st.rerun()