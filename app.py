import streamlit as st
import pandas as pd
import random
from datetime import datetime

st.set_page_config(page_title="Facility Report", page_icon="🏢")

# เก็บข้อมูลชั่วคราว
if "reports" not in st.session_state:
    st.session_state.reports = []

# Sidebar
st.sidebar.title("🏢 Facility Report System")

menu = st.sidebar.radio(
    "Menu",
    ["แจ้งปัญหา", "ติดตามสถานะ", "Admin"]
)

# -----------------------------
# หน้าแจ้งปัญหา
# -----------------------------

if menu == "แจ้งปัญหา":

    st.title("📢 แจ้งปัญหาภายในอาคาร")

    name = st.text_input("ชื่อผู้แจ้ง")

    category = st.selectbox(
        "หมวดปัญหา",
        ["ลิฟต์", "ไฟฟ้า", "ห้องน้ำ", "ที่จอดรถ", "อื่นๆ"]
    )

    location = st.text_input("สถานที่")

    phone = st.text_input("เบอร์โทร")

    detail = st.text_area("รายละเอียดปัญหา")

    image = st.file_uploader("แนบรูปภาพ", type=["jpg","png","jpeg"])

    if st.button("แจ้งปัญหา"):

        report_id = "RP-" + str(random.randint(100000,999999))

        report = {
            "ID": report_id,
            "Name": name,
            "Category": category,
            "Location": location,
            "Phone": phone,
            "Detail": detail,
            "Status": "รอดำเนินการ",
            "Date": datetime.now().strftime("%d/%m/%Y")
        }

        st.session_state.reports.append(report)

        st.success("แจ้งปัญหาสำเร็จ")

        st.subheader("รหัสแจ้งปัญหา")

        st.code(report_id)

        st.info("สามารถคัดลอกรหัสนี้เพื่อติดตามสถานะ")

# -----------------------------
# ติดตามสถานะ
# -----------------------------

elif menu == "ติดตามสถานะ":

    st.title("🔍 ติดตามสถานะ")

    track_id = st.text_input("กรอกรหัสแจ้งปัญหา")

    if st.button("ตรวจสอบสถานะ"):

        found = False

        for r in st.session_state.reports:

            if r["ID"] == track_id:

                found = True

                st.success("พบข้อมูล")

                st.write("รหัสแจ้ง :", r["ID"])
                st.write("หมวด :", r["Category"])
                st.write("สถานที่ :", r["Location"])
                st.write("สถานะ :", r["Status"])
                st.write("วันที่แจ้ง :", r["Date"])
                st.write("รายละเอียด :", r["Detail"])

        if not found:
            st.error("ไม่พบรหัสแจ้งปัญหา")

# -----------------------------
# ADMIN
# -----------------------------

elif menu == "Admin":

    st.title("🔐 Admin Login")

    password = st.text_input("Password", type="password")

    if password == "adm123":

        st.success("เข้าสู่ระบบ Admin")

        df = pd.DataFrame(st.session_state.reports)

        st.subheader("📋 รายการแจ้งปัญหา")

        st.dataframe(df)

        if len(df) > 0:

            st.subheader("🔧 เปลี่ยนสถานะ")

            selected_id = st.selectbox(
                "เลือก ID",
                df["ID"]
            )

            new_status = st.selectbox(
                "สถานะ",
                ["รอดำเนินการ","กำลังดำเนินการ","เสร็จสิ้น"]
            )

            if st.button("อัปเดตสถานะ"):

                for r in st.session_state.reports:

                    if r["ID"] == selected_id:

                        r["Status"] = new_status

                st.success("อัปเดตสถานะแล้ว")

    elif password != "":
        st.error("รหัสผ่านไม่ถูกต้อง")
