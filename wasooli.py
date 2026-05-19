import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- DITTO WASOOLI PK PREMIUM ENGINE WITH AUTO-EXPIRY & BULK UPLOAD ---
st.set_page_config(page_title="LYNX Fiber - Advanced ISP Portal", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    .block-container { padding-top: 50px !important; padding-bottom: 0px !important; max-width: 100% !important; background-color: #f8fafc; }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; background: transparent !important; }
    
    .wasooli-header {
        background-color: #0284c7 !important; color: white !important; padding: 15px 30px;
        display: flex; justify-content: space-between; align-items: center; width: 100%;
        font-family: 'Arial', sans-serif; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-bottom: 3px solid #0369a1; margin-bottom: 20px; border-radius: 4px;
    }
    .wasooli-brand { font-size: 22px; font-weight: bold; letter-spacing: 0.5px; }
    .wasooli-role-badge { background-color: white; color: #0284c7; padding: 6px 16px; border-radius: 4px; font-weight: bold; font-size: 13px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.2); }
    
    .action-row { display: flex; gap: 12px; margin-top: 10px; margin-bottom: 25px; flex-wrap: wrap; }
    .action-card-btn {
        background: linear-gradient(135deg, #0284c7, #0369a1); color: white; border: none; padding: 12px 24px; border-radius: 4px; font-size: 14px; font-weight: bold; text-align: center; flex: 1; min-width: 180px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-box-container { display: flex; gap: 20px; margin-bottom: 25px; flex-wrap: wrap; }
    .metric-box { background: white; padding: 15px 25px; border-radius: 6px; border: 1px solid #e2e8f0; border-top: 4px solid #0284c7; flex: 1; min-width: 220px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .metric-box-title { color: #64748b; font-size: 13px; font-weight: bold; text-transform: uppercase; }
    .metric-box-value { color: #0f172a; font-size: 28px; font-weight: bold; margin-top: 5px; }
    
    .table-section-heading { color: #0284c7 !important; font-size: 20px; font-weight: bold; margin-top: 20px; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE LAYER CONFIG ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_supabase(): return create_client(SUPABASE_URL, SUPABASE_KEY)
supabase: Client = init_supabase()

# Timing Globals
current_month = datetime.now().strftime("%B")
current_year = datetime.now().strftime("%Y")
today_str = datetime.now().strftime("%Y-%m-%d")
today_date = datetime.now().date()
MASTER_APPROVAL_CODE = "LYNX-SECURE-2026"

# Stateful Authentication Configurations
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None  
if "isp_id" not in st.session_state: st.session_state["isp_id"] = None
if "isp_name" not in st.session_state: st.session_state["isp_name"] = ""
if "operator_name" not in st.session_state: st.session_state["operator_name"] = ""
if "branding_mode" not in st.session_state: st.session_state["branding_mode"] = "Lynx Branding"

# Top Band Display
if st.session_state["logged_in"]:
    display_title = st.session_state["isp_name"].upper() if st.session_state["branding_mode"] == "Own Branding" else "LYNX FIBER INTERNET"
    role_text = f"👤 {st.session_state['operator_name'].upper()} ({st.session_state['user_role'].upper()})"
    st.markdown(f'<div class="wasooli-header"><div class="wasooli-brand">🌐 HELLO!! {display_title}</div><div class="wasooli-role-badge">{role_text}</div></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="wasooli-header"><div class="wasooli-brand">⚡ LYNX FIBER ADVANCED SYSTEM</div><div class="wasooli-role-badge">🔒 ACCESS SECURED</div></div>', unsafe_allow_html=True)

# Login Interfaces
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

# Active App Portal
else:
    my_isp_id = st.session_state["isp_id"]
    is_admin = (st.session_state["user_role"] == "Admin")
    current_operator = st.session_state["operator_name"]
    
    # ----------------==================================----------------
    # BACKGROUND ENGINE: AUTOMATIC EXPIRY & BILL BILLING SYSTEM
    # ----------------==================================----------------
    # Yeh code auto-pilot par kaam kareg, user ko khud reset karne ki zaroorat nahi padegi.
    raw_users_check = supabase.table("billing_users").select("*").eq("isp_id", my_isp_id).execute()
    if len(raw_users_check.data) > 0:
        for u in raw_users_check.data:
            user_expiry = datetime.strptime(u["expiry_date"], "%Y-%m-%d").date()
            # Agar customer ki expiry date aaj ki date se guzar chuki hai aur uska status 'Paid' tha:
            if today_date > user_expiry and u["status"] == "Paid":
                # 1. Pichle mahine ka cycle poora ho gaya, ab naya bill generate hoga aur status "Unpaid" ho jayega.
                # 2. Expiry date automatically theek 1 mahine aage barh jayegi.
                new_expiry = user_expiry + timedelta(days=30)
                supabase.table("billing_users").update({
                    "status": "Unpaid",
                    "previous_balance": float(u["previous_balance"]) + float(u["current_bill"]),
                    "expiry_date": str(new_expiry)
                }).eq("id", u["id"]).execute()
                st.rerun()

    # Top Ribbon Links
    st.markdown("""
    <div class="action-row">
        <div class="action-card-btn">User/Dealer Application</div>
        <div class="action-card-btn">BT Drivers</div>
        <div class="action-card-btn">Copy Query Link</div>
        <div class="action-card-btn">Download Bill</div>
        <div class="action-card-btn">Download Application</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Area Options
    st.sidebar.markdown(f"### Access: `{st.session_state['user_role']}`")
    if st.sidebar.button("🔒 Secure System Logout", use_container_width=True):
        st.session_state["logged_in"] = False; st.rerun()
        
    # Single Node Manual Entry
    with st.sidebar.expander("➕ Manual Single Node Register", expanded=False):
        with st.form("add_user_form", clear_on_submit=True):
            n_name = st.text_input("Customer Full Name")
            n_user = st.text_input("PPPoE / Router User ID")
            n_phone = st.text_input("Phone Number")
            n_area = st.text_input("Area Sector (e.g., Sanghoi)")
            n_prev = st.number_input("Previous Dues (Rs.)", min_value=0, step=50)
            n_bill = st.number_input("Monthly Package Bill (Rs.)", min_value=0, step=100)
            n_days = st.number_input("Validity Days Pack", min_value=1, value=30)
            if st.form_submit_button("Save Node Account", use_container_width=True):
                if n_name and n_user and n_area and n_bill > 0:
                    calc_expiry = today_date + timedelta(days=int(n_days))
                    supabase.table("billing_users").insert({
                        "isp_id": my_isp_id, "name": n_name, "username": n_user, "phone": n_phone,
                        "area": n_area, "previous_balance": n_prev, "current_bill": n_bill, 
                        "status": "Unpaid", "reg_date": str(today_date), "expiry_date": str(calc_expiry)
                    }).execute()
                    st.rerun()

    # ----------------==================================----------------
    # BULK EXCEL / CSV UPLOADER PANEL (ADMIN ONLY FOR SECURITY)
    # ----------------==================================----------------
    if is_admin:
        with st.sidebar.expander("📥 BULK UPLOAD (Excel / CSV)", expanded=True):
            st.caption("Excel/CSV file upload karein. Columns ka naam nache diye gaye mutabiq hona chahiye:")
            st.code("name, username, phone, area, previous_balance, current_bill, expiry_days")
            uploaded_file = st.file_uploader("Choose Excel or CSV File", type=["csv", "xlsx"])
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'): df_bulk = pd.read_csv(uploaded_file)
                    else: df_bulk = pd.read_excel(uploaded_file)
                    
                    if st.form_submit_button("🚀 Inject Bulk Data"):
                        success_count = 0
                        for _, row in df_bulk.iterrows():
                            days_valid = int(row['expiry_days']) if 'expiry_days' in row else 30
                            row_expiry = today_date + timedelta(days=days_valid)
                            
                            supabase.table("billing_users").insert({
                                "isp_id": my_isp_id,
                                "name": str(row['name']),
                                "username": str(row['username']),
                                "phone": str(row['phone']) if 'phone' in row else "",
                                "area": str(row['area']),
                                "previous_balance": float(row['previous_balance']) if 'previous_balance' in row else 0,
                                "current_bill": float(row['current_bill']),
                                "status": "Unpaid",
                                "reg_date": str(today_date),
                                "expiry_date": str(row_expiry)
                            }).execute()
                            success_count += 1
                        st.sidebar.success(f"🎉 Successfully imported {success_count} customers!")
                        st.rerun()
                except Exception as e:
                    st.sidebar.error(f"File Format Error: Check headers correctly.")

        # Create Boys Panel
        with st.sidebar.expander("👥 Create Staff/Boy Accounts", expanded=False):
            with st.form("create_staff_form", clear_on_submit=True):
                st_name = st.text_input("Boy Full Name")
                st_user = st.text_input("Login Username ID")
                st_pass = st.text_input("Login Password")
                if st.form_submit_button("Authorize Staff Member"):
                    if st_name and st_user and st_pass:
                        try:
                            supabase.table("isp_staff").insert({"isp_id": my_isp_id, "staff_name": st_name, "username": st_user, "password": st_pass}).execute()
                            st.sidebar.success(f"✔️ Account created for {st_name}!")
                        except: st.sidebar.error("❌ Username taken.")

    # Data Fetch Pipelines
    users_resp = supabase.table("billing_users").select("*").eq("isp_id", my_isp_id).order("name").execute()
    history_resp = supabase.table("billing_history").select("*").eq("isp_id", my_isp_id).execute()
    df_users = pd.DataFrame(users_resp.data)
    df_history = pd.DataFrame(history_resp.data)

    if is_admin: tab_summary, tab_areas, tab_history = st.tabs(["📊 Main Billing Directory", "📍 Area Grid Analytics", "📚 Annual Financial Ledgers"])
    else: tab_summary, tab_areas = st.tabs(["📊 Main Billing Directory", "📍 Area Grid Analytics"])

    with tab_summary:
        if df_users.empty: st.info("No active subscriber entries found.")
        else:
            total_nodes = len(df_users)
            paid_nodes = len(df_users[df_users['status'] == 'Paid'])
            unpaid_nodes = len(df_users[df_users['status'] == 'Unpaid'])
            
            st.markdown(f"""
            <div class="metric-box-container">
                <div class="metric-box"><div class="metric-box-title">👥 Active Subscriber Nodes</div><div class="metric-box-value">{total_nodes}</div></div>
                <div class="metric-box"><div class="metric-box-title">🟢 Settled Invoices (Paid)</div><div class="metric-box-value" style="color: #16a34a;">{paid_nodes}</div></div>
                <div class="metric-box"><div class="metric-box-title">🔴 Outstanding Collections (Unpaid)</div><div class="metric-box-value" style="color: #dc2626;">{unpaid_nodes}</div></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="table-section-heading">📋 CUSTOMER BILLING MATRIX (AUTOMATED MODES ACTIVE)</div>', unsafe_allow_html=True)
            
            # Row Sheets Grid View
            ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9 = st.columns([0.6, 1.2, 1.4, 1.1, 1.0, 0.8, 0.8, 1.3, 1.5])
            ch1.markdown("**CustID**")
            ch2.markdown("**Internet ID**")
            ch3.markdown("**Subscriber Name**")
            ch4.markdown("**Area Sector**")
            ch5.markdown("**Previous**")
            ch6.markdown("**Current**")
            ch7.markdown("**Total Due**")
            ch8.markdown("**🕒 Expiry Date**")
            ch9.markdown("**Action Panel**")
            st.markdown("<hr style='margin: 0.5em 0px; border-top: 2px solid #0284c7;'>", unsafe_allow_html=True)
            
            for index, row in df_users.iterrows():
                prev_val = float(row['previous_balance'])
                curr_val = float(row['current_bill'])
                total_due = prev_val + curr_val if row['status'] == 'Unpaid' else 0.0
                status_color = "green" if row['status'] == 'Paid' else "red"
                
                # Expiry conversion formatting
                exp_dt = datetime.strptime(row['expiry_date'], "%Y-%m-%d").strftime("%d-%b-%Y")
                
                r1, r2, r3, r4, r5, r6, r7, r8, r9 = st.columns([0.6, 1.2, 1.4, 1.1, 1.0, 0.8, 0.8, 1.3, 1.5])
                r1.write(f"#{row['id']}")
                r2.write(row['username'])
                r3.write(row['name'])
                r4.write(row['area'])
                r5.write(f"{prev_val:,.0f}")
                r6.write(f"{curr_val:,.0f}")
                r7.markdown(f"<b style='color:{status_color};'>{total_due:,.0f}</b>", unsafe_allow_html=True)
                r8.write(f"📅 {exp_dt}")
                
                if row['status'] == 'Unpaid':
                    if r9.button("Receive Bill 💵", key=f"rec_{row['id']}", use_container_width=True):
                        # Billing validation pipeline activation
                        # Jab bill receive hoga to automatic uski expiry date mazeed 30 days barha di jaye gi
                        current_exp = datetime.strptime(row['expiry_date'], "%Y-%m-%d").date()
                        extended_exp = current_exp + timedelta(days=30) if current_exp >= today_date else today_date + timedelta(days=30)
                        
                        supabase.table("billing_users").update({
                            "status": "Paid", 
                            "last_paid_date": today_str, 
                            "collected_by": current_operator,
                            "expiry_date": str(extended_exp)
                        }).eq("id", row['id']).execute()
                        
                        supabase.table("billing_history").insert({
                            "isp_id": my_isp_id, "user_id": int(row['id']), "name": row['name'], "area": row['area'],
                            "amount": total_due, "pay_date": today_str, "pay_month": current_month, "pay_year": current_year,
                            "collected_by": current_operator
                        }).execute()
                        st.rerun()
                else:
                    collector_label = row.get('collected_by') if row.get('collected_by') else "Admin"
                    r9.markdown(f"<span style='color:green; font-size:11px;'>By {collector_label}: {row['last_paid_date']}</span>", unsafe_allow_html=True)
                
                st.markdown("<hr style='margin: 0.2em 0px; opacity: 0.1;'>", unsafe_allow_html=True)

    with tab_areas:
        st.markdown('<div class="table-section-heading">📍 AREA WISE SECTOR FILTERS</div>', unsafe_allow_html=True)
        if not df_users.empty:
            areas = ["All Nodes"] + list(df_users['area'].unique())
            sel_area = st.selectbox("Isolate operational view by area zone:", areas)
            filtered = df_users if sel_area == "All Nodes" else df_users[df_users['area'] == sel_area]
            st.dataframe(filtered[['id', 'username', 'name', 'phone', 'area', 'status', 'expiry_date', 'collected_by']], use_container_width=True)

    if is_admin:
        with tab_history:
            st.markdown('<div class="table-section-heading">📚 TRANSACTION AUDIT REGISTER</div>', unsafe_allow_html=True)
            if not df_history.empty:
                st.dataframe(df_history[['name', 'area', 'amount', 'pay_date', 'collected_by', 'pay_month', 'pay_year']].sort_index(ascending=False), use_container_width=True)
            else: st.info("No commercial logs generated yet.")