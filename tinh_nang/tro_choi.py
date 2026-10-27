import random
from math import comb

import numpy as np
import pandas as pd
import streamlit as st
from tien_ich import ghi_lich_su

st.title("🎲 Trò chơi xác suất")
st.caption("Vừa chơi vừa học: đoán xác suất, thử thách Monty Hall và phòng thí nghiệm may rủi. Trang này không dùng AI nên chạy rất nhanh.")


def kich_ban():
    """Trả về (đề bài, xác suất đúng, lời giải, hàm mô phỏng một lần thử)."""
    loai = random.choice(
        ["tong2", "sau", "xu_dung", "xu_it_nhat", "bi_do", "bi_khac", "bai", "at", "sinh_nhat", "nhieu_lan"]
    )
    if loai == "tong2":
        k = random.randint(2, 12)
        cach = 6 - abs(k - 7)
        return (
            f"Tung 2 con xúc xắc cân đối. Xác suất để tổng hai mặt bằng **{k}**?",
            cach / 36,
            f"Không gian mẫu có 36 cặp đồng khả năng, trong đó {cach} cặp có tổng {k}. P = {cach}/36.",
            lambda: random.randint(1, 6) + random.randint(1, 6) == k,
        )
    if loai == "sau":
        n = random.choice([2, 3, 4])
        return (
            f"Tung **{n}** con xúc xắc cân đối. Xác suất để **ít nhất một** con ra mặt 6?",
            1 - (5 / 6) ** n,
            f"Dùng biến cố đối: không con nào ra 6 có xác suất (5/6)^{n}. P = 1 - (5/6)^{n}.",
            lambda: any(random.randint(1, 6) == 6 for _ in range(n)),
        )
    if loai == "xu_dung":
        n = random.randint(3, 8)
        k = random.randint(0, n)
        return (
            f"Tung **{n}** đồng xu cân đối. Xác suất để có **đúng {k}** mặt ngửa?",
            comb(n, k) / 2**n,
            f"Phân phối nhị thức: P = C({n},{k}) / 2^{n} = {comb(n, k)}/{2**n}.",
            lambda: sum(random.random() < 0.5 for _ in range(n)) == k,
        )
    if loai == "xu_it_nhat":
        n = random.randint(4, 8)
        k = random.randint(1, n)
        tong = sum(comb(n, i) for i in range(k, n + 1))
        return (
            f"Tung **{n}** đồng xu cân đối. Xác suất để có **ít nhất {k}** mặt ngửa?",
            tong / 2**n,
            f"Cộng các trường hợp từ {k} đến {n} mặt ngửa: ({tong}) / 2^{n}.",
            lambda: sum(random.random() < 0.5 for _ in range(n)) >= k,
        )
    if loai == "bi_do":
        r, b = random.randint(3, 7), random.randint(3, 7)
        return (
            f"Một túi có **{r} bi đỏ** và **{b} bi xanh**. Lấy ngẫu nhiên 2 bi (không hoàn lại). Xác suất cả hai đều đỏ?",
            comb(r, 2) / comb(r + b, 2),
            f"P = C({r},2) / C({r + b},2) = {comb(r, 2)}/{comb(r + b, 2)}.",
            lambda: all(x < r for x in random.sample(range(r + b), 2)),
        )
    if loai == "bi_khac":
        r, b = random.randint(3, 7), random.randint(3, 7)
        return (
            f"Một túi có **{r} bi đỏ** và **{b} bi xanh**. Lấy ngẫu nhiên 2 bi (không hoàn lại). Xác suất hai bi **khác màu**?",
            r * b / comb(r + b, 2),
            f"P = ({r} x {b}) / C({r + b},2) = {r * b}/{comb(r + b, 2)}.",
            lambda: len({x < r for x in random.sample(range(r + b), 2)}) == 2,
        )
    if loai == "bai":
        ten, dem = random.choice(
            [("lá **cơ**", 13), ("lá **hình** (J, Q, K)", 12), ("lá **át hoặc lá cơ**", 16), ("lá **đỏ**", 26)]
        )
        return (
            f"Rút ngẫu nhiên 1 lá từ bộ bài 52 lá. Xác suất rút được {ten}?",
            dem / 52,
            f"Có {dem} lá thỏa mãn trong 52 lá. P = {dem}/52.",
            lambda: random.randrange(52) < dem,
        )
    if loai == "at":
        return (
            "Rút ngẫu nhiên 2 lá (không hoàn lại) từ bộ bài 52 lá. Xác suất **cả hai đều là lá át**?",
            (4 / 52) * (3 / 51),
            "P = (4/52) x (3/51) = 1/221.",
            lambda: all(x < 4 for x in random.sample(range(52), 2)),
        )
    if loai == "sinh_nhat":
        n = random.choice([10, 15, 20, 23, 30, 40])
        kh = 1.0
        for i in range(n):
            kh *= (365 - i) / 365
        return (
            f"Trong một nhóm **{n} người**, xác suất để **ít nhất hai người trùng ngày sinh** (365 ngày, đồng khả năng)?",
            1 - kh,
            "Tính biến cố đối (không ai trùng): 365/365 x 364/365 x ... Kết quả thường lớn hơn trực giác nhiều.",
            lambda: len({random.randrange(365) for _ in range(n)}) < n,
        )
    p0 = random.choice([0.1, 0.2, 0.25, 0.3, 0.5])
    n = random.choice([3, 5, 8, 10])
    return (
        f"Mỗi lần thử thành công với xác suất **{p0}**, các lần độc lập. Thử **{n}** lần, xác suất có **ít nhất một** lần thành công?",
        1 - (1 - p0) ** n,
        f"P = 1 - (1 - {p0})^{n}.",
        lambda: any(random.random() < p0 for _ in range(n)),
    )


