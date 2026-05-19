import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="LYNX Fiber - Cloud Billing Portal", layout="wide", page_icon="⚡")

# --- SUPABASE SECURE CLOUD CONNECTION ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_supabase()

# Timing data variables
current_month = datetime.now().strftime("%B")
current_year = datetime.now().strftime("%Y")
today_date = datetime.now().strftime("%Y-%m-%d")

# --- SESSION STATE FOR LOGIN MANAGEMENT ---
if "isp_logged_in" not in st.session_state:
    st.session_state["isp_logged_in"] = False
if "isp_id" not in st.session_state:
    st.session_state["isp_id"] = None
if "isp_name" not in st.session_state:
    st.session_state["isp_name"] = ""

# --- PORTAL GATEWAY (LOGIN / SIGNUP SCREEN - WITH LYNX FIBER BRANDING) ---
if not st.session_state["isp_logged_in"]:
    
    _, col_center, _ = st.columns([1, 1.8, 1])
    
    with col_center:
        st.markdown("<br>", unsafe_allow_html=True)
        # Main top heading updated to LYNX Fiber
        st.markdown("<h1 style='text-align: center; color: #1E88E5; margin-bottom:0px;'>⚡ LYNX Fiber</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 16px; letter-spacing: 2px;'><b>CLOUD BILLING PLATFORM FOR INTERNET PROVIDERS</b></p>", unsafe_allow_html=True)
        
        # Tabs for Sign In and Register
        tab_login, tab_signup = st.tabs(["🔒 Sign In / Login", "📝 Register New ISP Account"])
        
        # --- TAB 1: LOGIN ---
        with tab_login:
            with st.form("isp_login_form"):
                st.markdown("<p style='text-align: center; color: gray;'>Enter your admin credentials to access your billing network</p>", unsafe_allow_html=True)
                login_user = st.text_input("👤 ISP Admin Username", placeholder="e.g., lynxadmin")
                login_pass = st.text_input("🔒 Password", type="password", placeholder="••••••••••••")
                btn_login = st.form_submit_button("Login to System", use_container_width=True)
                
                if btn_login:
                    if login_user and login_pass:
                        try:
                            # Dynamic Cloud authentication
                            res = supabase.table("isp_companies").select("*").eq("username", login_user).eq("password", login_pass).execute()
                            if len(res.data) > 0:
                                st.session_state["isp_logged_in"] = True
                                st.session_state["isp_id"] = res.data[0]["id"]
                                st.session_state["isp_name"] = res.data[0]["company_name"]
                                st.success(f"🔒 Access Granted! Welcome {st.session_state['isp_name']}")
                                st.rerun()
                            else:
                                st.error("❌ Galat Username ya Password! Dobara koshish karein.")
                        except Exception as e:
                            st.error(f"Connection Error: {e}")
                    else:
                        st.warning("⚠️ Dono khane bharna zaroori hain.")

        # --- TAB 2: SIGN UP (Branded under LYNX Fiber Platform) ---
        with tab_signup:
            with st.form("isp_signup_form"):
                # Branded text update here
                st.markdown("<p style='text-align: center; color: green;'>Apni Company ko LYNX Fiber Network par register karein</p>", unsafe_allow_html=True)
                new_isp_name = st.text_input("🏢 Company Name (e.g., Lynx Fiber Pvt Ltd)")
                new_isp_user = st.text_input("👤 Desired Admin Username (Unique)")
                new_isp_phone = st.text_input("📞 Phone / Contact Number")
                new_isp_pass = st.text_input("🔒 Set Login Password", type="password")
                btn_signup = st.form_submit_button("Create My Billing Portal", use_container_width=True)
                
                if btn_signup:
                    if new_isp_name and new_isp_user and new_isp_pass:
                        try:
                            signup_data = {
                                "company_name": new_isp_name,
                                "username": new_isp_user,
                                "password": new_isp_pass,
                                "phone": new_isp_phone
                            }
                            supabase.table("isp_companies").insert(signup_data).execute()
                            st.success("🎉 Account Created Successfully! Ab Sign In wale tab par ja kar login karein.")
                        except Exception:
                            st.error("❌ Yeh Username pehle se maujood hai! Koi naya username rukhain.")
                    else:
                        st.warning("⚠️ Meherbani karke saari details lazmi bharein.")
                        
        # Footer update to LYNX
        st.markdown("<p style='text-align: center; color: gray; font-size: 11px; margin-top: 20px;'>LYNX Fiber Cloud Infrastructure © 2026</p>", unsafe_allow_html=True)

