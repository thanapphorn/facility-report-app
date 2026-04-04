import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime
import pandas as pd
import uuid
import io

# -----------------------
# GOOGLE API CONNECT
# -----------------------

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

service_account_info = dict(st.secrets["gcp_service_account"])
service_account_info["private_key"] = service_account_info["private_key"].replace("\\n", "\n")

creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open("facility-report").sheet1

drive_service = build(
    "drive",
    "v3",
    credentials=creds
)

# -----------------------
# UPLOAD IMAGE FUNCTION
# -----------------------

def upload_to_drive(uploaded_file):

    file_metadata = {
        "name": uploaded_file.name,
        "parents": ["1FbKMmQ-MyToYHWnxRRcXEepqXhUXqT4t"]
    }

    media = MediaIoBaseUpload(
        io.BytesIO(uploaded_file.getvalue()),
        mimetype=uploaded_file.type
    )

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id",
        supportsAllDrives=True
    ).execute()

    file_id = file.get("id")

    # ทำให้รูปเปิดดูได้
    drive_service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"}
    ).execute()

    return f"https://drive.google.com/uc?id={file_id}"

# -----------------------
# UI
# -----------------------

st.set_page_config(page_title="Facility Reporting")

st.title("🏢 Facility Reporting System")

menu = st.sidebar.selectbox(
    "Menu",
    ["📩 แจ้งปัญหา", "🔎 ติดตามสถานะ", "👨‍💼 Admin"]
)

# -----------------------
# REPORT ISSUE
# -----------------------

if menu == "📩 แจ้งปัญหา":

    st.header("แจ้งปัญหา")

    category = st.selectbox(
        "หมวดหมู่",
        ["ไฟฟ้า","ประปา","ความสะอาด","อุปกรณ์ชำรุด","อื่นๆ"]
    )

    name = st.text_input("ชื่อ")
    phone = st.text_input("เบอร์โทร")
    location = st.text_input("สถานที่")
    description = st.text_area("รายละเอียด")

    image = st.file_uploader(
        "แนบรูป",
        type=["jpg","png","jpeg"]
    )

    if st.button("ส่งรายงาน"):

        report_id = "RTP-" + str(uuid.uuid4())[:6]

        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H:%M")

        image_url = ""

        if image is not None:
            image_url = upload_to_drive(image)

        sheet.append_row([
            report_id,
            category,
            name,
            phone,
            location,
            description,
            image_url,
            "pending",
            date,
            time
        ])

        st.success("ส่งรายงานสำเร็จ")
        st.write("รหัสติดตาม:", report_id)

# -----------------------
# TRACK STATUS
# -----------------------

elif menu == "🔎 ติดตามสถานะ":

    st.header("ติดตามสถานะ")

    track_id = st.text_input("กรอกรหัสติดตาม")

    if st.button("ค้นหา"):

        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        result = df[df["report_id"] == track_id]

        if len(result) > 0:

            row = result.iloc[0]

            st.write("สถานะ:", row["status"])
            st.write("สถานที่:", row["location"])
            st.write("รายละเอียด:", row["description"])

            if row["image_url"] != "":
                st.image(row["image_url"])

        else:

            st.error("ไม่พบข้อมูล")

# -----------------------
# ADMIN
# -----------------------

elif menu == "👨‍💼 Admin":

    st.header("Admin Panel")

    password = st.text_input("รหัสผ่าน", type="password")

    if password == "admin123":

        data = sheet.get_all_records()

        for i,row in enumerate(data):

            st.write("---")

            st.write("ID:", row["report_id"])
            st.write("สถานที่:", row["location"])
            st.write("รายละเอียด:", row["description"])

            if row["image_url"] != "":
                st.image(row["image_url"], width=300)

            status = st.selectbox(
                "เปลี่ยนสถานะ",
                ["pending","กำลังดำเนินการ","เสร็จแล้ว"],
                key=i
            )

            if st.button("อัปเดต", key=f"btn{i}"):

                sheet.update_cell(i+2,8,status)

                st.success("อัปเดตสถานะแล้ว")
