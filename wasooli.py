import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- WZ-WASOOLI PK CUSTOM CSS INJECTION ---
# Forcing the exact look, color codes (#0284c7), and clean tabular styling of Wasooli PK
st.set_page_config(page_title="LYNX Fiber - Management Portal", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    /* Hide Streamlit default paddings */
    .block-container { padding-top: 0px; padding-bottom: 0px; max-width: 100% !important; }
    [data-testid="stHeader"] { display: none; }
    
    /* Wasooli PK Top Main Blue Header Bar */
    .wasooli-top-bar {
        background-color: #0284c7 !important;
        color: white !important;
        padding: 12px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100vw;
        position: relative;
        left: 50%; right: 50%;
        margin-left: -50vw; margin-right: -50vw;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
    }
    .wasooli-brand { font-size: 22px; font-weight: bold; letter-spacing: 1px; display: flex; align-items: center; gap: 10px; }
    .wasooli-user-badge { background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 4px; font-size: 14px; font-weight: bold; }
    
    /* Custom Blue Action Buttons Row */
    .wasooli-btn-row { display: flex; gap: 10px; margin-top: 15px; margin-bottom: 20px; flex-wrap: wrap; }
    .wasooli-btn { 
        background-color: #0284c7; color: white; border: none; padding: 10px 20px; 
        border-radius: 4px; font-size: 14px; font-weight: 500; text-align: center; cursor: pointer; flex: 1; min-width: 150px;
    }
    
    /* Professional Data Table Styling */
    .wasooli-table { width: 100%; border-collapse: collapse; margin-top: 15px; background: white; color: #333; }
    .wasooli-table th { background-color: #f8fafc; color: #475569; padding: 12px; border-bottom: 2px solid #cbd5e1; font-weight: 600; text-align: left; }
    .wasooli-table td { padding: 12px; border-bottom: 1px solid #e2e8f0; font-size: 14px; }
    .wasooli-table tr:hover { background-color: #f1f5f9; }
    
    /* Status Badges */
    .badge-paid { background-color: #22c55e; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-unpaid { background-color: #ef4444; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- SUPABASE SECURE CLOUD CONNECTION ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_supabase()

# Timing Variables
current_month = datetime.now().strftime("%B")
current_year = datetime.now().strftime("%Y")
today_date = datetime.now().strftime("%Y-%m-%d")

# Master Key
MASTER_APPROVAL_CODE = "LYNX-SECURE-2026"

# Session Management
if "isp_logged_in" not in st.session_state: st.session_state["isp_logged_in"] = False
if "isp_id" not in st.session_state: st.session_state["isp_id"] = None
if "isp_name" not in st.session_state: st.session_state["isp_name"] = ""
if "branding_mode" not in st.session_state: st.session_state["branding_mode"] = "Lynx Branding"

# --- RENDER VENDOR BRANDED TOP BAR ---
if st.session_state["isp_logged_in"]:
    header_title = st.session_state["isp_name"].upper() if st.session_state["branding_mode"] == "Own Branding" else "LYNX FIBER INTERNET"
    user_display = st.session_state["isp_name"].replace(" ", "").upper()
    
    st.markdown(f"""
    <div class="wasooli-top-bar">
        <div class="wasooli-brand">🌐 HELLO!! {header_title}</div>
        <div class="wasooli-user-badge">👤 {user_display}ADMIN</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="wasooli-top-bar">
        <div class="wasooli-brand">⚡ LYNX FIBER CORE SYSTEM</div>
        <div class="wasooli-user-badge">🔒 SECURE GATEWAY</div>
    </div>
    """, unsafe_allow_html=True)

# --- PORTAL GATEWAY (LOGIN / SIGNUP SCREEN) ---
if not st.session_state["isp_logged_in"]:
    _, col_center, _ = st.columns([1, 1.8, 1])
    with col_center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["🔒 Sign In / Login", "📝 Register New ISP Account"])
        
        with tab_login:
            with st.form("isp_login_form"):
                login_user = st.text_input("👤 ISP Admin Username")
                login_pass = st.text_input("🔒 Password", type="password")
                if st.form_submit_button("Login to Portal", use_container_width=True):
                    res = supabase.table("isp_companies").select("*").eq("username", login_user).eq("password", login_pass).execute()
                    if len(res.data) > 0:
                        st.session_state["isp_logged_in"] = True
                        st.session_state["isp_id"] = res.data[0]["id"]
                        st.session_state["isp_name"] = res.data[0]["company_name"]
                        st.session_state["branding_mode"] = res.data[0].get("branding_mode", "Lynx Branding")
                        st.rerun()
                    else:
                        st.error("❌ Galat Username ya Password!")

        with tab_signup:
            st.info("📢 **Notice:** Activation ke liye LYNX Admin se rabta karein.\n📞 **0331-5336673 | 0321-5943786**")
            with st.form("isp_signup_form"):
                new_isp_name = st.text_input("🏢 Company Name")
                new_isp_user = st.text_input("👤 Desired Admin Username")
                new_isp_phone = st.text_input("📞 Phone Number")
                new_isp_pass = st.text_input("🔒 Set Password", type="password")
                selected_branding = st.selectbox("🎯 Select Application Branding Mode", ["Lynx Branding", "Own Branding"])
                input_approval_code = st.text_input("🔑 Admin Approval Code", type="password")
                
                if st.form_submit_button("Create My Billing Portal", use_container_width=True):
                    if input_approval_code != MASTER_APPROVAL_CODE:
                        st.error("❌ Invalid Code!")
                    else:
                        try:
                            supabase.table("isp_companies").insert({
                                "company_name": new_isp_name, "username": new_isp_user,
                                "password": new_isp_pass, "phone": new_isp_phone, "branding_mode": selected_branding
                            }).execute()
                            st.success("🎉 Registered! Ab login karein.")
                        except:
                            st.error("❌ Username already exists.")

# --- LIVE DASHBOARD (DITTO WASOOLI PK SCREEN FLOW) ---
else:
    my_isp_id = st.session_state["isp_id"]
    
    # Render Action Grid Row
    st.markdown("""
    <div class="wasooli-btn-row">
        <div class="wasooli-btn">User/Dealer Application</div>
        <div class="wasooli-btn">BT Drivers</div>
        <div class="wasooli-btn">Copy Query Link</div>
        <div class="wasooli-btn">Download Bill</div>
        <div class="wasooli-btn">Download Application</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Operations
    if st.sidebar.button("🔒 Secure Logout", use_container_width=True):
        st.session_state["isp_logged_in"] = False
        st.rerun()
        
    with st.sidebar.expander("➕ Naya Customer Add Karein", expanded=True):
        with st.form("add_user_form", clear_on_submit=True):
            n_name = st.text_input("Customer Name")
            n_user = st.text_input("PPPoE / Router ID")
            n_phone = st.text_input("Phone Number")
            n_area = st.text_input("Area / Sector Colony")
            n_bill = st.number_input("Monthly Bill (Rs.)", min_value=0, step=100)
            if st.form_submit_button("Save Customer"):
                if n_name and n_user and n_area and n_bill > 0:
                    supabase.table("billing_users").insert({
                        "isp_id": my_isp_id, "name": n_name, "username": n_user,
                        "phone": n_phone, "area": n_area, "monthly_bill": n_bill, "status": "Unpaid"
                    }).execute()
                    st.rerun()

    if st.sidebar.button("🔄 New Month Reset (Unpaid All)", use_container_width=True):
        supabase.table("billing_users").update({"status": "Unpaid"}).eq("isp_id", my_isp_id).execute()
        st.rerun()

    # Data Tabs Configuration
    tab_summary, tab_today, tab_complains, tab_areas = st.tabs([
        "📊 Summary Grid", "💰 Today's Collection", "🛠️ Complain Management", "📍 Area Wise Sorting"
    ])
    
    # Fetch Data
    users_resp = supabase.table("billing_users").select("*").eq("isp_id", my_isp_id).order("name").execute()
    history_resp = supabase.table("billing_history").select("*").eq("isp_id", my_isp_id).execute()
    df_users = pd.DataFrame(users_resp.data)
    df_history = pd.DataFrame(history_resp.data)
    
    with tab_summary:
        if df_users.empty:
            st.info("No data available in table. Sidebar se naye customers add karein.")
        else:
            total = len(df_users)
            paid = len(df_users[df_users['status'] == 'Paid'])
            unpaid = len(df_users[df_users['status'] == 'Unpaid'])
            
            # Metrics Row
            m1, m2, m3 = st.columns(3)
            m1.metric("👥 Total Users", total)
            m2.metric("✅ Paid Users", paid)
            m3.metric("❌ Unpaid Users", unpaid)
            
            st.markdown("---")
            st.markdown("### 📋 Main Directory & Active Billing Records")
            
            # Rendering Table Structure exactly like Wasooli PK
            table_html = """
            <table class="wasooli-table">
                <thead>
                    <tr>
                        <th>CustID</th>
                        <th>Internet ID (Router)</th>
                        <th>Name</th>
                        <th>Contact No</th>
                        <th>Area / Sector</th>
                        <th>Monthly Bill</th>
                        <th>Status</th>
                        <th>Action / Collection</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            st.markdown(table_html, unsafe_allow_html=True)
            
            # Loop through dataframe and print row inputs
            for index, row in df_users.iterrows():
                badge = f'<span class="badge-paid">🟢 Paid</span>' if row['status'] == 'Paid' else f'<span class="badge-unpaid">🔴 Unpaid</span>'
                
                c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([0.8, 1.5, 1.5, 1.2, 1.2, 1.0, 1.0, 1.5])
                c1.write(f"#{row['id']}")
                c2.write(row['username'])
                c3.write(row['name'])
                c4.write(row['phone'] if row['phone'] else "N/A")
                c5.write(row['area'])
                c6.write(f"Rs. {float(row['monthly_bill']):.0f}")
                c7.markdown(badge, unsafe_allow_html=True)
                
                if row['status'] == 'Unpaid':
                    if c8.button("Receive Bill 💵", key=f"pay_{row['id']}", use_container_width=True):
                        supabase.table("billing_users").update({"status": "Paid", "last_paid_date": today_date}).eq("id", row['id']).execute()
                        supabase.table("billing_history").insert({
                            "isp_id": my_isp_id, "user_id": int(row['id']), "name": row['name'],
                            "area": row['area'], "amount": float(row['monthly_bill']),
                            "pay_date": today_date, "pay_month": current_month, "pay_year": current_year
                        }).execute()
                        st.rerun()
                else:
                    c8.write(f"📆 {row['last_paid_date']}")
                    
                st.markdown("<hr style='margin: 0.2em 0px; opacity: 0.1;'>", unsafe_allow_html=True)