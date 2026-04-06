import streamlit as st
import pandas as pd
import random
from datetime import datetime
import base64

st.set_page_config(page_title="Facility Report", page_icon="🏢", layout="wide")

# -----------------------
# Global CSS
# -----------------------
st.markdown("""
<style>
/* ── Dashboard cards ── */
.dashboard {
    display: flex;
    gap: 16px;
    margin: 16px 0 28px 0;
}
.card {
    flex: 1;
    border-radius: 14px;
    padding: 20px 24px;
    text-align: center;
    font-size: 15px;
    font-weight: 600;
    color: #fff;
    box-shadow: 0 2px 8px rgba(0,0,0,0.10);
}
.card h1 { margin: 8px 0 0 0; font-size: 2.6rem; font-weight: 800; }
.total   { background: linear-gradient(135deg,#4F8EF7,#3a6fd8); }
.wait    { background: linear-gradient(135deg,#f5a623,#e08c0a); }
.process { background: linear-gradient(135deg,#7B61FF,#5a3fd4); }
.done    { background: linear-gradient(135deg,#34C37A,#1fa05a); }

/* ── Status badges ── */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    white-space: nowrap;
}
.badge-wait    { background:#FFF3CD; color:#856404; }
.badge-process { background:#EDE7FF; color:#5a3fd4; }
.badge-done    { background:#D1F8E6; color:#1a7a46; }

/* ── Info card (track page) ── */
.info-card {
    background: #f8f9fb;
    border: 1px solid #e2e6ea;
    border-radius: 14px;
    padding: 24px 28px;
    margin-top: 16px;
}
.info-card .row {
    display: flex;
    padding: 8px 0;
    border-bottom: 1px solid #eee;
    font-size: 15px;
}
.info-card .row:last-child { border-bottom: none; }
.info-card .label {
    min-width: 130px;
    color: #888;
    font-weight: 600;
}
.info-card .value { color: #222; }

/* ── Report ID success box ── */
.id-box {
    background: #E8F5E9;
    border: 1.5px solid #66BB6A;
    border-radius: 12px;
    padding: 18px 24px;
    margin-top: 12px;
    text-align: center;
}
.id-box .id-label { color: #2e7d32; font-size: 14px; margin-bottom: 6px; }
.id-box .id-code  {
    font-size: 2rem;
    font-weight: 800;
    color: #1b5e20;
    letter-spacing: 3px;
    font-family: monospace;
}
.id-box .id-hint  { color: #555; font-size: 13px; margin-top: 8px; }

/* ── Styled table ── */
.styled-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    margin-top: 8px;
}
.styled-table th {
    background: #4F8EF7;
    color: white;
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
}
.styled-table td {
    padding: 9px 12px;
    border-bottom: 1px solid #eee;
    vertical-align: middle;
}
.styled-table tr:hover td { background: #f5f8ff; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# Initialize session_state
# -----------------------
if "reports" not in st.session_state:
    st.session_state.reports = []
if "page" not in st.session_state:
    st.session_state.page = 1

# -----------------------
# Helper: status badge HTML
# -----------------------
def status_badge(status):
    cls = {"รอดำเนินการ": "badge-wait",
           "กำลังดำเนินการ": "badge-process",
           "เสร็จสิ้น": "badge-done"}.get(status, "badge-wait")
    return f'<span class="badge {cls}">{status}</span>'

# -----------------------
# Menu
# -----------------------
st.title("🏢 ระบบแจ้งปัญหาภายในอาคาร")
menu = st.radio("", ["📢 แจ้งปัญหา", "🔎 ติดตามสถานะ", "🔐 Admin"], horizontal=True)

# =============================================================
# PAGE 1 : REPORT
# =============================================================
if menu == "📢 แจ้งปัญหา":
    st.header("📢 แจ้งปัญหา")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("ชื่อผู้แจ้ง *")
    with col2:
        phone = st.text_input("เบอร์โทร *")

    category = st.selectbox(
        "หมวดปัญหา",
        ["ลิฟต์", "ไฟฟ้า", "ระบบแอร์", "น้ำประปา",
         "ห้องน้ำ", "ประตู/หน้าต่าง", "ไฟส่องสว่าง",
         "กล้องวงจรปิด", "อินเทอร์เน็ต", "ที่จอดรถ",
         "ความสะอาด", "อื่นๆ"]
    )
    location = st.text_input("สถานที่ *")
    detail   = st.text_area("รายละเอียดปัญหา")
    image    = st.file_uploader("📸 อัปโหลดรูปภาพ (ไม่บังคับ)", type=["jpg", "jpeg", "png", "gif"])
    confirm  = st.checkbox("ยืนยันการแจ้งปัญหา")

    if st.button("ส่งรายงาน", type="primary"):
        # ── Validation ──
        errors = []
        if not name.strip():    errors.append("ชื่อผู้แจ้ง")
        if not phone.strip():   errors.append("เบอร์โทร")
        if not location.strip(): errors.append("สถานที่")
        if not confirm:          errors.append("การยืนยัน")

        if errors:
            st.error(f"กรุณากรอกข้อมูลให้ครบ: {', '.join(errors)}")
        else:
            report_id  = "RP-" + str(random.randint(100000, 999999))
            image_data = None
            if image is not None:
                image_data = base64.b64encode(image.read()).decode()

            report = {
                "ID": report_id, "Name": name.strip(), "Phone": phone.strip(),
                "Category": category, "Location": location.strip(),
                "Detail": detail, "Status": "รอดำเนินการ",
                "Date": datetime.now().strftime("%d/%m/%Y"),
                "Time": datetime.now().strftime("%H:%M"),
                "Month": datetime.now().strftime("%B %Y"),
                "Image": image_data, "ImageName": image.name if image else None
            }
            st.session_state.reports.append(report)

            st.success("✅ แจ้งปัญหาสำเร็จแล้ว!")
            st.markdown(f"""
            <div class="id-box">
                <div class="id-label">📋 รหัสการแจ้งปัญหาของคุณ</div>
                <div class="id-code">{report_id}</div>
                <div class="id-hint">กรุณาจดรหัสนี้ไว้เพื่อติดตามสถานะในภายหลัง</div>
            </div>
            """, unsafe_allow_html=True)

# =============================================================
# PAGE 2 : TRACK
# =============================================================
elif menu == "🔎 ติดตามสถานะ":
    st.header("🔎 ติดตามสถานะ")

    col1, col2 = st.columns([3, 1])
    with col1:
        track_id = st.text_input("กรอกรหัสแจ้ง (เช่น RP-123456)", label_visibility="collapsed",
                                  placeholder="RP-XXXXXX")
    with col2:
        check = st.button("ตรวจสอบ", type="primary", use_container_width=True)

    if check:
        found = False
        for r in st.session_state.reports:
            if r["ID"] == track_id.strip():
                found = True
                badge_html = status_badge(r["Status"])
                st.markdown(f"""
                <div class="info-card">
                    <div class="row"><span class="label">🔖 รหัสแจ้ง</span>
                        <span class="value"><b>{r["ID"]}</b></span></div>
                    <div class="row"><span class="label">👤 ชื่อผู้แจ้ง</span>
                        <span class="value">{r["Name"]}</span></div>
                    <div class="row"><span class="label">📂 หมวดปัญหา</span>
                        <span class="value">{r["Category"]}</span></div>
                    <div class="row"><span class="label">📍 สถานที่</span>
                        <span class="value">{r["Location"]}</span></div>
                    <div class="row"><span class="label">🗒️ รายละเอียด</span>
                        <span class="value">{r["Detail"] or "-"}</span></div>
                    <div class="row"><span class="label">📅 วันที่/เวลา</span>
                        <span class="value">{r["Date"]} เวลา {r["Time"]} น.</span></div>
                    <div class="row"><span class="label">📌 สถานะ</span>
                        <span class="value">{badge_html}</span></div>
                </div>
                """, unsafe_allow_html=True)

                if r["Image"]:
                    st.image(base64.b64decode(r["Image"]),
                             caption=r["ImageName"], width=340)
                break

        if not found:
            st.error("❌ ไม่พบข้อมูล กรุณาตรวจสอบรหัสอีกครั้ง")

# =============================================================
# PAGE 3 : ADMIN
# =============================================================
elif menu == "🔐 Admin":
    st.header("🔐 Admin Login")
    password = st.text_input("รหัสผ่าน", type="password")
    if password != "ad123":
        st.warning("กรุณาใส่รหัสผ่าน")
        st.stop()

    st.success("✅ เข้าสู่ระบบ Admin")
    df = pd.DataFrame(st.session_state.reports)

    if len(df) == 0:
        st.info("ยังไม่มีข้อมูลในระบบ")
        st.stop()

    # ── Dashboard ──────────────────────────────────────────
    total   = len(df)
    wait    = len(df[df["Status"] == "รอดำเนินการ"])
    process = len(df[df["Status"] == "กำลังดำเนินการ"])
    done    = len(df[df["Status"] == "เสร็จสิ้น"])

    st.markdown(f"""
    <div class="dashboard">
        <div class="card total">  แจ้งทั้งหมด<br><h1>{total}</h1></div>
        <div class="card wait">   รอดำเนินการ<br><h1>{wait}</h1></div>
        <div class="card process">กำลังดำเนินการ<br><h1>{process}</h1></div>
        <div class="card done">   เสร็จสิ้น<br><h1>{done}</h1></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Filter ─────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        search = st.text_input("🔎 ค้นหา ID", placeholder="RP-XXXXXX")
    with col2:
        month = st.selectbox("📅 Filter เดือน",
                             ["ทั้งหมด"] + df["Month"].unique().tolist())
    with col3:
        status_filter = st.selectbox("📌 สถานะ",
                                     ["ทั้งหมด", "รอดำเนินการ",
                                      "กำลังดำเนินการ", "เสร็จสิ้น"])

    filtered = df.copy()
    if search:
        filtered = filtered[filtered["ID"].str.contains(search, case=False)]
    if month != "ทั้งหมด":
        filtered = filtered[filtered["Month"] == month]
    if status_filter != "ทั้งหมด":
        filtered = filtered[filtered["Status"] == status_filter]

    # ── Pagination ─────────────────────────────────────────
    rows_per_page = 10
    total_rows    = len(filtered)

    if total_rows == 0:
        st.info("ไม่พบข้อมูลที่ตรงกับเงื่อนไข")
    else:
        total_pages = max(1, (total_rows - 1) // rows_per_page + 1)
        if st.session_state.page > total_pages:
            st.session_state.page = 1

        col_prev, col_info, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("◀  Previous",
                         disabled=st.session_state.page <= 1,
                         use_container_width=True):
                st.session_state.page -= 1
                st.rerun()
        with col_info:
            st.markdown(
                f"<div style='text-align:center;padding:8px 0;color:#555;font-size:15px;'>"
                f"หน้า <b>{st.session_state.page}</b> / <b>{total_pages}</b> "
                f"<span style='color:#aaa;font-size:13px;'>({total_rows} รายการ)</span></div>",
                unsafe_allow_html=True)
        with col_next:
            if st.button("Next  ▶",
                         disabled=st.session_state.page >= total_pages,
                         use_container_width=True):
                st.session_state.page += 1
                st.rerun()

        start     = (st.session_state.page - 1) * rows_per_page
        page_data = filtered.iloc[start: start + rows_per_page].copy()

        # ── Styled table with badge ─────────────────────────
        page_data["สถานะ"]  = page_data["Status"].apply(status_badge)
        page_data["รูปภาพ"] = page_data["ImageName"].apply(
            lambda x: f"<span style='color:#2e7d32'>✓ {x}</span>" if x else "<span style='color:#aaa'>-</span>"
        )

        html_rows = ""
        for _, row in page_data.iterrows():
            html_rows += f"""
            <tr>
                <td><b>{row["ID"]}</b></td>
                <td>{row["Name"]}</td>
                <td>{row["Phone"]}</td>
                <td>{row["Category"]}</td>
                <td>{row["Location"]}</td>
                <td>{row["Date"]}</td>
                <td>{row["Time"]}</td>
                <td>{row["สถานะ"]}</td>
                <td>{row["รูปภาพ"]}</td>
            </tr>"""

        st.markdown(f"""
        <table class="styled-table">
            <tr>
                <th>ID</th><th>ชื่อ</th><th>เบอร์</th><th>หมวด</th>
                <th>สถานที่</th><th>วันที่</th><th>เวลา</th><th>สถานะ</th><th>รูปภาพ</th>
            </tr>
            {html_rows}
        </table>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Update Status ───────────────────────────────────────
    st.subheader("🔄 เปลี่ยนสถานะ")
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        selected_id = st.selectbox("เลือก ID", df["ID"])
    with col2:
        # แสดงสถานะปัจจุบันใน dropdown
        current_statuses = ["รอดำเนินการ", "กำลังดำเนินการ", "เสร็จสิ้น"]
        cur_status = next(
            (r["Status"] for r in st.session_state.reports if r["ID"] == selected_id),
            "รอดำเนินการ"
        )
        new_status = st.selectbox("สถานะใหม่", current_statuses,
                                   index=current_statuses.index(cur_status))
    with col3:
        st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
        if st.button("💾 Update", type="primary", use_container_width=True):
            for r in st.session_state.reports:
                if r["ID"] == selected_id:
                    r["Status"] = new_status
            st.success(f"✅ อัปเดต {selected_id} → {new_status}")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ── View Report Detail ──────────────────────────────────
    st.subheader("📋 ดูรายละเอียดรายงาน")
    view_id = st.selectbox("เลือก ID เพื่อดูรายละเอียด", df["ID"])
    if st.button("แสดงรายละเอียด"):
        for r in st.session_state.reports:
            if r["ID"] == view_id:
                badge_html = status_badge(r["Status"])
                st.markdown(f"""
                <div class="info-card">
                    <div class="row"><span class="label">🔖 รหัสแจ้ง</span>
                        <span class="value"><b>{r["ID"]}</b></span></div>
                    <div class="row"><span class="label">👤 ชื่อผู้แจ้ง</span>
                        <span class="value">{r["Name"]}</span></div>
                    <div class="row"><span class="label">📞 เบอร์โทร</span>
                        <span class="value">{r["Phone"]}</span></div>
                    <div class="row"><span class="label">📂 หมวดปัญหา</span>
                        <span class="value">{r["Category"]}</span></div>
                    <div class="row"><span class="label">📍 สถานที่</span>
                        <span class="value">{r["Location"]}</span></div>
                    <div class="row"><span class="label">🗒️ รายละเอียด</span>
                        <span class="value">{r["Detail"] or "-"}</span></div>
                    <div class="row"><span class="label">📅 วันที่/เวลา</span>
                        <span class="value">{r["Date"]} เวลา {r["Time"]} น.</span></div>
                    <div class="row"><span class="label">📌 สถานะ</span>
                        <span class="value">{badge_html}</span></div>
                </div>
                """, unsafe_allow_html=True)

                if r["Image"]:
                    st.image(base64.b64decode(r["Image"]),
                             caption=r["ImageName"], width=420)
                else:
                    st.info("ไม่มีรูปภาพ")
