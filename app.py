import streamlit as st
import pandas as pd
from datetime import datetime
import os

DATA_FILE = "data.csv"

st.set_page_config(page_title="ระบบแจ้งปัญหา")

menu = st.sidebar.selectbox(
    "เมนู",
    ["แจ้งปัญหา","ติดตามงาน","Admin"]
)

# ======================
# แจ้งปัญหา
# ======================

if menu == "แจ้งปัญหา":

    st.title("📝 แจ้งปัญหา")

    category = st.selectbox(
        "หมวดหมู่",
        ["ไฟฟ้า","ประปา","ห้องน้ำ","แอร์","เฟอร์นิเจอร์","อื่นๆ"]
    )

    name = st.text_input("ชื่อ")
    phone = st.text_input("เบอร์โทร")
    location = st.text_input("สถานที่")
    description = st.text_area("รายละเอียด")

    image = st.file_uploader("แนบรูป", type=["jpg","png","jpeg"])

    if st.button("ส่งรายงาน"):

        ticket = "RTP" + str(int(datetime.now().timestamp()))

        if image:
            os.makedirs("uploads",exist_ok=True)
            path = f"uploads/{image.name}"
            with open(path,"wb") as f:
                f.write(image.getbuffer())
        else:
            path = ""

        data = {
            "ticket":[ticket],
            "category":[category],
            "name":[name],
            "phone":[phone],
            "location":[location],
            "description":[description],
            "image":[path],
            "status":["pending"],
            "date":[datetime.now()]
        }

        df_new = pd.DataFrame(data)

        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            df = pd.concat([df,df_new])
        else:
            df = df_new

        df.to_csv(DATA_FILE,index=False)

        st.success(f"ส่งสำเร็จ Ticket: {ticket}")

# ======================
# ติดตามงาน
# ======================

elif menu == "ติดตามงาน":

    st.title("🔍 ติดตามงาน")

    ticket = st.text_input("กรอกรหัส Ticket")

    if os.path.exists(DATA_FILE):

        df = pd.read_csv(DATA_FILE)

        result = df[df["ticket"] == ticket]

        if len(result)>0:

            st.write(result)

        else:
            st.warning("ไม่พบข้อมูล")

# ======================
# ADMIN
# ======================

elif menu == "Admin":

    st.title("🔐 Admin")

    password = st.text_input("รหัสผ่าน",type="password")

    if password == "admin123":

        if os.path.exists(DATA_FILE):

            df = pd.read_csv(DATA_FILE)

            for i,row in df.iterrows():

                st.subheader(row["ticket"])

                st.write(row["description"])

                status = st.selectbox(
                    "สถานะ",
                    ["pending","in progress","done"],
                    index=["pending","in progress","done"].index(row["status"]),
                    key=i
                )

                df.at[i,"status"] = status

            df.to_csv(DATA_FILE,index=False)
