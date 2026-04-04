import streamlit as st
import gspread
import pandas as pd
import io
import uuid
import smtplib

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime
from email.mime.text import MIMEText

# -----------------------
# CONFIG
# -----------------------

ADMIN_PASSWORD = "1234"

EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"
EMAIL_RECEIVER = "your_email@gmail.com"

FOLDER_ID = "YOUR_DRIVE_FOLDER_ID"

# -----------------------
# GOOGLE API CONNECT
# -----------------------

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

gc = gspread.authorize(creds)

sheet = gc.open("building_report").sheet1

drive_service = build("drive", "v3", credentials=creds)

# -----------------------
# EMAIL FUNCTION
# -----------------------

def send_email(name, location, problem):

    msg = MIMEText(f"""
มีการแจ้งปัญหาใหม่

ผู้แจ้ง: {name}
สถานที่: {location}
รายละเอียด: {problem}

กรุณาเข้าระบบเพื่อตรวจสอบ
""")

    msg["Subject"] = "แจ้งปัญหาใหม่ในระบบ"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

# -----------------------
# PAGE TITLE
# -----------------------

st.title("🏢 ระบบแจ้งปัญหาภายในอาคาร")

menu = st.sidebar.selectbox(
    "เมนู",
    ["แจ้งปัญหา", "Admin"]
)

# -----------------------
# PAGE 1 REPORT
# -----------------------

if menu == "แจ้งปัญหา":

    st.header("แจ้งปัญหา")

    name = st.text_input("ชื่อผู้แจ้ง")

    location = st.selectbox(
        "สถานที่",
        ["ลิฟต์","ห้องน้ำ","ที่จอดรถ","ไฟฟ้า","อื่นๆ"]
    )

    problem = st.text_area("รายละเอียดปัญหา")

    report_time = st.time_input("เวลาแจ้ง")

    image = st.file_uploader("แนบรูปภาพ", type=["jpg","png","jpeg"])

    if st.button("แจ้งปัญหา"):

        image_url = ""

        if image is not None:

            file_id = str(uuid.uuid4())

            file_metadata = {
                "name": file_id + ".jpg",
                "parents": [FOLDER_ID]
            }

            media = MediaIoBaseUpload(
                io.BytesIO(image.read()),
                mimetype="image/jpeg"
            )

            uploaded = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id"
            ).execute()

            image_url = f"https://drive.google.com/file/d/{uploaded['id']}/view"

        sheet.append_row([
            str(uuid.uuid4()),
            name,
            location,
            problem,
            image_url,
            "รอดำเนินการ",
            datetime.now().strftime("%Y-%m-%d"),
            str(report_time)
        ])

        send_email(name, location, problem)

        st.success("แจ้งปัญหาสำเร็จ และส่งอีเมลแจ้งเตือนแล้ว")

# -----------------------
# ADMIN PAGE
# -----------------------

if menu == "Admin":

    password = st.text_input("ใส่รหัสผ่าน Admin", type="password")

    if password == ADMIN_PASSWORD:

        st.success("เข้าสู่ระบบ Admin")

        data = sheet.get_all_records()

        df = pd.DataFrame(data)

        st.dataframe(df)

        st.subheader("เปลี่ยนสถานะการซ่อม")

        if not df.empty:

            job_id = st.selectbox("เลือก ID งาน", df["ID"])

            status = st.selectbox(
                "สถานะ",
                ["รอดำเนินการ","กำลังซ่อม","ซ่อมเสร็จ"]
            )

            if st.button("อัปเดตสถานะ"):

                cell = sheet.find(job_id)

                row = cell.row

                sheet.update_cell(row,6,status)

                st.success("อัปเดตสถานะเรียบร้อย")

    elif password != "":
        st.error("รหัสผ่านไม่ถูกต้อง")
