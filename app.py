import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import uuid

# =========================
# CONNECT GOOGLE SHEET
# =========================

scope = [
"https://spreadsheets.google.com/feeds",
"https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
"credentials.json", scope
)

client = gspread.authorize(creds)

sheet = client.open("facility-report").sheet1


st.set_page_config(page_title="ระบบแจ้งปัญหา")

menu = st.sidebar.selectbox(
"เมนู",
["แจ้งปัญหา","ติดตามงาน","Admin"]
)

# =========================
# PAGE 1 : REPORT
# =========================

if menu == "แจ้งปัญหา":

    st.title("📝 แจ้งปัญหา")

    category = st.selectbox(
    "หมวดหมู่ปัญหา",
    ["ไฟฟ้า","ประปา","ห้องน้ำ","แอร์","เฟอร์นิเจอร์","อื่นๆ"]
    )

    name = st.text_input("ชื่อ")
    phone = st.text_input("เบอร์โทร")
    location = st.text_input("สถานที่")
    description = st.text_area("รายละเอียด")

    image = st.file_uploader("📸 แนบรูป",type=["jpg","png","jpeg"])

    if st.button("ส่งรายงาน"):

        ticket = "RTP-" + str(uuid.uuid4())[:6]

        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M")

        sheet.append_row([
        ticket,
        category,
        name,
        phone,
        location,
        description,
        "",
        "pending",
        date,
        time
        ])

        st.success(f"ส่งสำเร็จ Ticket: {ticket}")

# =========================
# PAGE 2 : TRACK
# =========================

elif menu == "ติดตามงาน":

    st.title("🔍 ติดตามงาน")

    ticket = st.text_input("กรอกรหัส Ticket")

    data = sheet.get_all_records()

    df = pd.DataFrame(data)

    result = df[df["ticket"] == ticket]

    if len(result)>0:

        st.subheader("สถานะงาน")

        st.write(result)

    elif ticket != "":
        st.warning("ไม่พบ Ticket")

# =========================
# PAGE 3 : ADMIN
# =========================

elif menu == "Admin":

    st.title("🔐 Admin")

    password = st.text_input("รหัสผ่าน",type="password")

    if password == "admin123":

        data = sheet.get_all_records()

        df = pd.DataFrame(data)

        for i,row in df.iterrows():

            st.subheader(row["ticket"])

            st.write("หมวดหมู่:",row["category"])
            st.write("สถานที่:",row["location"])
            st.write("รายละเอียด:",row["description"])
            st.write("วันที่:",row["date"],"เวลา:",row["time"])

            status = st.selectbox(
            "สถานะ",
            ["pending","in progress","done"],
            index=["pending","in progress","done"].index(row["status"]),
            key=i
            )

            if st.button("บันทึกสถานะ",key=f"btn{i}"):

                sheet.update_cell(i+2,8,status)

                st.success("อัปเดตแล้ว")
