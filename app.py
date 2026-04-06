import streamlit as st
import pandas as pd
import random
from datetime import datetime
import base64
from io import BytesIO

st.set_page_config(page_title="Facility Report", page_icon="🏢", layout="wide")


# -----------------------
# Menu
# -----------------------

st.title("🏢 ระบบแจ้งปัญหาภายในอาคาร")

menu = st.radio(
    "",
    ["📢 แจ้งปัญหา","🔎 ติดตามสถานะ","🔐 Admin"],
    horizontal=True
)

# -----------------------
# PAGE 1 : REPORT
# -----------------------

if menu == "📢 แจ้งปัญหา":

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

    image = st.file_uploader("📸 อัปโหลดรูปภาพ", type=["jpg", "jpeg", "png", "gif"])

    confirm = st.checkbox("ยืนยันการแจ้งปัญหา")

    if st.button("ส่งรายงาน"):

        if not confirm:
            st.warning("กรุณายืนยันก่อนแจ้ง")
        else:

            report_id = "RP-" + str(random.randint(100000,999999))

            # แปลงรูปเป็น base64
            image_data = None
            if image is not None:
                image_bytes = image.read()
                image_data = base64.b64encode(image_bytes).decode()

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
                "Image": image_data,
                "ImageName": image.name if image else None
            }

            st.session_state.reports.append(report)

            st.success("แจ้งปัญหาสำเร็จ")
            st.code(report_id)

# -----------------------
# PAGE 2 : TRACK
# -----------------------

elif menu == "🔎 ติดตามสถานะ":

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

                # แสดงรูปภาพ
                if r["Image"]:
                    st.image(r["Image"], caption=r["ImageName"], width=300)
                else:
                    st.info("ไม่มีรูปภาพ")

        if not found:
            st.error("ไม่พบข้อมูล")

# -----------------------
# PAGE 3 : ADMIN
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
    # Dashboard
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
    # Filter
    # -----------------------

    col1,col2 = st.columns(2)

    with col1:
        search = st.text_input("🔎 Search ID")

    with col2:
        month = st.selectbox(
            "Filter เดือน",
            ["ทั้งหมด"] + df["Month"].unique().tolist()
        )

    filtered = df.copy()

    if search:
        filtered = filtered[filtered["ID"].str.contains(search)]

    if month != "ทั้งหมด":
        filtered = filtered[filtered["Month"] == month]

    # -----------------------
    # Pagination
    # -----------------------

    rows_per_page = 10
    total_rows = len(filtered)
    total_pages = (total_rows - 1) // rows_per_page + 1

    col1,col2,col3 = st.columns([1,2,1])

    with col1:
        if st.button("Previous") and st.session_state.page > 1:
            st.session_state.page -= 1

    with col3:
        if st.button("Next") and st.session_state.page < total_pages:
            st.session_state.page += 1

    st.write(f"Page {st.session_state.page} / {total_pages}")

    start = (st.session_state.page - 1) * rows_per_page
    end = start + rows_per_page

    page_data = filtered.iloc[start:end]

    # -----------------------
    # Table
    # -----------------------

    table = page_data.copy()
    table["Image"] = table["ImageName"].apply(
        lambda x: f"✓ {x}" if x else "-"
    )

    st.write(
        table[
            [
                "ID","Name","Phone","Category",
                "Location","Date","Time","Status","Image"
            ]
        ].to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

    # -----------------------
    # Update Status
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

    # -----------------------
    # View Report Detail
    # -----------------------

    st.subheader("📋 ดูรายละเอียดรายงาน")

    view_id = st.selectbox("เลือก ID เพื่อดูรายละเอียด", df["ID"])

    if st.button("แสดงรายละเอียด"):
        for r in st.session_state.reports:
            if r["ID"] == view_id:
                st.write("**รหัสแจ้ง:**", r["ID"])
                st.write("**ชื่อผู้แจ้ง:**", r["Name"])
                st.write("**เบอร์โทร:**", r["Phone"])
                st.write("**หมวดปัญหา:**", r["Category"])
                st.write("**สถานที่:**", r["Location"])
                st.write("**รายละเอียด:**", r["Detail"])
                st.write("**สถานะ:**", r["Status"])
                st.write("**วันที่:**", r["Date"], "เวลา:", r["Time"])

                if r["Image"]:
                    st.image(r["Image"], caption=r["ImageName"], width=400)
                else:
                    st.info("ไม่มีรูปภาพ")
