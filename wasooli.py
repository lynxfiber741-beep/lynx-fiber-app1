import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- DITTO WASOOLI PK THEME ENGINE (CSS INJECTION) ---
st.set_page_config(page_title="LYNX Fiber - Advanced ISP Portal", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    .block-container { padding-top: 0px; padding-bottom: 0px; max-width: 100% !important; background-color: #f8fafc; }
    [data-testid="stHeader"] { display: none; }
    
    /* Wasooli PK Exact Top Blue Ribbon Header Bar */
    .wasooli-header {
        background-color: #0284c7 !important; color: white !important; padding: 15px 40px;
        display: flex; justify-content: space-between; align-items: center;
        width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw;
        font-family: 'Arial', sans-serif; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-bottom: 3px solid #0369a1;
    }
    .wasooli-brand { font-size: 24px; font-weight: bold; letter-spacing: 0.5px; }
    .wasooli-role-badge { background-color: white; color: #0284c7; padding: 6px 16px; border-radius: 4px; font-weight: bold; font-size: 13px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.2); }
    
    .action-row { display: flex; gap: 12px; margin-top: 20px; margin-bottom: 25px; flex-wrap: wrap; }
    .action-card-btn {
        background: linear-gradient(135deg, #0284c7, #0369a1); color: white; border: none;
        padding: 12px 24px; border-radius: 4px; font-size: 14px; font-weight: bold;
        text-align: center; cursor: pointer; flex: 1; min-width: 180px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-box-container { display: flex; gap: 20px; margin-bottom: 25px; }
    .metric-box { background: white; padding: 15px 25px; border-radius: 6px; border: 1px solid #e2e8f0; border-top: 4px solid #0284c7; flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .metric-box-title { color: #64748b; font-size: 13px; font-weight: bold; text-transform: uppercase; }
    .metric-box-value { color: #0f172a; font-size: 28px; font-weight: bold; margin-top: 5px; }
    
    .table-section-heading { color: #0284c7 !important; font-size: 20px; font-weight: bold; margin-top: 20px; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE CONFIG ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_supabase()

# Timing Core Variables
current_month = datetime.now().strftime("%B")
current_year = datetime.now().strftime("%Y")
today_date = datetime.now().strftime("%Y-%m-%d")
MASTER_APPROVAL_CODE = "LYNX-SECURE-2026"

# Advanced Multi-Role Session Management
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None  # 'Admin' ya 'Staff'
if "isp_id" not in st.session_state: st.session_state["isp_id"] = None
if "isp_name" not in st.session_state: st.session_state["isp_name"] = ""
if "operator_name" not in st.session_state: st.session_state["operator_name"] = ""
if "branding_mode" not in st.session_state: st.session_state["branding_mode"] = "Lynx Branding"

# --- TOP PRO HEADER CONTROLLER ---
if st.session_state["logged_in"]:
    display_title = st.session_state["isp_name"].upper() if st.session_state["branding_mode"] == "Own Branding" else "LYNX FIBER"
    role_text = f"👤 {st.session_state['operator_name'].upper()} ({st.session_state['user_role'].upper()})"
    st.markdown(f'<div class="wasooli-header"><div class="wasooli-brand">🌐 HELLO!! {display_title}</div><div class="wasooli-role-badge">{role_text}</div></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="wasooli-header"><div class="wasooli-brand">⚡ LYNX FIBER ADVANCED SYSTEM</div><div class="wasooli-role-badge">🔒 ACCESS SECURED</div></div>', unsafe_allow_html=True)

# --- AUTHENTICATION GATEWAY WITH ROLE MANAGEMENT ---
if not st.session_state["logged_in"]:
    _, col_center, _ = st.columns([1, 1.8, 1])
    with col_center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        tab_staff, tab_admin, tab_register = st.tabs(["📲 Field Staff Login", "🔒 Owner/Admin Gate", "📝 Corporate Signup"])
        
        # TAB 1: FIELD STAFF GATEWAY
        with tab_staff:
            with st.form("staff_login_form"):
                st.caption("Field boys billing aur recovery receive karne ke liye yahan se login karein:")
                s_user = st.text_input("Staff Username ID")
                s_pass = st.text_input("Staff Password", type="password")
                if st.form_submit_button("Enter Field Dashboard", use_container_width=True):
                    res = supabase.table("isp_staff").select("*, isp_companies(company_name, branding_mode)").eq("username", s_user).eq("password", s_pass).execute()
                    if len(res.data) > 0:
                        st.session_state["logged_in"] = True
                        st.session_state["user_role"] = "Staff"
                        st.session_state["isp_id"] = res.data[0]["isp_id"]
                        st.session_state["operator_name"] = res.data[0]["staff_name"]
                        st.session_state["isp_name"] = res.data[0]["isp_companies"]["company_name"]
                        st.session_state["branding_mode"] = res.data[0]["isp_companies"].get("branding_mode", "Lynx Branding")
                        st.rerun()
                    else:
                        st.error("❌ Staff Username ya Password galat hai!")

        # TAB 2: OWNER ADMIN GATEWAY
        with tab_admin:
            with st.form("admin_login_form"):
                st.caption("Main ISP Owner (Master Access Control) login gateway:")
                a_user = st.text_input("Master Username")
                a_pass = st.text_input("Master Password", type="password")
                if st.form_submit_button("Authenticate Master Engine", use_container_width=True):
                    res = supabase.table("isp_companies").select("*").eq("username", a_user).eq("password", a_pass).execute()
                    if len(res.data) > 0:
                        st.session_state["logged_in"] = True
                        st.session_state["user_role"] = "Admin"
                        st.session_state["isp_id"] = res.data[0]["id"]
                        st.session_state["operator_name"] = "Admin"
                        st.session_state["isp_name"] = res.data[0]["company_name"]
                        st.session_state["branding_mode"] = res.data[0].get("branding_mode", "Lynx Branding")
                        st.rerun()
                    else:
                        st.error("❌ Owner credentials incorrect!")

        # TAB 3: SIGNUP
        with tab_register:
            st.info("📢 Helplines for Master Keys: 0331-5336673 | 0321-5943786")
            with st.form("signup_master_form"):
                r_company = st.text_input("Company Corporate Name")
                r_user = st.text_input("Desired Admin Username")
                r_phone = st.text_input("Official Phone No")
                r_pass = st.text_input("Set Password", type="password")
                r_brand = st.selectbox("Branding Mode Pack", ["Lynx Branding", "Own Branding"])
                r_key = st.text_input("Master Activation Code", type="password")
                if st.form_submit_button("Register & Deploy Network", use_container_width=True):
                    if r_key != MASTER_APPROVAL_CODE:
                        st.error("❌ Secure license registration key wrong.")
                    else:
                        supabase.table("isp_companies").insert({
                            "company_name": r_company, "username": r_user, "password": r_pass, "phone": r_phone, "branding_mode": r_brand
                        }).execute()
                        st.success("🎉 Registry Complete! Log in via Admin Gate.")

# --- LIVE INTERFACE (ROLES-ISOLATED ENVIRONMENT) ---
else:
    my_isp_id = st.session_state["isp_id"]
    is_admin = (st.session_state["user_role"] == "Admin")
    
    # 1. Action Matrix Row Design
    st.markdown("""
    <div class="action-row">
        <div class="action-card-btn">User/Dealer Application</div>
        <div class="action-card-btn">BT Drivers</div>
        <div class="action-card-btn">Copy Query Link</div>
        <div class="action-card-btn">Download Bill</div>
        <div class="action-card-btn">Download Application</div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- SIDEBAR ACCESS MANAGEMENT ---
    st.sidebar.markdown(f"### Mode: `{st.session_state['user_role']}` Control Panel")
    if st.sidebar.button("🔒 Secure Logout", use_container_width=True):
        st.session_state["logged_in"] = False
        st.rerun()
        
    # BOTH ADMIN & STAFF CAN ADD CUSTOMERS (Field requirement)
    with st.sidebar.expander("➕ Register New Customer Node", expanded=True):
        with st.form("add_user_form", clear_on_submit=True):
            n_name = st.text_input("Customer Full Name")
            n_user = st.text_input("PPPoE / Router User ID")
            n_phone = st.text_input("Phone Number")
            n_area = st.text_input("Area Sector / Colony Location")
            n_prev = st.number_input("Previous Balance / Dues (Rs.)", min_value=0, step=50)
            n_bill = st.number_input("Current Monthly Package Bill (Rs.)", min_value=0, step=100)
            if st.form_submit_button("Save Customer Account", use_container_width=True):
                if n_name and n_user and n_area and n_bill > 0:
                    supabase.table("billing_users").insert({
                        "isp_id": my_isp_id, "name": n_name, "username": n_user, "phone": n_phone,
                        "area": n_area, "previous_balance": n_prev, "current_bill": n_bill, "status": "Unpaid"
                    }).execute()
                    st.rerun()

    # ONLY ADMIN CAN REGISTER STAFF MEMBERS (LADKON KE ACCOUNT BANANA)
    if is_admin:
        with st.sidebar.expander("👥 Create Staff/Boy Accounts", expanded=False):
            with st.form("create_staff_form", clear_on_submit=True):
                st.caption("Field boys ke liye alag username aur password yahan se banayein:")
                st_name = st.text_input("Boy Full Name (e.g., Ali)")
                st_user = st.text_input("Login Username ID (Unique)")
                st_pass = st.text_input("Login Password")
                if st.form_submit_button("Authorize Staff Member"):
                    if st_name and st_user and st_pass:
                        try:
                            supabase.table("isp_staff").insert({
                                "isp_id": my_isp_id, "staff_name": st_name, "username": st_user, "password": st_pass
                            }).execute()
                            st.sidebar.success(f"✔️ Account created for {st_name}!")
                        except:
                            st.sidebar.error("❌ Username already taken.")

        # ONLY ADMIN CAN RESET MONTHLY CYCLES
        st.sidebar.markdown("---")
        if st.sidebar.button("🔄 Execute Month Reset (Roll Forward Bills)", use_container_width=True):
            users_raw = supabase.table("billing_users").select("*").eq("isp_id", my_isp_id).execute()
            for u in users_raw.data:
                new_prev = float(u["previous_balance"]) + float(u["current_bill"]) if u["status"] == "Unpaid" else 0
                supabase.table("billing_users").update({"previous_balance": new_prev, "status": "Unpaid"}).eq("id", u["id"]).execute()
            st.sidebar.success("New Billing cycle advanced successfully!")
            st.rerun()

    # --- MAIN VIEW INTERFACE HOOKS ---
    users_resp = supabase.table("billing_users").select("*").eq("isp_id", my_isp_id).order("name").execute()
    history_resp = supabase.table("billing_history").select("*").eq("isp_id", my_isp_id).execute()
    df_users = pd.DataFrame(users_resp.data)
    df_history = pd.DataFrame(history_resp.data)

    # SECURE TABS CONFIGURATION
    if is_admin:
        tab_summary, tab_areas, tab_history = st.tabs(["📊 Main Billing Directory", "📍 Area Grid Analytics", "📚 Annual Financial Ledgers"])
    else:
        # STAFF CANNOT SEE SYSTEM FINANCIAL AUDIT LEDGERS
        tab_summary, tab_areas = st.tabs(["📊 Main Billing Directory", "📍 Area Grid Analytics"])

    with tab_summary:
        if df_users.empty:
            st.info("No active subscriber entries. Add records via sidebar panel.")
        else:
            total_nodes = len(df_users)
            paid_nodes = len(df_users[df_users['status'] == 'Paid'])
            unpaid_nodes = len(df_users[df_users['status'] == 'Unpaid'])
            
            # Metrics Counters
            st.markdown(f"""
            <div class="metric-box-container">
                <div class="metric-box"><div class="metric-box-title">👥 Active Subscriber Nodes</div><div class="metric-box-value">{total_nodes}</div></div>
                <div class="metric-box"><div class="metric-box-title">🟢 Settled Invoices (Paid)</div><div class="metric-box-value" style="color: #16a34a;">{paid_nodes}</div></div>
                <div class="metric-box"><div class="metric-box-title">🔴 Outstanding Collections (Unpaid)</div><div class="metric-box-value" style="color: #dc2626;">{unpaid_nodes}</div></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="table-section-heading">📋 CUSTOMER BILLING MATRIX</div>', unsafe_allow_html=True)
            
            # Table Row Layout Matching Wasooli PK mockup
            ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9 = st.columns([0.6, 1.2, 1.5, 1.1, 1.1, 0.9, 0.9, 0.9, 1.3])
            ch1.markdown("**CustID**")
            ch2.markdown("**Internet ID**")
            ch3.markdown("**Subscriber Name**")
            ch4.markdown("**Contact No**")
            ch5.markdown("**Area Sector**")
            ch6.markdown("**Previous**")
            ch7.markdown("**Current**")
            ch8.markdown("**Total Due**")
            ch9.markdown("**Action Panel**")
            st.markdown("<hr style='margin: 0.5em 0px; border-top: 2px solid #0284c7;'>", unsafe_allow_html=True)
            
            for index, row in df_users.iterrows():
                prev_val = float(row['previous_balance'])
                curr_val = float(row['current_bill'])
                total_due = prev_val + curr_val if row['status'] == 'Unpaid' else 0.0
                
                status_color = "green" if row['status'] == 'Paid' else "red"
                
                r1, r2, r3, r4, r5, r6, r7, r8, r9 = st.columns([0.6, 1.2, 1.5, 1.1, 1.1, 0.9, 0.9, 0.9, 1.3])
                r1.write(f"#{row['id']}")
                r2.write(row['username'])
                r3.write(row['name'])
                r4.write(row['phone'] if row['phone'] else "N/A")
                r5.write(row['area'])
                r6.write(f"{prev_val:,.0f}")
                r7.write(f"{curr_val:,.0f}")
                r8.markdown(f"<b style='color:{status_color};'>{total_due:,.0f}</b>", unsafe_allow_html=True)
                
                if row['status'] == 'Unpaid':
                    if r9.button("Receive Bill 💵", key=f"rec_{row['id']}", use_container_width=True):
                        # Executing collection process pipeline
                        supabase.table("billing_users").update({"status": "Paid", "last_paid_date": today_date}).eq("id", row['id']).execute()
                        supabase.table("billing_history").insert({
                            "isp_id": my_isp_id, "user_id": int(row['id']), "name": row['name'], "area": row['area'],
                            "amount": total_due, "pay_date": today_date, "pay_month": current_month, "pay_year": current_year
                        }).execute()
                        st.rerun()
                else:
                    r9.markdown(f"<span style='color:green; font-size:12px;'>Settle: {row['last_paid_date']}</span>", unsafe_allow_html=True)
                
                st.markdown("<hr style='margin: 0.2em 0px; opacity: 0.1;'>", unsafe_allow_html=True)

    with tab_areas:
        st.markdown('<div class="table-section-heading">📍 AREA WISE SECTOR FILTERS</div>', unsafe_allow_html=True)
        if not df_users.empty:
            areas = ["All Nodes"] + list(df_users['area'].unique())
            sel_area = st.selectbox("Isolate operational view by area zone:", areas)
            filtered = df_users if sel_area == "All Nodes" else df_users[df_users['area'] == sel_area]
            st.dataframe(filtered[['id', 'username', 'name', 'phone', 'area', 'status']], use_container_width=True)

    if is_admin:
        with tab_history:
            st.markdown('<div class="table-section-heading">📚 FISCAL YEAR TRANSACTION AUDIT REGISTER (MASTER ONLY)</div>', unsafe_allow_html=True)
            if not df_history.empty:
                st.dataframe(df_history[['name', 'area', 'amount', 'pay_date', 'pay_month', 'pay_year']].sort_index(ascending=False), use_container_width=True)
            else:
                st.info("No commercial transactions logged yet.")