SO_VONG = 5


def xep_hang(tong):
    if tong >= 450:
        return "🏆 Nhà xác suất học"
    if tong >= 350:
        return "🎓 Giáo sư trẻ"
    if tong >= 250:
        return "📘 Sinh viên giỏi"
    if tong >= 150:
        return "🧪 Tân binh"
    return "🌱 Cần luyện thêm"


def van_moi():
    return {"vong": 0, "tong": 0, "kb": None, "xong": False, "kq": None, "da_ghi": False}


tab1, tab2, tab3 = st.tabs(["🎯 Đoán xác suất", "🚪 Monty Hall", "🧪 Phòng thí nghiệm"])

# ============================== TAB 1: ĐOÁN XÁC SUẤT ==============================
with tab1:
    if "gm" not in st.session_state:
        st.session_state.gm = van_moi()
    gm = st.session_state.gm

    if gm["vong"] >= SO_VONG and gm["xong"]:
        st.subheader("Kết thúc ván chơi")
        st.metric("Tổng điểm", f"{gm['tong']}/{SO_VONG * 100}")
        st.markdown(f"### Xếp hạng: {xep_hang(gm['tong'])}")
        if not gm["da_ghi"]:
            ghi_lich_su("Trò chơi", "Đoán xác suất", round(gm["tong"] / (SO_VONG * 10), 1))
            gm["da_ghi"] = True
            st.balloons()
        if st.button("Chơi lại", key="choi_lai_gm"):
            st.session_state.gm = van_moi()
            st.rerun()
    else:
        if gm["kb"] is None:
            gm["kb"] = kich_ban()
        de, p, giai, thu = gm["kb"]
        st.progress(gm["vong"] / SO_VONG, text=f"Vòng {gm['vong'] + 1}/{SO_VONG}  ·  Điểm hiện tại: {gm['tong']}")
        st.markdown(de)
        if gm["kq"] is None:
            doan = st.slider("Bạn đoán xác suất là bao nhiêu (%)?", 0, 100, 50, key=f"doan_{gm['vong']}")
            if st.button("Chốt đáp án", type="primary", key=f"chot_{gm['vong']}"):
                sai = abs(doan - p * 100)
                diem = max(0, round(100 - 4 * sai))
                n = 3000
                tan_suat = sum(thu() for _ in range(n)) / n
                gm["kq"] = {"doan": doan, "sai": sai, "diem": diem, "tan_suat": tan_suat, "n": n}
                gm["tong"] += diem
                st.rerun()
        else:
            kq = gm["kq"]
            c1, c2, c3 = st.columns(3)
            c1.metric("Đáp án đúng", f"{p * 100:.1f}%")
            c2.metric("Bạn đoán", f"{kq['doan']}%", f"sai lệch {kq['sai']:.1f}", delta_color="off")
            c3.metric("Điểm vòng này", f"{kq['diem']}/100")
            st.info("**Lời giải:** " + giai)
            st.caption(f"Mô phỏng máy tính ({kq['n']} lần thử): {kq['tan_suat'] * 100:.1f}%, gần với đáp án lý thuyết.")
            nhan = "Xem kết quả →" if gm["vong"] + 1 >= SO_VONG else "Vòng tiếp theo →"
            if st.button(nhan, type="primary", key=f"tiep_{gm['vong']}"):
                gm["vong"] += 1
                gm["kb"] = None
                gm["kq"] = None
                if gm["vong"] >= SO_VONG:
                    gm["xong"] = True
                st.rerun()

