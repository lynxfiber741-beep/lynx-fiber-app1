Python
import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
import bcrypt
import re

# =========================================================
# ⚡ LYNX FIBER ADVANCED ISP CRM SYSTEM (SECURE VERSION)
# =========================================================

st.set_page_config(
    page_title="LYNX Fiber - Advanced ISP Portal",
    layout="wide",
    page_icon="⚡"
)

# =========================================================
# 🎨 PREMIUM UI ENGINE
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 0px;
    padding-bottom: 0px;
    max-width: 100% !important;
    background-color: #f8fafc;
}

[data-testid="stHeader"] {
    display: none;
}

.wasooli-header {
    background-color: #0284c7 !important;
    color: white !important;
    padding: 15px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100vw;
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
    font-family: Arial, sans-serif;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    border-bottom: 3px solid #0369a1;
}

.wasooli-brand {
    font-size: 24px;
    font-weight: bold;
}

.wasooli-role-badge {
    background-color: white;
    color: #0284c7;
    padding: 6px 16px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 13px;
}

.action-row {
    display: flex;
    gap: 12px;
    margin-top: 20px;
    margin-bottom: 25px;
    flex-wrap: wrap;
}

.action-card-btn {
    background: linear-gradient(135deg, #0284c7, #0369a1);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 4px;
    font-size: 14px;
    font-weight: bold;
    text-align: center;
    flex: 1;
    min-width: 180px;
}

.metric-box-container {
    display: flex;
    gap: 20px;
    margin-bottom: 25px;
}

.metric-box {
    background: white;
    padding: 15px 25px;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    border-top: 4px solid #0284c7;
    flex: 1;
}

.metric-box-title {
    color: #64748b;
    font-size: 13px;
    font-weight: bold;
}

.metric-box-value {
    color: #0f172a;
    font-size: 28px;
    font-weight: bold;
    margin-top: 5px;
}

.table-section-heading {
    color: #0284c7 !important;
    font-size: 20px;
    font-weight: bold;
    margin-top: 20px;
    margin-bottom: 15px;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 5px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# 🔐 DATABASE CONFIG
# =========================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
MASTER_APPROVAL_CODE = st.secrets["MASTER_APPROVAL_CODE"]

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_supabase()

# =========================================================
# 📅 GLOBAL VARIABLES
# =========================================================

current_month = datetime.now().strftime("%B")
current_year = datetime.now().strftime("%Y")
today_date = datetime.now().strftime("%Y-%m-%d")

# =========================================================
# 🔐 SESSION ENGINE
# =========================================================

default_sessions = {
    "logged_in": False,
    "user_role": None,
    "isp_id": None,
    "isp_name": "",
    "operator_name": "",
    "branding_mode": "Lynx Branding"
}

for key, value in default_sessions.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# 🔒 SECURITY FUNCTIONS
# =========================================================

def hash_password(password):
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

def verify_password(input_password, hashed_password):
    return bcrypt.checkpw(
        input_password.encode(),
        hashed_password.encode()
    )

def validate_phone(phone):
    pattern = r'^[0-9]{11}$'
    return re.match(pattern, phone)

def secure_logout():
    keys = list(st.session_state.keys())
    for key in keys:
        del st.session_state[key]

    st.rerun()

# =========================================================
# 🌐 TOP HEADER
# =========================================================

if st.session_state["logged_in"]:

    display_title = (
        st.session_state["isp_name"].upper()
        if st.session_state["branding_mode"] == "Own Branding"
        else "LYNX FIBER INTERNET"
    )

    role_text = f"👤 {st.session_state['operator_name']} ({st.session_state['user_role']})"

    st.markdown(f"""
    <div class="wasooli-header">
        <div class="wasooli-brand">
            🌐 HELLO!! {display_title}
        </div>

        <div class="wasooli-role-badge">
            {role_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

else:

    st.markdown("""
    <div class="wasooli-header">
        <div class="wasooli-brand">
            ⚡ LYNX FIBER ADVANCED SYSTEM
        </div>

        <div class="wasooli-role-badge">
            🔒 ACCESS SECURED
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# 🔐 AUTHENTICATION
# =========================================================

if not st.session_state["logged_in"]:

    _, col_center, _ = st.columns([1, 1.8, 1])

    with col_center:

        st.markdown("<br><br>", unsafe_allow_html=True)

        tab_staff, tab_admin, tab_register = st.tabs([
            "📲 Staff Login",
            "🔒 Admin Login",
            "📝 Register ISP"
        ])

        # =================================================
        # 👨‍🔧 STAFF LOGIN
        # =================================================

        with tab_staff:

            with st.form("staff_login_form"):

                s_user = st.text_input("Staff Username")
                s_pass = st.text_input("Password", type="password")

                if st.form_submit_button("Login Staff"):

                    try:

                        res = supabase.table("isp_staff") \
                            .select("*, isp_companies(company_name, branding_mode)") \
                            .eq("username", s_user) \
                            .execute()

                        if len(res.data) > 0:

                            user_data = res.data[0]

                            if verify_password(
                                s_pass,
                                user_data["password"]
                            ):

                                st.session_state["logged_in"] = True
                                st.session_state["user_role"] = "Staff"
                                st.session_state["isp_id"] = user_data["isp_id"]
                                st.session_state["operator_name"] = user_data["staff_name"]
                                st.session_state["isp_name"] = user_data["isp_companies"]["company_name"]
                                st.session_state["branding_mode"] = user_data["isp_companies"]["branding_mode"]

                                st.rerun()

                            else:
                                st.error("❌ Invalid password")

                        else:
                            st.error("❌ User not found")

                    except Exception as e:
                        st.error(f"Database Error: {e}")

        # =================================================
        # 👑 ADMIN LOGIN
        # =================================================

        with tab_admin:

            with st.form("admin_login_form"):

                a_user = st.text_input("Admin Username")
                a_pass = st.text_input("Admin Password", type="password")

                if st.form_submit_button("Login Admin"):

                    try:

                        res = supabase.table("isp_companies") \
                            .select("*") \
                            .eq("username", a_user) \
                            .execute()

                        if len(res.data) > 0:

                            admin_data = res.data[0]

                            if verify_password(
                                a_pass,
                                admin_data["password"]
                            ):

                                st.session_state["logged_in"] = True
                                st.session_state["user_role"] = "Admin"
                                st.session_state["isp_id"] = admin_data["id"]
                                st.session_state["operator_name"] = "Admin"
                                st.session_state["isp_name"] = admin_data["company_name"]
                                st.session_state["branding_mode"] = admin_data["branding_mode"]

                                st.rerun()

                            else:
                                st.error("❌ Invalid password")

                        else:
                            st.error("❌ Admin not found")

                    except Exception as e:
                        st.error(f"Database Error: {e}")

        # =================================================
        # 📝 ISP REGISTRATION
        # =================================================

        with tab_register:

            st.info("📞 Support: 0331-5336673")

            with st.form("signup_form"):

                r_company = st.text_input("Company Name")
                r_user = st.text_input("Admin Username")
                r_phone = st.text_input("Phone Number")
                r_pass = st.text_input("Password", type="password")

                r_brand = st.selectbox(
                    "Branding Mode",
                    ["Lynx Branding", "Own Branding"]
                )

                r_key = st.text_input(
                    "Activation Code",
                    type="password"
                )

                if st.form_submit_button("Register ISP"):

                    if not all([
                        r_company,
                        r_user,
                        r_phone,
                        r_pass,
                        r_key
                    ]):
                        st.error("❌ Fill all fields")

                    elif not validate_phone(r_phone):
                        st.error("❌ Invalid phone number")

                    elif r_key != MASTER_APPROVAL_CODE:
                        st.error("❌ Invalid activation code")

                    else:

                        try:

                            check_user = supabase.table("isp_companies") \
                                .select("id") \
                                .eq("username", r_user) \
                                .execute()

                            if len(check_user.data) > 0:
                                st.error("❌ Username already taken")

                            else:

                                secure_password = hash_password(r_pass)

                                supabase.table("isp_companies").insert({
                                    "company_name": r_company,
                                    "username": r_user,
                                    "password": secure_password,
                                    "phone": r_phone,
                                    "branding_mode": r_brand
                                }).execute()

                                st.success("🎉 ISP Registered Successfully")

                        except Exception as e:
                            st.error(f"Registration Error: {e}")

# =========================================================
# 🚀 MAIN SYSTEM
# =========================================================

else:

    my_isp_id = st.session_state["isp_id"]
    is_admin = st.session_state["user_role"] == "Admin"
    current_operator = st.session_state["operator_name"]

    # =====================================================
    # 🎛️ TOP ACTION BUTTONS
    # =====================================================

    st.markdown("""
    <div class="action-row">

        <div class="action-card-btn">
            User Registration
        </div>

        <div class="action-card-btn">
            Download Bills
        </div>

        <div class="action-card-btn">
            WhatsApp Notices
        </div>

        <div class="action-card-btn">
            Payment Receipts
        </div>

    </div>
    """, unsafe_allow_html=True)

    # =====================================================
    # 📌 SIDEBAR
    # =====================================================

    st.sidebar.markdown(
        f"### Logged in as: `{st.session_state['user_role']}`"
    )

    if st.sidebar.button(
        "🔒 Logout",
        use_container_width=True
    ):
        secure_logout()

    # =====================================================
    # ➕ ADD CUSTOMER
    # =====================================================

    with st.sidebar.expander(
        "➕ Add Customer",
        expanded=True
    ):

        with st.form(
            "add_customer_form",
            clear_on_submit=True
        ):

            n_name = st.text_input("Customer Name")
            n_user = st.text_input("PPPoE Username")
            n_phone = st.text_input("Phone")
            n_area = st.text_input("Area")

            n_prev = st.number_input(
                "Previous Balance",
                min_value=0,
                step=100
            )

            n_bill = st.number_input(
                "Monthly Bill",
                min_value=0,
                step=100
            )

            if st.form_submit_button(
                "Save Customer",
                use_container_width=True
            ):

                if not all([
                    n_name,
                    n_user,
                    n_phone,
                    n_area
                ]):
                    st.error("❌ Fill all fields")

                elif not validate_phone(n_phone):
                    st.error("❌ Invalid phone number")

                elif n_bill <= 0:
                    st.error("❌ Invalid bill amount")

                else:

                    try:

                        supabase.table("billing_users").insert({

                            "isp_id": my_isp_id,
                            "name": n_name,
                            "username": n_user,
                            "phone": n_phone,
                            "area": n_area,
                            "previous_balance": n_prev,
                            "current_bill": n_bill,
                            "status": "Unpaid"

                        }).execute()

                        st.success("✅ Customer Added")

                        st.rerun()

                    except Exception as e:
                        st.error(f"Error: {e}")

    # =====================================================
    # 👥 CREATE STAFF
    # =====================================================

    if is_admin:

        with st.sidebar.expander("👥 Create Staff"):

            with st.form(
                "create_staff_form",
                clear_on_submit=True
            ):

                st_name = st.text_input("Staff Name")
                st_user = st.text_input("Username")
                st_pass = st.text_input("Password")

                if st.form_submit_button(
                    "Create Staff"
                ):

                    if not all([
                        st_name,
                        st_user,
                        st_pass
                    ]):
                        st.error("❌ Fill all fields")

                    else:

                        try:

                            check_staff = supabase.table("isp_staff") \
                                .select("id") \
                                .eq("username", st_user) \
                                .execute()

                            if len(check_staff.data) > 0:

                                st.error("❌ Username exists")

                            else:

                                secure_password = hash_password(st_pass)

                                supabase.table("isp_staff").insert({

                                    "isp_id": my_isp_id,
                                    "staff_name": st_name,
                                    "username": st_user,
                                    "password": secure_password

                                }).execute()

                                st.success("✅ Staff Created")

                        except Exception as e:
                            st.error(f"Error: {e}")

    # =====================================================
    # 📊 FETCH DATA
    # =====================================================

    try:

        users_resp = supabase.table("billing_users") \
            .select("*") \
            .eq("isp_id", my_isp_id) \
            .order("name") \
            .execute()

        history_resp = supabase.table("billing_history") \
            .select("*") \
            .eq("isp_id", my_isp_id) \
            .execute()

        df_users = pd.DataFrame(users_resp.data)
        df_history = pd.DataFrame(history_resp.data)

    except Exception as e:

        st.error(f"Database Fetch Error: {e}")
        st.stop()

    # =====================================================
    # 📑 TABS
    # =====================================================

    if is_admin:

        tab1, tab2, tab3 = st.tabs([
            "📊 Billing",
            "📍 Area Analytics",
            "📚 Payment History"
        ])

    else:

        tab1, tab2 = st.tabs([
            "📊 Billing",
            "📍 Area Analytics"
        ])

    # =====================================================
    # 📊 BILLING TAB
    # =====================================================

    with tab1:

        if df_users.empty:

            st.info("No customers added yet.")

        else:

            total_users = len(df_users)

            paid_users = len(
                df_users[df_users["status"] == "Paid"]
            )

            unpaid_users = len(
                df_users[df_users["status"] == "Unpaid"]
            )

            st.markdown(f"""

            <div class="metric-box-container">

                <div class="metric-box">
                    <div class="metric-box-title">
                        Total Customers
                    </div>

                    <div class="metric-box-value">
                        {total_users}
                    </div>
                </div>

                <div class="metric-box">
                    <div class="metric-box-title">
                        Paid
                    </div>

                    <div class="metric-box-value" style="color:green;">
                        {paid_users}
                    </div>
                </div>

                <div class="metric-box">
                    <div class="metric-box-title">
                        Unpaid
                    </div>

                    <div class="metric-box-value" style="color:red;">
                        {unpaid_users}
                    </div>
                </div>

            </div>

            """, unsafe_allow_html=True)

            # SEARCH

            search = st.text_input("🔍 Search Customer")

            if search:

                df_users = df_users[
                    df_users["name"]
                    .str.lower()
                    .str.contains(search.lower())
                ]

            st.dataframe(
                df_users,
                use_container_width=True
            )

    # =====================================================
    # 📍 AREA TAB
    # =====================================================

    with tab2:

        if not df_users.empty:

            areas = ["All"] + list(
                df_users["area"].unique()
            )

            selected_area = st.selectbox(
                "Select Area",
                areas
            )

            if selected_area == "All":
                filtered = df_users
            else:
                filtered = df_users[
                    df_users["area"] == selected_area
                ]

            st.dataframe(
                filtered,
                use_container_width=True
            )

    # =====================================================
    # 📚 HISTORY TAB
    # =====================================================

    if is_admin:

        with tab3:

            if df_history.empty:

                st.info("No payment history.")

            else:

                st.dataframe(
                    df_history,
                    use_container_width=True
                )