import streamlit as st
import streamlit.components.v1 as components
from google.genai import types
from tien_ich import goi_ai, ghi_lich_su

st.title("🖊️ Bảng vẽ và giọng nói")
st.caption("Viết tay bài giải (bằng bút trên iPad hoặc chuột), lưu ảnh rồi hỏi AI bằng giọng nói hoặc chữ.")

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

components.html(BANG_VE, height=520)
st.info("Bấm **Lưu ảnh** (ảnh nằm trong thư mục Tải xuống), rồi tải ảnh lên ở phần bên dưới. Nếu nút lưu không hoạt động, hãy chụp màn hình khung vẽ.")

anh = st.file_uploader("Tải ảnh bài viết tay / hình vẽ", type=["png", "jpg", "jpeg", "webp"])
giong = st.audio_input("Hỏi bằng giọng nói (không bắt buộc)")
chu = st.text_area("Hoặc gõ câu hỏi", placeholder="Ví dụ: Bước 3 của mình có đúng không?")

SYSTEM = """Bạn là gia sư Xác suất thống kê. Sinh viên gửi ảnh bài viết tay hoặc hình vẽ,
có thể kèm câu hỏi bằng giọng nói hoặc chữ. Đọc kỹ chữ viết tay, nhận xét từng bước,
chỉ ra lỗi và hướng dẫn bước tiếp theo. Tiếng Việt, LaTeX $...$."""

if st.button("Hỏi AI", type="primary"):
    if not (anh or giong or chu.strip()):
        st.warning("Hãy tải ảnh, ghi âm hoặc gõ câu hỏi.")
        st.stop()
    parts = []
    if anh:
        parts.append(types.Part.from_bytes(data=anh.getvalue(), mime_type=anh.type))
    if giong:
        parts.append(types.Part.from_bytes(data=giong.getvalue(), mime_type="audio/wav"))
    parts.append(types.Part(text=chu.strip() or "Hãy xem nội dung đính kèm và giúp mình."))
    with st.spinner("AI đang xem bài của bạn..."):
        st.markdown(goi_ai(parts, SYSTEM))
    ghi_lich_su("Bảng vẽ và giọng nói", "Bài viết tay")