# ================================ TAB 2: MONTY HALL ================================
with tab2:
    st.markdown(
        "Có 3 cánh cửa: sau một cửa là **xe hơi 🚗**, sau hai cửa còn lại là **dê 🐐**. "
        "Bạn chọn một cửa. Người dẫn chương trình (biết rõ cửa nào có xe) mở một cửa **có dê** trong hai cửa còn lại, "
        "rồi hỏi bạn: **giữ nguyên** hay **đổi** sang cửa kia?"
    )
    if "mh" not in st.session_state:
        st.session_state.mh = {"buoc": 0, "xe": 0, "chon": 0, "mo": 0, "cuoi": 0, "thang": False,
                               "giu": [0, 0], "doi": [0, 0]}
    mh = st.session_state.mh

    def hien_cua(mo_het=False):
        cot = st.columns(3)
        for i in range(3):
            if mo_het:
                bieu_tuong = "🚗" if i == mh["xe"] else "🐐"
            elif i == mh["mo"] and mh["buoc"] >= 1:
                bieu_tuong = "🐐"
            else:
                bieu_tuong = "🚪"
            nhan = f"Cửa {i + 1}" + (" (bạn chọn)" if i == mh["chon"] and mh["buoc"] >= 1 else "")
            cot[i].markdown(f"<div style='text-align:center;font-size:3rem'>{bieu_tuong}</div>"
                            f"<div style='text-align:center'>{nhan}</div>", unsafe_allow_html=True)

    if mh["buoc"] == 0:
        st.markdown("**Bước 1:** chọn một cửa")
        cot = st.columns(3)
        for i in range(3):
            if cot[i].button(f"🚪 Cửa {i + 1}", key=f"cua_{i}", use_container_width=True):
                mh["xe"] = random.randrange(3)
                mh["chon"] = i
                mh["mo"] = random.choice([d for d in range(3) if d != i and d != mh["xe"]])
                mh["buoc"] = 1
                st.rerun()
    elif mh["buoc"] == 1:
        hien_cua()
        con_lai = next(d for d in range(3) if d != mh["chon"] and d != mh["mo"])
        st.markdown(f"Người dẫn chương trình đã mở **cửa {mh['mo'] + 1}**: có dê 🐐. Bạn muốn làm gì?")
        c1, c2 = st.columns(2)
        if c1.button(f"Giữ cửa {mh['chon'] + 1}", use_container_width=True):
            mh["cuoi"] = mh["chon"]
            mh["thang"] = mh["cuoi"] == mh["xe"]
            mh["giu"][1] += 1
            mh["giu"][0] += int(mh["thang"])
            mh["kieu"] = "giữ"
            mh["buoc"] = 2
            st.rerun()
        if c2.button(f"Đổi sang cửa {con_lai + 1}", use_container_width=True):
            mh["cuoi"] = con_lai
            mh["thang"] = mh["cuoi"] == mh["xe"]
            mh["doi"][1] += 1
            mh["doi"][0] += int(mh["thang"])
            mh["kieu"] = "đổi"
            mh["buoc"] = 2
            st.rerun()
    else:
        hien_cua(mo_het=True)
        if mh["thang"]:
            st.success(f"Bạn chọn **{mh['kieu']}** cửa và **thắng xe** 🚗!")
        else:
            st.error(f"Bạn chọn **{mh['kieu']}** cửa và gặp dê 🐐.")
        if st.button("Chơi ván mới", type="primary"):
            mh["buoc"] = 0
            st.rerun()

    st.divider()
    g, d = mh["giu"], mh["doi"]
    c1, c2 = st.columns(2)
    c1.metric("Giữ cửa: số ván thắng", f"{g[0]}/{g[1]}", f"{(g[0] / g[1] * 100 if g[1] else 0):.0f}%", delta_color="off")
    c2.metric("Đổi cửa: số ván thắng", f"{d[0]}/{d[1]}", f"{(d[0] / d[1] * 100 if d[1] else 0):.0f}%", delta_color="off")

    if st.button("Mô phỏng 10.000 ván cho cả hai chiến thuật"):
        n = 10000
        thang_giu = thang_doi = 0
        for _ in range(n):
            xe, chon = random.randrange(3), random.randrange(3)
            mo = random.choice([x for x in range(3) if x != chon and x != xe])
            doi = next(x for x in range(3) if x != chon and x != mo)
            thang_giu += chon == xe
            thang_doi += doi == xe
        a, b = st.columns(2)
        a.metric("Luôn giữ cửa", f"{thang_giu / n * 100:.1f}%")
        b.metric("Luôn đổi cửa", f"{thang_doi / n * 100:.1f}%")
        st.info(
            "Giữ cửa thắng khoảng **1/3**, đổi cửa thắng khoảng **2/3**. "
            "Lý do: lúc đầu bạn chọn đúng xe với xác suất 1/3. Nếu chọn sai (xác suất 2/3), "
            "người dẫn chương trình buộc phải mở cửa dê còn lại, nên cửa kia chắc chắn là xe."
        )

