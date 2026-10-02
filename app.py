import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PR Workflow System", page_icon="📝", layout="wide")

# --- จำลองฐานข้อมูลชั่วคราว ---
if "pr_database" not in st.session_state:
    st.session_state.pr_database = pd.DataFrame(columns=[
        "เลขที่ PR", "วันที่", "หน่วยงาน", "ใช้กับงาน", 
        "วันที่ต้องการใช้", "รายการสิ่งของ", "จำนวน", "สถานะ", "ผู้ขอซื้อ"
    ])

# --- ระบบล็อกอินแยกตาม 4 บทบาท ---
st.sidebar.markdown("### 🔐 ระบบเข้าสู่ระบบตามตำแหน่ง")
role = st.sidebar.selectbox(
    "เลือกบทบาทของคุณ:",
    [
        "1. ผู้ขอซื้อ (Requester)",
        "2. หัวหน้างาน / Supervisor",
        "3. ผู้จัดการ (Manager)",
        "4. ฝ่ายจัดซื้อ (Purchasing)"
    ]
)

password_input = st.sidebar.text_input("กรอกรหัสผ่านประจำตำแหน่ง:", type="password")
login_btn = st.sidebar.button("เข้าสู่ระบบ")

# กำหนดรหัสผ่านแยกตาม 4 ตำแหน่ง
ROLE_PASSWORDS = {
    "1. ผู้ขอซื้อ (Requester)": "req123",
    "2. หัวหน้างาน / Supervisor": "sup123",
    "3. ผู้จัดการ (Manager)": "mgr123",
    "4. ฝ่ายจัดซื้อ (Purchasing)": "pur123"
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

# ถ้ายังไม่ล็อกอิน
if st.session_state.current_role is None:
    st.title("📝 ระบบขอซื้อสินค้าและอนุมัติ (PR Workflow 4 ขั้นตอน)")
    st.info("👈 กรุณาเลือกบทบาทและกรอกรหัสผ่านที่แถบด้านข้าง (Sidebar)")
    
    st.markdown("### 🔑 รหัสผ่านทดสอบทั้ง 4 ตำแหน่ง:")
    st.code(
        "1. ผู้ขอซื้อ: req123\n"
        "2. หัวหน้างาน/Supervisor: sup123\n"
        "3. ผู้จัดการ: mgr123\n"
        "4. ฝ่ายจัดซื้อ: pur123"
    )
    st.stop()

# เมนูออกจากระบบ
st.sidebar.markdown("---")
if st.sidebar.button("ออกจากระบบ"):
    st.session_state.current_role = None
    st.rerun()

current_role = st.session_state.current_role

# ==========================================
# 1. ผู้ขอซื้อ (Requester)
# ==========================================
if current_role == "1. ผู้ขอซื้อ (Requester)":
    st.title("📝 ฟอร์มกรอกใบขอซื้อสินค้า (Purchase Requisition)")
    
    with st.form("pr_form"):
        col1, col2 = st.columns(2)
        with col1:
            requester_div = st.text_input("หน่วยงาน (Requester's Div.)", "ฝ่ายผลิต")
            for_job = st.text_input("ใช้กับงาน (For Job)", "Factory")
        with col2:
            req_date = st.date_input("วันที่ขอซื้อ (Date)", datetime.date.today())
            needed_date = st.date_input("วันที่ต้องการใช้งาน", datetime.date.today() + datetime.timedelta(days=2))
        
        st.markdown("---")
        item_desc = st.text_area("รายการสิ่งของ (Material Description)", "พุกเหล็ก 1 1/4\" (งานปรับปรุงภายในโรงงาน)")
        quantity = st.text_input("จำนวน (Quantity)", "30 Pcs.")
        requester_name = st.text_input("ผู้สั่งซื้อ / ผู้ขอเบิก (Issued By)", "สมชาย ใจดี")

        submit_pr = st.form_submit_button("📤 ส่งใบ PR ให้หัวหน้างาน (Supervisor)")

        if submit_pr:
            if item_desc.strip() == "" or requester_name.strip() == "":
                st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")
            else:
                new_pr_no = f"PR-{datetime.datetime.now().strftime('%Y%m%d')}-{len(st.session_state.pr_database)+1:03d}"
                new_row = {
                    "เลขที่ PR": new_pr_no,
                    "วันที่": str(req_date),
                    "หน่วยงาน": requester_div,
                    "ใช้กับงาน": for_job,
                    "วันที่ต้องการใช้": str(needed_date),
                    "รายการสิ่งของ": item_desc,
                    "จำนวน": quantity,
                    "สถานะ": "⏳ รอหัวหน้างานอนุมัติ (Pending Supervisor)",
                    "ผู้ขอซื้อ": requester_name
                }
                st.session_state.pr_database = pd.concat([st.session_state.pr_database, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"✅ ส่งใบ PR สำเร็จ! เลขที่เอกสาร: {new_pr_no}")

    st.markdown("### 📊 ประวัติใบ PR ของคุณ")
    if not st.session_state.pr_database.empty:
        st.dataframe(st.session_state.pr_database, use_container_width=True, hide_index=True)

# ==========================================
# 2. หัวหน้างาน / Supervisor
# ==========================================
elif current_role == "2. หัวหน้างาน / Supervisor":
    st.title("🛡️ หน้าจอหัวหน้างาน / Supervisor")
    st.write("ตรวจสอบและกลั่นกรองใบ PR เบื้องต้นจากลูกน้อง ก่อนส่งต่อให้ผู้จัดการอนุมัติ")

    if st.session_state.pr_database.empty:
        st.info("📭 ยังไม่มีใบ PR ในระบบ")
    else:
        pending_sup = st.session_state.pr_database[st.session_state.pr_database["สถานะ"].str.contains("รอหัวหน้างานอนุมัติ", na=False)]
        st.dataframe(st.session_state.pr_database, use_container_width=True, hide_index=True)
        
        if not pending_sup.empty:
            st.markdown("---")
            selected_pr = st.selectbox("เลือกเลขที่ PR ที่ต้องการตรวจสอบ:", pending_sup["เลขที่ PR"].tolist())
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ หัวหน้างานอนุมัติ (ส่งต่อผู้จัดการ)", use_container_width=True):
                    st.session_state.pr_database.loc[st.session_state.pr_database["เลขที่ PR"] == selected_pr, "สถานะ"] = "✔️ หัวหน้างานอนุมัติแล้ว (Waiting Manager)"
                    st.success("ส่งต่อไปยังผู้จัดการเรียบร้อย!")
                    st.rerun()
            with col2:
                if st.button("❌ ไม่อนุมัติ", use_container_width=True):
                    st.session_state.pr_database.loc[st.session_state.pr_database["เลขที่ PR"] == selected_pr, "สถานะ"] = "❌ ไม่อนุมัติโดยหัวหน้างาน"
                    st.error("ตีกลับเอกสารแล้ว")
                    st.rerun()

# ==========================================
# 3. ผู้จัดการ (Manager)
# ==========================================
elif current_role == "3. ผู้จัดการ (Manager)":
    st.title("👑 หน้าจอผู้จัดการ (Manager Approval)")
    st.write("อนุมัติขั้นสุดท้ายสำหรับใบ PR ที่ผ่านหัวหน้างานมาแล้ว เพื่อส่งต่อให้ฝ่ายจัดซื้อ")

    if st.session_state.pr_database.empty:
        st.info("📭 ยังไม่มีข้อมูลในระบบ")
    else:
        pending_mgr = st.session_state.pr_database[st.session_state.pr_database["สถานะ"].str.contains("หัวหน้างานอนุมัติแล้ว", na=False)]
        st.dataframe(st.session_state.pr_database, use_container_width=True, hide_index=True)
        
        if not pending_mgr.empty:
            st.markdown("---")
            selected_pr = st.selectbox("เลือกเลขที่ PR เพื่อพิจารณาอนุมัติขั้นสุดท้าย:", pending_mgr["เลขที่ PR"].tolist())
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ ผู้จัดการอนุมัติ (ส่งต่อฝ่ายจัดซื้อ)", use_container_width=True):
                    st.session_state.pr_database.loc[st.session_state.pr_database["เลขที่ PR"] == selected_pr, "สถานะ"] = "✔️ ผู้จัดการอนุมัติแล้ว (Waiting Purchasing)"
                    st.success("อนุมัติเรียบร้อย! ส่งต่อไปยังฝ่ายจัดซื้อแล้ว")
                    st.rerun()
            with col2:
                if st.button("❌ ไม่อนุมัติ", use_container_width=True):
                    st.session_state.pr_database.loc[st.session_state.pr_database["เลขที่ PR"] == selected_pr, "สถานะ"] = "❌ ไม่อนุมัติโดยผู้จัดการ"
                    st.error("ตีกลับเอกสารแล้ว")
                    st.rerun()

# ==========================================
# 4. ฝ่ายจัดซื้อ (Purchasing)
# ==========================================
elif current_role == "4. ฝ่ายจัดซื้อ (Purchasing)":
    st.title("🛒 หน้าจอฝ่ายจัดซื้อ (Purchasing Dashboard)")
    st.write("รับใบ PR ที่ผ่านการอนุมัติครบถ้วนจากผู้จัดการแล้ว เพื่อออกใบสั่งซื้อ (PO)")

    if st.session_state.pr_database.empty:
        st.info("📭 ยังไม่มีข้อมูลในระบบ")
    else:
        approved_df = st.session_state.pr_database[st.session_state.pr_database["สถานะ"].str.contains("ผู้จัดการอนุมัติแล้ว", na=False)]
        st.dataframe(st.session_state.pr_database, use_container_width=True, hide_index=True)
        
        if not approved_df.empty:
            st.markdown("---")
            selected_pr_pur = st.selectbox("เลือกเลขที่ PR เพื่อออก PO:", approved_df["เลขที่ PR"].tolist())
            po_no = st.text_input("กรอกเลขที่ใบสั่งซื้อ (PO. NO.):", "PO-2026-001")
            
            if st.button("📦 ออกใบสั่งซื้อสำเร็จ (Complete PO)"):
                st.session_state.pr_database.loc[st.session_state.pr_database["เลขที่ PR"] == selected_pr_pur, "สถานะ"] = f"📦 สั่งซื้อเรียบร้อย (PO: {po_no})"
                st.success(f"บันทึกเลขที่ PO สำเร็จ!")
                st.rerun()
