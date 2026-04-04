import streamlit as st
import pandas as pd
import random
from datetime import datetime

st.set_page_config(page_title="Facility Report", page_icon="🏢", layout="wide")

# ---------------------------
# CSS Dashboard สี
# ---------------------------

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

# ---------------------------
# Memory storage
# ---------------------------

if "reports" not in st.session_state:
    st.session_state.reports = []

# ---------------------------
# Sidebar
# ---------------------------

st.sidebar.title("🏢 Facility System")

menu = st.sidebar.radio(
    "Menu",
    ["แจ้งปัญหา", "ติดตามสถานะ", "Admin"]
)

# ---------------------------
# PAGE 1 REPORT ISSUE
# ---------------------------

if menu == "แจ้งปัญหา":

    st.title("📢 แจ้งปัญหาภายในอาคาร")

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

    image = st.file_uploader("แนบรูป", type=["jpg","png","jpeg"])

    confirm = st.checkbox("ยืนยันการแจ้งปัญหา")

    if st.button("แจ้งปัญหา"):

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
                "Image": image
            }

            st.session_state.reports.append(report)

            st.success("แจ้งปัญหาสำเร็จ")
            st.code(report_id)

# ---------------------------
# PAGE 2 TRACK STATUS
# ---------------------------

elif menu == "ติดตามสถานะ":

    st.title("🔍 ติดตามสถานะ")

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
                st.write("วันที่:", r["Date"])
                st.write("เวลา:", r["Time"])
                st.write("สถานะ:", r["Status"])

                if r["Image"]:
                    st.image(r["Image"], width=300)

        if not found:
            st.error("ไม่พบข้อมูล")

# ---------------------------
# PAGE 3 ADMIN
# ---------------------------

elif menu == "Admin":

    st.title("📊 Admin Dashboard")

    df = pd.DataFrame(st.session_state.reports)

    if len(df) == 0:
        st.info("ยังไม่มีข้อมูล")
        st.stop()

    # -----------------------
    # Dashboard statistics
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
    # Filters
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
    # Table
    # -----------------------

    st.subheader("📋 รายการแจ้งปัญหา")

    for i,row in filtered.iterrows():

        col1,col2,col3,col4,col5,col6,col7,col8 = st.columns([1,1,1,1,1,1,1,1])

        col1.write(row["ID"])
        col2.write(row["Name"])
        col3.write(row["Phone"])
        col4.write(row["Category"])
        col5.write(row["Location"])
        col6.write(row["Date"] + " " + row["Time"])

        new_status = col7.selectbox(
            "Status",
            ["รอดำเนินการ","กำลังดำเนินการ","เสร็จสิ้น"],
            index=["รอดำเนินการ","กำลังดำเนินการ","เสร็จสิ้น"].index(row["Status"]),
            key=row["ID"]
        )

        if new_status != row["Status"]:
            st.session_state.reports[i]["Status"] = new_status

        if row["Image"]:
            col8.image(row["Image"], width=80)
        else:
            col8.write("-")
