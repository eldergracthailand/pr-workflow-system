import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PR Workflow System", page_icon="📝", layout="wide")

# --- จำลองฐานข้อมูลชั่วคราวด้วย st.session_state (ในอนาคตเชื่อม Google Sheets ได้) ---
if "pr_database" not in st.session_state:
    st.session_state.pr_database = pd.DataFrame(columns=[
        "เลขที่ PR", "วันที่", "หน่วยงาน", "ใช้กับงาน", 
        "วันที่ต้องการใช้", "รายการสิ่งของ", "จำนวน", "สถานะ", "ผู้ขอซื้อ"
    ])

# --- ระบบล็อกอินแยกตามตำแหน่ง (Role-based Login) ---
st.sidebar.markdown("### 🔐 ระบบเข้าสู่ระบบตามตำแหน่ง")
role = st.sidebar.selectbox(
    "เลือกบทบาทของคุณ:",
    [
        "1. พนักงานผู้ขอซื้อ (Requester)",
        "2. หัวหน้างาน / ผู้จัดการ (Manager)",
        "3. ฝ่ายจัดซื้อ (Purchasing Division)"
    ]
)

password_input = st.sidebar.text_input("กรอกรหัสผ่านประจำตำแหน่ง:", type="password")
login_btn = st.sidebar.button("เข้าสู่ระบบ")

# กำหนดรหัสผ่านจำลองง่ายๆ แยกตามตำแหน่ง
ROLE_PASSWORDS = {
    "1. พนักงานผู้ขอซื้อ (Requester)": "req123",
    "2. หัวหน้างาน / ผู้จัดการ (Manager)": "mgr123",
    "3. ฝ่ายจัดซื้อ (Purchasing Division)": "pur123"
}

if "current_role" not in st.session_state:
    st.session_state.current_role = None

if login_btn:
    if password_input == ROLE_PASSWORDS.get(role):
        st.session_state.current_role = role
        st.sidebar.success("เข้าสู่ระบบสำเร็จ!")
        st.rerun()
    else:
        st.sidebar.error("รหัสผ่านไม่ถูกต้อง!")

# ถ้ายังไม่ล็อกอิน ให้แสดงหน้าต้อนรับ
if st.session_state.current_role is None:
    st.title("📝 ระบบขอซื้อสินค้าและอนุมัติ (PR Workflow)")
    st.info("👈 กรุณาเลือกบทบาทและกรอกรหัสผ่านที่แถบด้านข้าง (Sidebar) เพื่อเริ่มต้นใช้งาน")
    
    st.markdown("### 🔑 รหัสผ่านทดสอบสำหรับแต่ละตำแหน่ง:")
    st.code("พนักงานผู้ขอซื้อ: req123\nหัวหน้างาน/ผู้จัดการ: mgr123\nฝ่ายจัดซื้อ: pur123")
    st.stop()

# --- เมนูเมื่อล็อกอินเข้ามาแล้ว ---
st.sidebar.markdown("---")
if st.sidebar.button("ออกจากระบบ"):
    st.session_state.current_role = None
    st.rerun()

current_role = st.session_state.current_role

# ==========================================
# บทบาทที่ 1: พนักงานผู้ขอซื้อ (Requester)
# ==========================================
if current_role == "1. พนักงานผู้ขอซื้อ (Requester)":
    st.title("📝 ฟอร์มกรอกใบขอซื้อสินค้า (Purchase Requisition)")
    st.write("กรอกรายละเอียดตามใบ PR เพื่อส่งเรื่องให้หัวหน้างานอนุมัติ")

    with st.form("pr_form"):
        col1, col2 = st.columns(2)
        with col1:
            requester_div = st.text_input("หน่วยงาน (Requester's Div.)", "ฝ่ายผลิต")
            for_job = st.text_input("ใช้กับงาน (For Job)", "Factory")
        with col2:
            req_date = st.date_input("วันที่ขอซื้อ (Date)", datetime.date.today())
            needed_date = st.date_input("วันที่ต้องการใช้งาน (Material Required Date)", datetime.date.today() + datetime.timedelta(days=2))
        
        st.markdown("---")
        item_desc = st.text_area("รายการสิ่งของ (Material Description & Details)", "พุกเหล็ก 1 1/4\" (งานปรับปรุงภายในโรงงาน)\n*ขอ่วน เนื่องจากเป็นงานของผู้รับเหมา")
        quantity = st.text_input("จำนวน (Quantity)", "30 Pcs.")
        requester_name = st.text_input("ผู้สั่งซื้อ / ผู้ขอเบิก (Issued By)", "สมชาย ใจดี")

        submit_pr = st.form_submit_button("📤 ส่งใบ PR ให้หัวหน้าอนุมัติ")

        if submit_pr:
            if item_desc.strip() == "" or requester_name.strip() == "":
                st.warning("กรุณากรอกรายการสิ่งของและชื่อผู้ขอซื้อให้ครบถ้วน")
            else:
                # สร้างเลขที่ PR อัตโนมัติ (เช่น PR-2026-001)
                new_pr_no = f"PR-{datetime.datetime.now().strftime('%Y%m%d')}-{len(st.session_state.pr_database)+1:03d}"
                
                new_row = {
                    "เลขที่ PR": new_pr_no,
                    "วันที่": str(req_date),
                    "หน่วยงาน": requester_div,
                    "ใช้กับงาน": for_job,
                    "วันที่ต้องการใช้": str(needed_date),
                    "รายการสิ่งของ": item_desc,
                    "จำนวน": quantity,
                    "สถานะ": "⏳ รอหัวหน้าอนุมัติ (Pending Manager)",
                    "ผู้ขอซื้อ": requester_name
                }
                
                # บันทึกลงตารางจำลอง
                st.session_state.pr_database = pd.concat([
                    st.session_state.pr_database, 
                    pd.DataFrame([new_row])
                ], ignore_index=True)
                
                st.success(f"✅ ส่งใบ PR สำเร็จ! เลขที่เอกสารของคุณคือ: {new_pr_no}")

    # แสดงประวัติ PR ที่ผู้ใช้คนนี้เคยส่ง
    st.markdown("### 📊 ประวัติใบ PR ที่คุณส่งไปแล้ว")
    if not st.session_state.pr_database.empty:
        st.dataframe(st.session_state.pr_database, use_container_width=True, hide_index=True)
    else:
        st.info("ยังไม่มีประวัติการขอซื้อ")