# ============================ TAB 3: PHÒNG THÍ NGHIỆM ============================
with tab3:
    st.markdown("Chạy thí nghiệm nhiều lần để thấy **tần suất tiến gần xác suất lý thuyết** khi số lần thử tăng (luật số lớn).")
    thi_nghiem = st.selectbox(
        "Chọn thí nghiệm",
        ["Tung đồng xu: xác suất mặt ngửa", "Tung xúc xắc: xác suất ra mặt 6", "Tung 2 xúc xắc: xác suất tổng bằng 7"],
    )
    so_lan = st.select_slider("Số lần thử", options=[10, 50, 100, 500, 1000, 5000, 20000], value=1000)
    if st.button("Chạy thí nghiệm", type="primary"):
        rng = np.random.default_rng()
        if thi_nghiem.startswith("Tung đồng xu"):
            p_lt = 0.5
            kq = rng.random(so_lan) < 0.5
        elif thi_nghiem.startswith("Tung xúc xắc"):
            p_lt = 1 / 6
            kq = rng.integers(1, 7, so_lan) == 6
        else:
            p_lt = 6 / 36
            kq = (rng.integers(1, 7, so_lan) + rng.integers(1, 7, so_lan)) == 7
        luy_ke = np.cumsum(kq) / np.arange(1, so_lan + 1)
        buoc = max(1, so_lan // 400)
        chi_so = np.arange(0, so_lan, buoc)
        df = pd.DataFrame(
            {"Tần suất thực nghiệm": luy_ke[chi_so], "Xác suất lý thuyết": p_lt},
            index=chi_so + 1,
        )
        df.index.name = "Số lần thử"
        st.session_state.lab = {"df": df, "p": p_lt, "tan_suat": float(luy_ke[-1]), "n": so_lan}
    lab = st.session_state.get("lab")
    if lab:
        c1, c2, c3 = st.columns(3)
        c1.metric("Số lần thử", f"{lab['n']:,}")
        c2.metric("Tần suất thực nghiệm", f"{lab['tan_suat'] * 100:.2f}%")
        c3.metric("Xác suất lý thuyết", f"{lab['p'] * 100:.2f}%")
        st.line_chart(lab["df"])
        st.caption("Thử chạy với 10 lần rồi 20.000 lần: đường thực nghiệm dao động mạnh lúc đầu và dần bám sát đường lý thuyết.")