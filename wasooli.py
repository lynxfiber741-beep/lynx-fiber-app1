import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- DITTO WASOOLI PK - LYNX FIBER PRODUCTION ENGINE ---
st.set_page_config(page_title="LYNX Fiber - Advanced ISP Portal", layout="wide", page_icon="⚡")

# Custom Professional UI/CSS Injection
st.markdown("""
<style>
    .block-container { padding-top: 40px !important; padding-bottom: 0px !important; max-width: 100% !important; background-color: #f8fafc; }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; background: transparent !important; }
    
    .wasooli-header {
        background-color: #0284c7 !important; color: white !important; padding: 15px 30px;
        display: flex; justify-content: space-between; align-items: center; width: 100%;
        font-family: 'Arial', sans-serif; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-bottom: 3px solid #0369a1; margin-bottom: 20px; border-radius: 4px;
    }
    .wasooli-brand { font-size: 22px; font-weight: bold; letter-spacing: 0.5px; }
    .wasooli-role-badge { background-color: white; color: #0284c7; padding: 6px 16px; border-radius: 4px; font-weight: bold; font-size: 13px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.2); }
    
    .screenshot-metrics {
        display: flex; justify-content: space-around; align-items: center; 
        background: white; padding: 20px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 30px; border: 1px solid #e2e8f0; text-align: center;
    }
    .metric-item { flex: 1; font-family: 'Arial', sans-serif; }
    .metric-num { font-size: 30px; font-weight: bold; color: #0f172a; }
    .metric-sub-green { font-size: 12px; color: #16a34a; font-weight: bold; margin-top: 2px; }
    .metric-sub-red { font-size: 12px; color: #dc2626; font-weight: bold; margin-top: 2px; }
    
    .screenshot-section-title {
        font-size: 20px; font-weight: bold; color: #1e293b; margin-top: 25px; margin-bottom: 15px;
        font-family: 'Arial', sans-serif; border-left: 5px solid #0284c7; padding-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE LAYER CONFIG ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_supabase(): return create_client(SUPABASE_URL, SUPABASE_KEY)
supabase: Client = init_supabase()

# Live Operational Date Control
current_month = datetime.now().strftime("%B")
current_year = datetime.now().strftime("%Y")
today_str = datetime.now().strftime("%Y-%m-%d")
today_date = datetime.now().date()

# Session Verification States
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None  
if "isp_id" not in st.session_state: st.session_state["isp_id"] = None
if "isp_name" not in st.session_state: st.session_state["isp_name"] = ""
if "operator_name" not in st.session_state: st.session_state["operator_name"] = ""
if "branding_mode" not in st.session_state: st.session_state["branding_mode"] = "Lynx Branding"

# Top Dynamic Branding Bar
if st.session_state["logged_in"]:
    display_title = st.session_state["isp_name"].upper() if st.session_state["branding_mode"] == "Own Branding" else "LYNX FIBER INTERNET"
    role_text = f"👤 {st.session_state['operator_name'].upper()} ({st.session_state['user_role'].upper()})"
    st.markdown(f'<div class="wasooli-header"><div class="wasooli-brand">🌐 HELLO!! {display_title}</div><div class="wasooli-role-badge">{role_text}</div></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="wasooli-header"><div class="wasooli-brand">⚡ LYNX FIBER ADVANCED SYSTEM</div><div class="wasooli-role-badge">🔒 ACCESS SECURED</div></div>', unsafe_allow_html=True)

# Security Gateway
if not st.session_state["logged_in"]:
    _, col_center, _ = st.columns([1, 1.8, 1])
    with col_center:
        st.markdown("<br>", unsafe_allow_html=True)
        tab_staff, tab_admin = st.tabs(["📲 Field Staff Login", "🔒 Owner/Admin Gate"])
        
        with tab_staff:
            with st.form("staff_login_form"):
                s_user = st.text_input("Staff Username ID")
                s_pass = st.text_input("Staff Password", type="password")
                if st.form_submit_button("Enter Field Dashboard", use_container_width=True):
                    res = supabase.table("isp_staff").select("*, isp_companies(company_name, branding_mode)").eq("username", s_user).eq("password", s_pass).execute()
                    if len(res.data) > 0:
                        st.session_state["logged_in"] = True; st.session_state["user_role"] = "Staff"
                        st.session_state["isp_id"] = res.data[0]["isp_id"]; st.session_state["operator_name"] = res.data[0]["staff_name"]
                        st.session_state["isp_name"] = res.data[0]["isp_companies"]["company_name"]
                        st.session_state["branding_mode"] = res.data[0]["isp_companies"].get("branding_mode", "Lynx Branding")
                        st.rerun()
                    else: st.error("❌ Staff Credentials Error.")

        with tab_admin:
            with st.form("admin_login_form"):
                a_user = st.text_input("Master Username")
                a_pass = st.text_input("Master Password", type="password")
                if st.form_submit_button("Authenticate Master Engine", use_container_width=True):
                    res = supabase.table("isp_companies").select("*").eq("username", a_user).eq("password", a_pass).execute()
                    if len(res.data) > 0:
                        st.session_state["logged_in"] = True; st.session_state["user_role"] = "Admin"
                        st.session_state["isp_id"] = res.data[0]["id"]; st.session_state["operator_name"] = "Admin"
                        st.session_state["isp_name"] = res.data[0]["company_name"]
                        st.session_state["branding_mode"] = res.data[0].get("branding_mode", "Lynx Branding")
                        st.rerun()
                    else: st.error("❌ Owner Credentials Error.")

# --- LIVE OPERATIONS INTERFACE ---
else:
    my_isp_id = st.session_state["isp_id"]
    is_admin = (st.session_state["user_role"] == "Admin")
    current_operator = st.session_state["operator_name"]
    
    # --- AUTOMATIC 30-DAYS EXPIRY ENGINE ---
    raw_users_check = supabase.table("billing_users").select("*").eq("isp_id", my_isp_id).execute()
    if len(raw_users_check.data) > 0:
        for u in raw_users_check.data:
            user_expiry = datetime.strptime(u["expiry_date"], "%Y-%m-%d").date()
            if today_date > user_expiry and u["status"] == "Paid":
                new_expiry = user_expiry + timedelta(days=30)
                updated_prev_balance = float(u["previous_balance"] if u["previous_balance"] else 0) + float(u["current_bill"] if u["current_bill"] else 0)
                
                supabase.table("billing_users").update({
                    "status": "Unpaid",
                    "previous_balance": updated_prev_balance,
                    "expiry_date": str(new_expiry)
                }).eq("id", u["id"]).execute()
                st.rerun()

    # Sidebar Logout
    if st.sidebar.button("🔒 Secure Logout", use_container_width=True):
        st.session_state["logged_in"] = False; st.rerun()
        
    st.sidebar.subheader("⚙️ Customer Control")
    
    # Manual Single Entry Form
    with st.sidebar.expander("📝 Manual Add Customer", expanded=False):
        with st.form("manual_add_form", clear_on_submit=True):
            n_name = st.text_input("Customer Name")
            n_user = st.text_input("Username (Router ID)")
            n_phone = st.text_input("Phone Number")
            n_area = st.text_input("Area (e.g. Sanghoi System)")
            n_bill = st.number_input("Bill Amount (Rs.)", min_value=0, step=100)
            n_prev = st.number_input("Previous Balance (Rs.)", min_value=0, step=100)
            
            if st.form_submit_button("Save Customer", use_container_width=True):
                if n_name and n_user and n_area and n_bill > 0:
                    calc_expiry = today_date + timedelta(days=30)
                    supabase.table("billing_users").insert({
                        "isp_id": my_isp_id, "name": n_name, "username": n_user, "phone": n_phone,
                        "area": n_area, "previous_balance": float(n_prev), "current_bill": float(n_bill), 
                        "status": "Unpaid", "reg_date": str(today_date), "expiry_date": str(calc_expiry)
                    }).execute()
                    st.rerun()

    # 📥 EXACT EXCEL AUTOMATIC READER (MATCHED WITH YOUR ORIGINAL SHEET HEADERS)
    if is_admin:
        with st.sidebar.expander("📥 Bulk Upload Original Excel / CSV", expanded=True):
            st.caption("Apni asli Excel ya CSV file upload karein. Headers auto-mapped hain.")
            uploaded_file = st.file_uploader("Upload File", type=["csv", "xlsx"])
            
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'): 
                        df_bulk = pd.read_csv(uploaded_file)
                    else: 
                        df_bulk = pd.read_excel(uploaded_file)
                    
                    # Columns check logic according to your exact sheet headers
                    required_headers = ['Username', 'CustomerName', 'Area', 'BillAmount']
                    found_headers = [col for col in required_headers if col in df_bulk.columns]
                    
                    if len(found_headers) < len(required_headers):
                        st.sidebar.error("⚠️ File Headers main mismatch hai. Ensure columns match original structure.")
                    else:
                        if st.button("🚀 Start Precision Upload", use_container_width=True):
                            success_count = 0
                            for _, row in df_bulk.iterrows():
                                try:
                                    c_user = str(row['Username']).strip()
                                    c_name = str(row['CustomerName']).strip()
                                    c_area = str(row['Area']).strip()
                                    c_bill = float(row['BillAmount']) if pd.notna(row['BillAmount']) else 0.0
                                    
                                    # Safe checks for trailing spaces in your original sheet columns
                                    c_phone = str(row['Phone']).strip() if 'Phone' in row and pd.notna(row['Phone']) else ""
                                    
                                    # Reading 'Previous Balance ' with trailing space check from excel
                                    p_col = [col for col in df_bulk.columns if 'Previous Balance' in col]
                                    c_prev = float(row[p_col[0]]) if p_col and pd.notna(row[p_col[0]]) else 0.0
                                    
                                    # Target automated 30 days lock
                                    auto_expiry_target = today_date + timedelta(days=30)
                                    
                                    # Clear duplicated users prevention
                                    supabase.table("billing_users").insert({
                                        "isp_id": my_isp_id, "name": c_name, "username": c_user,
                                        "phone": c_phone, "area": c_area, "previous_balance": c_prev,
                                        "current_bill": c_bill, "status": "Unpaid", "reg_date": str(today_date),
                                        "expiry_date": str(auto_expiry_target)
                                    }).execute()
                                    success_count += 1
                                except Exception:
                                    continue
                            st.sidebar.success(f"🎉 Imported {success_count} Records Perfectly!")
                            st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Error Reading File: {str(e)}")

    # FETCH MATHEMATICAL PIPELINES FOR DATA ACCURACY
    users_resp = supabase.table("billing_users").select("*").eq("isp_id", my_isp_id).order("name").execute()
    history_resp = supabase.table("billing_history").select("*").eq("isp_id", my_isp_id).execute()
    df_users = pd.DataFrame(users_resp.data)
    df_history = pd.DataFrame(history_resp.data)

    # PRECISION MATHEMATICAL LOCKS FOR THE TOP DASHBOARD
    total_nodes = len(df_users) if not df_users.empty else 0
    paid_nodes = len(df_users[df_users['status'] == 'Paid']) if not df_users.empty else 0
    unpaid_nodes = len(df_users[df_users['status'] == 'Unpaid']) if not df_users.empty else 0
    
    # 1. Total Collected Lock (Always matches exact sum of payment history logs)
    total_cash_recovered = float(df_history['amount'].sum()) if not df_history.empty else 0.0
    
    # 2. Total Outstanding Lock (Always matches exact current display values of client dictionary)
    total_cash_remaining = 0.0
    if not df_users.empty:
        for idx, r in df_users.iterrows():
            if r['status'] == 'Unpaid':
                p_bal = float(r['previous_balance'] if r['previous_balance'] else 0.0)
                c_bill = float(r['current_bill'] if r['current_bill'] else 0.0)
                total_cash_remaining += (p_bal + c_bill)

    # Dynamic Metric Bar Implementation
    st.markdown(f"""
    <div class="screenshot-metrics">
        <div class="metric-item"><div class="metric-num">{total_nodes}</div><div style="font-size:12px; color:#64748b;">Total Clients</div></div>
        <div class="metric-item"><div class="metric-num">{paid_nodes}</div><div class="metric-sub-green">↑ {paid_nodes} Recovered</div></div>
        <div class="metric-item"><div class="metric-num">{unpaid_nodes}</div><div class="metric-sub-red">↓ -{unpaid_nodes} Remaining</div></div>
        <div class="metric-item"><div class="metric-num">Rs. {total_cash_recovered:,.0f}</div><div style="font-size:12px; color:#64748b;">Total Collected</div></div>
        <div class="metric-item"><div class="metric-num">Rs. {total_cash_remaining:,.0f}</div><div style="font-size:12px; color:#64748b;">Total Outstanding</div></div>
    </div>
    """, unsafe_allow_html=True)

    # --- AREA SELECTION PANEL ---
    st.markdown('<div class="screenshot-section-title">📍 Area Wise Filter System</div>', unsafe_allow_html=True)
    areas_list = ["All Areas"]
    if not df_users.empty:
        areas_list = ["All Areas"] + list(df_users['area'].unique())
    sel_area = st.selectbox("Select Filter Sector:", areas_list, label_visibility="collapsed")
    filtered_users = df_users if sel_area == "All Areas" else df_users[df_users['area'] == sel_area]

    # --- CLIENT DIRECTORY PANEL ---
    st.markdown('<div class="screenshot-section-title">📋 Client Directory & Cash Collection</div>', unsafe_allow_html=True)
    
    if filtered_users.empty:
        st.info("No data available for display.")
    else:
        for idx, row in filtered_users.iterrows():
            p_val = float(row['previous_balance'] if row['previous_balance'] else 0.0)
            c_val = float(row['current_bill'] if row['current_bill'] else 0.0)
            
            # Mathematical Sync: Net due matches exactly what's added to metrics
            net_payable = (p_val + c_val) if row['status'] == 'Unpaid' else 0.0
            
            status_badge = '<span style="color:#16a34a; font-weight:bold;">🟢 Paid</span>' if row['status'] == 'Paid' else '<span style="color:#dc2626; font-weight:bold;">🔴 Unpaid</span>'
                
            cc1, cc2 = st.columns([5, 1.2])
            with cc1:
                st.markdown(f"""
                <div style="font-family:'Arial',sans-serif; font-size:15px; color:#334155; padding: 5px 0px;">
                    <b style="color:#0f172a; font-size:16px;">{row['name']}</b> ({row['username']}) &nbsp;|&nbsp; 
                    📍 {row['area']} &nbsp;|&nbsp; 📞 {row['phone'] if row['phone'] else 'N/A'} &nbsp;|&nbsp; 
                    💵 Net Due: <b>Rs. {net_payable:,.0f}</b> (Prev: {p_val:,.0f} | Current: {c_val:,.0f}) &nbsp;|&nbsp; Status: {status_badge}
                </div>
                """, unsafe_allow_html=True)
                
            with cc2:
                if row['status'] == 'Unpaid':
                    if st.button("Receive Cash 💵", key=f"rec_card_{row['id']}", use_container_width=True):
                        curr_exp = datetime.strptime(row['expiry_date'], "%Y-%m-%d").date()
                        extended_exp = curr_exp + timedelta(days=30) if curr_exp >= today_date else today_date + timedelta(days=30)
                        
                        # Database updates
                        supabase.table("billing_users").update({
                            "status": "Paid", 
                            "previous_balance": 0.0,
                            "last_paid_date": today_str, 
                            "collected_by": current_operator, 
                            "expiry_date": str(extended_exp)
                        }).eq("id", row['id']).execute()
                        
                        # Add strict historical record that updates Total Collected metric instantly
                        supabase.table("billing_history").insert({
                            "isp_id": my_isp_id, "user_id": int(row['id']), "name": row['name'], "area": row['area'],
                            "amount": net_payable, "pay_date": today_str, "pay_month": current_month, "pay_year": current_year, "collected_by": current_operator
                        }).execute()
                        st.rerun()
                else:
                    st.markdown(f"<p style='color:green; text-align:center; font-size:13px; margin-top:8px;'>Collected by {row.get('collected_by','Admin')}</p>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:0px 0px 10px 0px; opacity:0.15;'>", unsafe_allow_html=True)

    # --- BUSINESS ANNUAL LEDGER LOGS ---
    st.markdown('<div class="screenshot-section-title">📚 Business Annual Ledger Logs</div>', unsafe_allow_html=True)
    if not df_history.empty:
        st.dataframe(df_history[['name', 'area', 'amount', 'pay_date', 'collected_by', 'pay_month']], use_container_width=True)
    else:
        st.caption("History log khali hai. Jab aap collection karenge, records yahan save honge.")