# --- LIVE ISOLATED ISP DASHBOARD (AFTER LOGGED IN) ---
else:
    my_isp_id = st.session_state["isp_id"]
    my_isp_name = st.session_state["isp_name"]
    
    # Shows the specific ISP company name that logged in (e.g., Lynx Fiber or any other)
    st.title(f"⚡ {my_isp_name} - Control Panel")
    st.caption(f"Logged in securely | Powered by LYNX Fiber Core | Cycle: {current_month} {current_year}")
    st.markdown("---")
    
    if st.sidebar.button("🔒 Secure Logout", use_container_width=True):
        st.session_state["isp_logged_in"] = False
        st.session_state["isp_id"] = None
        st.session_state["isp_name"] = ""
        st.rerun()
        
    st.sidebar.header("➕ Customer Operations")

    # Sidebar: Add Customer
    with st.sidebar.expander("📝 Naya Customer Add Karein", expanded=True):
        with st.form("add_user_form", clear_on_submit=True):
            new_name = st.text_input("Customer Name")
            new_username = st.text_input("PPPoE / Router ID")
            new_phone = st.text_input("Phone Number")
            new_area = st.text_input("Area / Sector Colony")
            new_bill = st.number_input("Monthly Bill (Rs.)", min_value=0, step=100)
            submit_user = st.form_submit_button("Save Customer", use_container_width=True)
            
            if submit_user:
                if new_name and new_username and new_area and new_bill > 0:
                    try:
                        data = {
                            "isp_id": my_isp_id,
                            "name": new_name,
                            "username": new_username,
                            "phone": new_phone,
                            "area": new_area,
                            "monthly_bill": new_bill,
                            "status": "Unpaid"
                        }
                        supabase.table("billing_users").insert(data).execute()
                        st.success(f"✔️ {new_name} Save Ho Gaya!")
                        st.rerun()
                    except Exception:
                        st.error("❌ Error: Yeh Router ID aapke pass pehle se registered hai!")
                else:
                    st.warning("⚠️ Details mukammal bharein.")

    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 New Month Reset (Unpaid All)", use_container_width=True):
        try:
            supabase.table("billing_users").update({"status": "Unpaid"}).eq("isp_id", my_isp_id).execute()
            st.sidebar.success("Aapki company ke saray users ka status reset ho gaya!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Reset fail: {e}")

    # --- DATA FETCHING ---
    try:
        users_resp = supabase.table("billing_users").select("*").eq("isp_id", my_isp_id).order("name").execute()
        history_resp = supabase.table("billing_history").select("*").eq("isp_id", my_isp_id).execute()
        
        df_users = pd.DataFrame(users_resp.data)
        df_history = pd.DataFrame(history_resp.data)
    except Exception as e:
        df_users = pd.DataFrame()
        df_history = pd.DataFrame()

    if df_users.empty:
        st.info(f"👋 Setup Completed! Sidebar khol kar apne {my_isp_name} ke customers add karein.")
    else:
        total_users = len(df_users)
        paid_users = len(df_users[df_users['status'] == 'Paid'])
        unpaid_users = len(df_users[df_users['status'] == 'Unpaid'])
        
        if not df_history.empty:
            today_collection = df_history[df_history['pay_date'] == today_date]['amount'].sum()
            monthly_collection = df_history[(df_history['pay_month'] == current_month) & (df_history['pay_year'] == current_year)]['amount'].sum()
        else:
            today_collection = 0
            monthly_collection = 0

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("👥 Total Users", f"{total_users}")
        m2.metric("✅ Paid Users", f"{paid_users}", delta=f"{paid_users} Recovered")
        m3.metric("❌ Unpaid Users", f"{unpaid_users}", delta=f"-{unpaid_users} Remaining", delta_color="inverse")
        m4.metric("💰 Today's Cash", f"Rs. {today_collection:,.0f}")
        m5.metric(f"📅 Revenue ({current_month})", f"Rs. {monthly_collection:,.0f}")
        
        st.markdown("---")

        st.subheader("📍 Area Wise Sorting Panel")
        unique_areas = ["All Areas"] + list(df_users['area'].unique())
        selected_area = st.selectbox("Apna Sector/Area Select Karein:", unique_areas)
        
        filtered_df = df_users if selected_area == "All Areas" else df_users[df_users['area'] == selected_area]

        st.markdown("### 📋 Client Directory & Cash Collection")
        
        for index, row in filtered_df.iterrows():
            status_label = "🟢 Paid" if row['status'] == 'Paid' else "🔴 Unpaid"
            
            c1, c2, c3, c4, c5 = st.columns([2, 2, 1.5, 1.5, 1.5])
            c1.markdown(f"**{row['name']}** ({row['username']})")
            c2.markdown(f"📍 {row['area']} | 📞 {row['phone'] if row['phone'] else 'N/A'}")
            c3.markdown(f"💵 Bill: **Rs. {float(row['monthly_bill']):.0f}**")
            c4.markdown(f"Status: **{status_label}**")
            
            if row['status'] == 'Unpaid':
                if c5.button("Receive Bill 💵", key=f"pay_{row['id']}"):
                    supabase.table("billing_users").update({"status": "Paid", "last_paid_date": today_date}).eq("id", row['id']).execute()
                    
                    hist_data = {
                        "isp_id": my_isp_id,
                        "user_id": int(row['id']),
                        "name": row['name'],
                        "area": row['area'],
                        "amount": float(row['monthly_bill']),
                        "pay_date": today_date,
                        "pay_month": current_month,
                        "pay_year": current_year
                    }
                    supabase.table("billing_history").insert(hist_data).execute()
                    
                    st.success(f"💸 {row['name']} ka bill record ho gaya!")
                    st.rerun()
            else:
                c5.markdown(f"📆 Paid: `{row['last_paid_date']}`")
                
            st.markdown("<hr style='margin: 0.3em 0px; opacity: 0.2;'>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📚 Business Annual Ledger Logs")
        
        if not df_history.empty:
            t1, t2 = st.tabs(["📋 Detailed Log Sheet", "🗓️ Monthly Summary Overview"])
            with t1:
                st.dataframe(df_history[['name', 'area', 'amount', 'pay_date', 'pay_month', 'pay_year']].sort_index(ascending=False), use_container_width=True)
            with t2:
                summary_df = df_history.groupby(['pay_year', 'pay_month'])['amount'].sum().reset_index()
                summary_df.columns = ['Year', 'Month', 'Total Collection (Rs.)']
                st.table(summary_df)