# ==========================================
# บทบาทที่ 2: หัวหน้างาน / ผู้จัดการ (Manager)
# ==========================================
elif current_role == "2. หัวหน้างาน / ผู้จัดการ (Manager)":
    st.title("🛡️ หน้าจอตรวจสอบและอนุมัติใบ PR (Manager Dashboard)")
    st.write("ตรวจสอบรายการขอซื้อจากพนักงาน และกดอนุมัติเพื่อส่งต่อให้ฝ่ายจัดซื้อ")

    if st.session_state.pr_database.empty:
        st.info("📭 ยังไม่มีใบ PR ในระบบขณะนี้")
    else:
        st.dataframe(st.session_state.pr_database, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("✍️ ทำรายการอนุมัติเอกสาร")
        
        # เลือกเลขที่ PR ที่ต้องการอนุมัติ
        pr_options = st.session_state.pr_database["เลขที่ PR"].tolist()
        selected_pr = st.selectbox("เลือกเลขที่ PR ที่ต้องการตรวจสอบ:", pr_options)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ ออนุมัติใบ PR นี้ (Approve)", use_container_width=True):
                st.session_state.pr_database.loc[
                    st.session_state.pr_database["เลขที่ PR"] == selected_pr, "สถานะ"
                ] = "✔️ หัวหน้าอนุมัติแล้ว (Waiting Purchasing)"
                st.success(f"อนุมัติใบ PR รหัส {selected_pr} เรียบร้อยแล้ว ส่งต่อไปยังแผนกจัดซื้อ")
                st.rerun()
                
        with col2:
            if st.button("❌ ไม่อนุมัติ (Reject)", use_container_width=True):
                st.session_state.pr_database.loc[
                    st.session_state.pr_database["เลขที่ PR"] == selected_pr, "สถานะ"
                ] = "❌ ไม่อนุมัติโดยผู้จัดการ"
                st.error(f"ตีกลับใบ PR รหัส {selected_pr} เรียบร้อย")
                st.rerun()

# ==========================================
# บทบาทที่ 3: ฝ่ายจัดซื้อ (Purchasing Division)
# ==========================================
elif current_role == "3. ฝ่ายจัดซื้อ (Purchasing Division)":
    st.title("🛒 หน้าจอจัดการฝ่ายจัดซื้อ (Purchasing Dashboard)")
    st.write("แสดงรายการใบ PR ที่ผ่านการอนุมัติจากผู้จัดการแล้ว เพื่อดำเนินการสั่งซื้อต่อไป")

    if st.session_state.pr_database.empty:
        st.info("📭 ยังไม่มีข้อมูลในระบบ")
    else:
        # กรองเฉพาะใบที่หัวหน้าอนุมัติแล้ว
        approved_df = st.session_state.pr_database[
            st.session_state.pr_database["สถานะ"].str.contains("หัวหน้าอนุมัติแล้ว", na=False)
        ]
        
        st.markdown("### 📌 รายการ PR ที่รอจัดซื้อดำเนินการ")
        if not approved_df.empty:
            st.dataframe(approved_df, use_container_width=True, hide_index=True)
            
            selected_pr_pur = st.selectbox("เลือกเลขที่ PR เพื่อบันทึกการสั่งซื้อ (PO):", approved_df["เลขที่ PR"].tolist())
            po_no = st.text_input("กรอกเลขที่ใบสั่งซื้อ (PO. NO.):", "PO-2026-999")
            
            if st.button("📦 ยืนยันออกใบสั่งซื้อ (Complete PO)"):
                st.session_state.pr_database.loc[
                    st.session_state.pr_database["เลขที่ PR"] == selected_pr_pur, "สถานะ"
                ] = f"📦 สั่งซื้อเรียบร้อย (PO: {po_no})"
                st.success(f"บันทึกเลขที่ PO สำหรับ PR {selected_pr_pur} เรียบร้อย!")
                st.rerun()
        else:
            st.info("ยังไม่มีใบ PR ที่ผ่านการอนุมัติจากหัวหน้าในขณะนี้")

        st.markdown("---")
        st.markdown("### 📋 ประวัติ PR ทั้งหมดในระบบภาพรวม")
        st.dataframe(st.session_state.pr_database, use_container_width=True, hide_index=True)
