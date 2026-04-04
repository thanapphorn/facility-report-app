import streamlit as st
import pandas as pd
import random
from datetime import datetime

st.set_page_config(page_title="Facility Report", page_icon="🔧", layout="wide")

# -----------------------
# CSS Dashboard
# -----------------------

st.markdown("""
<style>

.dashboard{
display:flex;
gap:20px;
margin-bottom:30px;
}

.card{
padding:20px;
border-radius:10px;
width:200px;
text-align:center;
color:white;
font-weight:bold;
}

.total{background:#6c757d;}
.wait{background:#f0ad4e;}
.process{background:#5bc0de;}
.done{background:#5cb85c;}

</style>
""", unsafe_allow_html=True)

# -----------------------
# MEMORY STORAGE
# -----------------------

if "reports" not in st.session_state:
    st.session_state.reports = []

# -----------------------
# HEADER
# -----------------------

st.title("🔧 ระบบรายงานปัญหา")

menu = st.radio(
    "",
    ["📝 ส่งรายงาน","📊 ติดตามสถานะ","🔐 Admin"],
    horizontal=True
)

# -----------------------
# PAGE 1 REPORT
# -----------------------

if menu == "📝 ส่งรายงาน":

    st.header("📢 แจ้งปัญหา")

    name = st.text_input("ชื่อผู้แจ้ง")
    phone = st.text_input("เบอร์โทร")

    category = st.selectbox(
        "หมวดปัญหา",
        [
            "ลิฟต์","ไฟฟ้า","ระบบแอร์","น้ำประปา",
            "ห้องน้ำ","ประตู/หน้าต่าง","ไฟส่องสว่าง",
            "กล้องวงจรปิด","อินเทอร์เน็ต","ที่จอดรถ",
            "ความสะอาด","อื่นๆ"
        ]
    )

    location = st.text_input("สถานที่")
    detail = st.text_area("รายละเอียดปัญหา")

    image = st.file_uploader("แนบรูปภาพ")

    confirm = st.checkbox("ยืนยันการแจ้งปัญหา")

    if st.button("ส่งรายงาน"):

        if not confirm:
            st.warning("กรุณายืนยันก่อนแจ้ง")
        else:

            report_id = "RP-" + str(random.randint(100000,999999))

            report = {
                "ID": report_id,
                "Name": name,
                "Phone": phone,
                "Category": category,
                "Location": location,
                "Detail": detail,
                "Status": "รอดำเนินการ",
                "Date": datetime.now().strftime("%d/%m/%Y"),
                "Time": datetime.now().strftime("%H:%M"),
                "Month": datetime.now().strftime("%B %Y"),
                "Image": "View Image"
            }

            st.session_state.reports.append(report)

            st.success("แจ้งปัญหาสำเร็จ")
            st.code(report_id)

# -----------------------
# PAGE 2 TRACK
# -----------------------

elif menu == "📊 ติดตามสถานะ":

    st.header("🔎 ติดตามสถานะ")

    track_id = st.text_input("กรอกรหัสแจ้ง")

    if st.button("ตรวจสอบ"):

        found = False

        for r in st.session_state.reports:

            if r["ID"] == track_id:

                found = True

                st.success("พบข้อมูล")

                st.write("ชื่อ:", r["Name"])
                st.write("หมวด:", r["Category"])
                st.write("สถานที่:", r["Location"])
                st.write("สถานะ:", r["Status"])
                st.write("วันที่:", r["Date"])
                st.write("เวลา:", r["Time"])

        if not found:
            st.error("ไม่พบข้อมูล")

# -----------------------
# PAGE 3 ADMIN
# -----------------------

elif menu == "🔐 Admin":

    st.header("🔐 Admin Login")

    password = st.text_input("รหัสผ่าน", type="password")

    if password != "ad123":
        st.warning("กรุณาใส่รหัสผ่าน")
        st.stop()

    st.success("เข้าสู่ระบบ Admin")

    df = pd.DataFrame(st.session_state.reports)

    if len(df) == 0:
        st.info("ยังไม่มีข้อมูล")
        st.stop()

    # -----------------------
    # DASHBOARD
    # -----------------------

    total = len(df)
    wait = len(df[df["Status"]=="รอดำเนินการ"])
    process = len(df[df["Status"]=="กำลังดำเนินการ"])
    done = len(df[df["Status"]=="เสร็จสิ้น"])

    st.markdown(f"""
    <div class="dashboard">

        <div class="card total">
        แจ้งทั้งหมด<br><h1>{total}</h1>
        </div>

        <div class="card wait">
        รอดำเนินการ<br><h1>{wait}</h1>
        </div>

        <div class="card process">
        กำลังดำเนินการ<br><h1>{process}</h1>
        </div>

        <div class="card done">
        เสร็จสิ้น<br><h1>{done}</h1>
        </div>

    </div>
    """, unsafe_allow_html=True)

    # -----------------------
    # FILTER
    # -----------------------

    col1,col2 = st.columns(2)

    with col1:
        search = st.text_input("🔎 Search ID")

    with col2:
        month = st.selectbox(
            "Sort by เดือน",
            ["ทั้งหมด"] + df["Month"].unique().tolist()
        )

    filtered = df.copy()

    if search:
        filtered = filtered[filtered["ID"].str.contains(search)]

    if month != "ทั้งหมด":
        filtered = filtered[filtered["Month"] == month]

    # -----------------------
    # TABLE
    # -----------------------

    st.subheader("📋 รายการแจ้งปัญหา")

    st.dataframe(
        filtered[
            [
                "ID","Name","Phone","Category",
                "Location","Date","Time","Status","Image"
            ]
        ],
        use_container_width=True
    )

    # -----------------------
    # UPDATE STATUS
    # -----------------------

    st.subheader("🔄 เปลี่ยนสถานะ")

    selected_id = st.selectbox("เลือก ID", df["ID"])

    new_status = st.selectbox(
        "สถานะ",
        ["รอดำเนินการ","กำลังดำเนินการ","เสร็จสิ้น"]
    )

    if st.button("Update"):

        for r in st.session_state.reports:

            if r["ID"] == selected_id:
                r["Status"] = new_status

        st.success("อัปเดตสถานะเรียบร้อย")
