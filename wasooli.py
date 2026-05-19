import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- DITTO WASOOLI PK - MATCHING SCREENSHOT UI LAYOUT ---
st.set_page_config(page_title="LYNX Fiber - Advanced ISP Portal", layout="wide", page_icon="⚡")

# Custom UI/CSS Injection according to screenshot styling
st.markdown("""
<style>
    .block-container { padding-top: 50px !important; padding-bottom: 0px !important; max-width: 100% !important; background-color: #f8fafc; }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; background: transparent !important; }
    
    /* Responsive Top Bar Ribbon */
    .wasooli-header {
        background-color: #0284c7 !important; color: white !important; padding: 15px 30px;
        display: flex; justify-content: space-between; align-items: center; width: 100%;
        font-family: 'Arial', sans-serif; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-bottom: 3px solid #0369a1; margin-bottom: 20px; border-radius: 4px;
    }
    .wasooli-brand { font-size: 22px; font-weight: bold; letter-spacing: 0.5px; }
    .wasooli-role-badge { background-color: white; color: #0284c7; padding: 6px 16px; border-radius: 4px; font-weight: bold; font-size: 13px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.2); }
    
    /* Top Row Dynamic Metrics Indicators */
    .screenshot-metrics {
        display: flex; justify-content: space-around; align-items: center; 
        background: white; padding: 20px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 30px; border: 1px solid #e2e8f0; text-align: center;
    }
    .metric-item { flex: 1; font-family: 'Arial', sans-serif; }
    .metric-num { font-size: 32px; font-weight: bold; color: #0f172a; }
    .metric-sub-green { font-size: 12px; color: #16a34a; font-weight: bold; margin-top: 2px; }
    .metric-sub-red { font-size: 12px; color: #dc2626; font-weight: bold; margin-top: 2px; }
    
    /* Section Headings Styling matching screenshot icons */
    .screenshot-section-title {
        font-size: 22px; font-weight: bold; color: #1e293b; margin-top: 25px; margin-bottom: 15px;
        display: flex; align-items: center; gap: 8px; font-family: 'Arial', sans-serif;
    }
    
    /* Customer Card UI Renderer */
    .customer-card {
        background: white; padding: 15px 25px; border-radius: 6px; border: 1px solid #e2e8f0;
        margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.01);
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE LAYER CONFIG ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_supabase(): return create_client(SUPABASE_URL, SUPABASE_KEY)
supabase: Client = init_supabase()

# Live Operational Clocks
current_month = datetime.now().strftime("%B")
current_year = datetime.now().strftime("%Y")
today_str = datetime.now().strftime("%Y-%m-%d")
today_date = datetime.now().date()
MASTER_APPROVAL_CODE = "LYNX-SECURE-2026"

# Session Verification States
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None  
if "isp_id" not in st.session_state: st.session_state["isp_id"] = None
if "isp_name" not in st.session_state: st.session_state["isp_name"] = ""
if "operator_name" not in st.session_state: st.session_state["operator_name"] = ""
if "branding_mode" not in st.session_state: st.session_state["branding_mode"] = "Lynx Branding"

# Top Band Dynamic Display
if st.session_state["logged_in"]:
    display_title = st.session_state["isp_name"].upper() if st.session_state["branding_mode"] == "Own Branding" else "LYNX FIBER INTERNET"
    role_text = f"👤 {st.session_state['operator_name'].upper()} ({st.session_state['user_role'].upper()})"
    st.markdown(f'<div class="wasooli-header"><div class="wasooli-brand">🌐 HELLO!! {display_title}</div><div class="wasooli-role-badge">{role_text}</div></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="wasooli-header"><div class="wasooli-brand">⚡ LYNX FIBER ADVANCED SYSTEM</div><div class="wasooli-role-badge">🔒 ACCESS SECURED</div></div>', unsafe_allow_html=True)

# Portal Entry Security Gateways
if not st.session_state["logged_in"]:
    _, col_center, _ = st.columns([1, 1.8, 1])
    with col_center:
        st.markdown("<br>", unsafe_allow_html=True)
        tab_staff, tab_admin, tab_register = st.tabs(["📲 Field Staff Login", "🔒 Owner/Admin Gate", "📝 Corporate Signup"])
        
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

        with tab_register:
            with st.form("signup_master_form"):
                r_company = st.text_input("Company Corporate Name")
                r_user = st.text_input("Desired Admin Username")
                r_phone = st.text_input("Official Phone No")
                r_pass = st.text_input("Set Password", type="password")
                r_brand = st.selectbox("Branding Mode Pack", ["Lynx Branding", "Own Branding"])
                r_key = st.text_input("Master Activation Code", type="password")
                if st.form_submit_button("Register & Deploy Network", use_container_width=True):
                    if r_key != MASTER_APPROVAL_CODE: st.error("❌ Invalid Key.")
                    else:
                        supabase.table("isp_companies").insert({"company_name": r_company, "username": r_user, "password": r_pass, "phone": r_phone, "branding_mode": r_brand}).execute()
                        st.success("🎉 Registered successfully!")

# --- LIVE OPERATIONS INTERFACE ---
else:
    my_isp_id = st.session_state["isp_id"]
    is_admin = (st.session_state["user_role"] == "Admin")
    current_operator = st.session_state["operator_name"]
    
    # --- AUTOMATIC BACKGROUND BILLING ENGINE ---
    raw_users_check = supabase.table("billing_users").select("*").eq("isp_id", my_isp_id).execute()
    if len(raw_users_check.data) > 0:
        for u in raw_users_check.data:
            user_expiry = datetime.strptime(u["expiry_date"], "%Y-%m-%d").date()
            if today_date > user_expiry and u["status"] == "Paid":
                new_expiry = user_expiry + timedelta(days=30)
                supabase.table("billing_users").update({
                    "status": "Unpaid",
                    "previous_balance": float(u["previous_balance"]) + float(u["current_bill"]),
                    "expiry_date": str(new_expiry)
                }).eq("id", u["id"]).execute()
                st.rerun()

    # --- SIDEBAR CONTROL MATRIX ---
    if st.sidebar.button("🔒 Secure Logout", use_container_width=True):
        st.session_state["logged_in"] = False; st.rerun()
        
    st.sidebar.subheader("⚙️ Customer Operations")
    
    # 1. Manual Entry Matching Left Sidebar Input Structure
    with st.sidebar.expander("📝 Naya Customer Add Karein", expanded=True):
        with st.form("manual_add_screenshot_form", clear_on_submit=True):
            n_name = st.text_input("Customer Name")
            n_user = st.text_input("PPPoE / Router ID")
            n_phone = st.text_input("Phone Number")
            n_area = st.text_input("Area / Sector Colony")
            n_bill = st.number_input("Monthly Bill (Rs.)", min_value=0, step=100, value=0)
            n_prev = st.number_input("Previous Pending Balance (Optional)", min_value=0, step=100, value=0)
            n_days = st.number_input("Validity Days (Default 30)", min_value=1, value=30)
            
            if st.form_submit_button("Save Customer", use_container_width=True):
                if n_name and n_user and n_area and n_bill > 0:
                    calc_expiry = today_date + timedelta(days=int(n_days))
                    supabase.table("billing_users").insert({
                        "isp_id": my_isp_id, "name": n_name, "username": n_user, "phone": n_phone,
                        "area": n_area, "previous_balance": n_prev, "current_bill": n_bill, 
                        "status": "Unpaid", "reg_date": str(today_date), "expiry_date": str(calc_expiry)
                    }).execute()
                    st.rerun()

    # 2. Bulk Upload Engine with Fake Test Data Generation Feature
    if is_admin:
        with st.sidebar.expander("📥 Bulk Upload (Excel / CSV)", expanded=False):
            st.caption("Excel ya CSV file upload karein. Columns scheme nache di gayi hai:")
            st.code("name,username,phone,area,current_bill,previous_balance,expiry_days")
            
            # --- FAKE DATA GENERATOR BUTTON FOR BLANK SYSTEM TESTING ---
            if st.button("🎭 Inject Temporary Fake Data (3 Clients)", use_container_width=True):
                fake_samples = [
                    {"name": "Umer Wazir", "username": "umer (37301-7910445-9)", "phone": "03118808741", "area": "Sanghoi", "current_bill": 1200, "previous_balance": 0, "expiry_date": str(today_date + timedelta(days=30))},
                    {"name": "Ali Raza", "username": "ali.lynx", "phone": "03215544332", "area": "Saeela System", "current_bill": 1500, "previous_balance": 500, "expiry_date": str(today_date + timedelta(days=30))},
                    {"name": "Zain Ahmed", "username": "zain.fiber", "phone": "03009988776", "area": "Sanghoi", "current_bill": 1000, "previous_balance": 0, "expiry_date": str(today_date - timedelta(days=2))} # Automatically expired/Unpaid
                ]
                for fs in fake_samples:
                    # Injecting with ignore duplicates constraint logic
                    try:
                        supabase.table("billing_users").insert({
                            "isp_id": my_isp_id, "name": fs["name"], "username": fs["username"], "phone": fs["phone"],
                            "area": fs["area"], "current_bill": fs["current_bill"], "previous_balance": fs["previous_balance"],
                            "status": "Unpaid", "expiry_date": fs["expiry_date"], "reg_date": str(today_date)
                        }).execute()
                    except: pass
                st.success("Fake Sample Data Injected!")
                st.rerun()
                
            uploaded_file = st.file_uploader("Choose File", type=["csv", "xlsx"])
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'): df_bulk = pd.read_csv(uploaded_file)
                    else: df_bulk = pd.read_excel(uploaded_file)
                    
                    if st.button("🚀 Execute File Data Injection", use_container_width=True):
                        success_count = 0
                        for _, row in df_bulk.iterrows():
                            days_valid = int(row['expiry_days']) if 'expiry_days' in row else 30
                            row_expiry = today_date + timedelta(days=days_valid)
                            
                            supabase.table("billing_users").insert({
                                "isp_id": my_isp_id, "name": str(row['name']), "username": str(row['username']),
                                "phone": str(row['phone']) if 'phone' in row else "", "area": str(row['area']),
                                "previous_balance": float(row['previous_balance']) if 'previous_balance' in row else 0,
                                "current_bill": float(row['current_bill']), "status": "Unpaid",
                                "reg_date": str(today_date), "expiry_date": str(row_expiry)
                            }).execute()
                            success_count += 1
                        st.sidebar.success(f"Imported {success_count} entries successfully!")
                        st.rerun()
                except Exception as e:
                    st.sidebar.error("Header Mismatch Error. Use strict format.")

    # Data Sync Streams
    users_resp = supabase.table("billing_users").select("*").eq("isp_id", my_isp_id).order("name").execute()
    history_resp = supabase.table("billing_history").select("*").eq("isp_id", my_isp_id).execute()
    df_users = pd.DataFrame(users_resp.data)
    df_history = pd.DataFrame(history_resp.data)

    # --- SCREENSHOT REPLICA TOP COUNTERS ---
    total_nodes = len(df_users) if not df_users.empty else 0
    paid_nodes = len(df_users[df_users['status'] == 'Paid']) if not df_users.empty else 0
    unpaid_nodes = len(df_users[df_users['status'] == 'Unpaid']) if not df_users.empty else 0
    
    total_cash_recovered = df_history['amount'].sum() if not df_history.empty else 0
    total_cash_remaining = df_users[df_users['status'] == 'Unpaid'].apply(lambda r: float(r['previous_balance'])+float(r['current_bill']), axis=1).sum() if not df_users.empty else 0

    st.markdown(f"""
    <div class="screenshot-metrics">
        <div class="metric-item"><div class="metric-num">{total_nodes}</div></div>
        <div class="metric-item"><div class="metric-num">{paid_nodes}</div><div class="metric-sub-green">↑ {paid_nodes} Recovered</div></div>
        <div class="metric-item"><div class="metric-num">{unpaid_nodes}</div><div class="metric-sub-red">↓ -{unpaid_nodes} Remaining</div></div>
        <div class="metric-item"><div class="metric-num">Rs. {total_cash_recovered:,.0f}</div></div>
        <div class="metric-item"><div class="metric-num">Rs. {total_cash_remaining:,.0f}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # --- AREA WISE SORTING PANEL ---
    st.markdown('<div class="screenshot-section-title">📍 Area Wise Sorting Panel</div>', unsafe_allow_html=True)
    areas_list = ["All Areas"]
    if not df_users.empty:
        areas_list = ["All Areas"] + list(df_users['area'].unique())
    sel_area = st.selectbox("Apna Sector/Area Select Karein:", areas_list, label_visibility="collapsed")

    # Filtered dataset initialization
    filtered_users = df_users if sel_area == "All Areas" else df_users[df_users['area'] == sel_area]

    # --- CLIENT DIRECTORY & CASH COLLECTION PANEL ---
    st.markdown('<div class="screenshot-section-title">📋 Client Directory & Cash Collection</div>', unsafe_allow_html=True)
    
    if filtered_users.empty:
        st.info("System blank hai ya is area mein koi user nahi hai. Fake data inject karne ke liye sidebar panel use karein.")
    else:
        for idx, row in filtered_users.iterrows():
            p_val = float(row['previous_balance'])
            c_val = float(row['current_bill'])
            net_payable = p_val + c_val if row['status'] == 'Unpaid' else 0.0
            
            # Status badge selection matching screen
            if row['status'] == 'Paid':
                status_badge = '<span style="color:#16a34a; font-weight:bold;">🟢 Paid</span>'
            else:
                status_badge = '<span style="color:#dc2626; font-weight:bold;">🔴 Unpaid</span>'
                
            # Layout configuration for rows matching cards look precisely
            cc1, cc2 = st.columns([5, 1])
            
            with cc1:
                st.markdown(f"""
                <div style="font-family:'Arial',sans-serif; font-size:15px; color:#334155; padding: 5px 0px;">
                    <b style="color:#0f172a; font-size:16px;">{row['name']}</b> ({row['username']}) &nbsp;|&nbsp; 
                    📍 {row['area']} &nbsp;|&nbsp; 📞 {row['phone'] if row['phone'] else 'N/A'} &nbsp;|&nbsp; 
                    💵 Bill: Rs. {c_val:,.0f} &nbsp;|&nbsp; Status: {status_badge}
                </div>
                """, unsafe_allow_html=True)
                
            with cc2:
                if row['status'] == 'Unpaid':
                    if st.button("Receive Bill 💵", key=f"rec_card_{row['id']}", use_container_width=True):
                        # Auto calculations for extending target dates on recovery success
                        curr_exp = datetime.strptime(row['expiry_date'], "%Y-%m-%d").date()
                        extended_exp = curr_exp + timedelta(days=30) if curr_exp >= today_date else today_date + timedelta(days=30)
                        
                        supabase.table("billing_users").update({
                            "status": "Paid", "last_paid_date": today_str, "collected_by": current_operator, "expiry_date": str(extended_exp)
                        }).eq("id", row['id']).execute()
                        
                        supabase.table("billing_history").insert({
                            "isp_id": my_isp_id, "user_id": int(row['id']), "name": row['name'], "area": row['area'],
                            "amount": net_payable, "pay_date": today_str, "pay_month": current_month, "pay_year": current_year, "collected_by": current_operator
                        }).execute()
                        st.rerun()
                else:
                    st.markdown(f"<p style='color:green; text-align:center; font-size:12px; margin-top:8px;'>Done by {row.get('collected_by','Admin')}</p>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:0px 0px 10px 0px; opacity:0.15;'>", unsafe_allow_html=True)

    # --- BUSINESS ANNUAL LEDGER LOGS ---
    st.markdown('<div class="screenshot-section-title">📚 Business Annual Ledger Logs</div>', unsafe_allow_html=True)
    if not df_history.empty:
        st.dataframe(df_history[['name', 'area', 'amount', 'pay_date', 'collected_by', 'pay_month']], use_container_width=True)
    else:
        st.caption("Abhi tak koi transaction entry generated nahi hui.")