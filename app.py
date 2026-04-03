import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import uuid

# --------------------------
# PAGE CONFIG
# --------------------------

st.set_page_config(
    page_title="Facility Report",
    page_icon="🛠",
    layout="centered"
)

# --------------------------
# STYLE (Mobile UI)
# --------------------------

st.markdown("""
<style>

.stButton button{
width:100%;
border-radius:10px;
height:45px;
font-size:16px;
}

.block-container{
padding-top:2rem;
}

.ticket-card{
background:#f7f7f7;
padding:15px;
border-radius:10px;
margin-bottom:15px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------
# CONNECT GOOGLE SHEET
# --------------------------

scope = [
"https://spreadsheets.google.com/feeds",
"https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
st.secrets["gcp_service_account"],
scope
)

client = gspread.authorize(creds)

sheet = client.open("facility-report").sheet1

# --------------------------
# MENU
# --------------------------

menu = st.selectbox(
"เลือกเมนู",
["📝 แจ้งปัญหา","🔍 ติดตามงาน","🛠 Admin"]
)

# =========================
# REPORT PAGE
# =========================

if menu == "📝 แจ้งปัญหา":

    st.title("📝 แจ้งปัญหา")

    category = st.selectbox(
    "หมวดหมู่",
    ["ไฟฟ้า","ประปา","ห้องน้ำ","แอร์","เฟอร์นิเจอร์","อื่นๆ"]
    )

    name = st.text_input("ชื่อ")
    phone = st.text_input("เบอร์โทร")
    location = st.text_input("สถานที่")
    description = st.text_area("รายละเอียด")

    image = st.file_uploader(
    "📸 แนบรูป",
    type=["jpg","png","jpeg"]
    )

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
# TRACK PAGE
# =========================

elif menu == "🔍 ติดตามงาน":

    st.title("🔍 ติดตามงาน")

    ticket = st.text_input("Ticket ID")

    if ticket:

        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        result = df[df["ticket"] == ticket]

        if len(result)>0:

            r = result.iloc[0]

            st.markdown(f"""
            <div class="ticket-card">

            <b>Ticket:</b> {r['ticket']} <br>

            <b>หมวดหมู่:</b> {r['category']} <br>

            <b>สถานที่:</b> {r['location']} <br>

            <b>รายละเอียด:</b> {r['description']} <br>

            <b>สถานะ:</b> {r['status']} <br>

            <b>วันที่:</b> {r['date']} {r['time']}

            </div>
            """, unsafe_allow_html=True)

        else:

            st.warning("ไม่พบ Ticket")

# =========================
# ADMIN PAGE
# =========================

elif menu == "🛠 Admin":

    st.title("🔐 Admin")

    password = st.text_input(
    "รหัสผ่าน",
    type="password"
    )

    if password == "admin123":

        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        for i,row in df.iterrows():

            st.markdown("---")

            st.markdown(f"""
            <div class="ticket-card">

            <b>{row['ticket']}</b><br>
            หมวดหมู่: {row['category']}<br>
            สถานที่: {row['location']}<br>
            รายละเอียด: {row['description']}<br>
            วันที่: {row['date']} {row['time']}

            </div>
            """, unsafe_allow_html=True)

            status = st.selectbox(
            "สถานะ",
            ["pending","in progress","done"],
            index=["pending","in progress","done"].index(row["status"]),
            key=i
            )

            if st.button("บันทึกสถานะ",key=f"btn{i}"):

                sheet.update_cell(i+2,8,status)

                st.success("อัปเดตแล้ว")
