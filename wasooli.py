import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
import bcrypt
import re

# =========================================================
# ⚡ LYNX FIBER ADVANCED ISP CRM SYSTEM
# =========================================================

st.set_page_config(
    page_title="LYNX Fiber - Advanced ISP Portal",
    layout="wide",
    page_icon="⚡"
)

# =========================================================
# 🎨 PREMIUM CSS UI
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
    background-color: #0284c7;
    color: white;
    padding: 15px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100vw;
    position: relative;
    left: 50%;
    margin-left: -50vw;
    font-family: Arial, sans-serif;
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
# 📅 DATE VARIABLES
# =========================================================

current_month = datetime.now().strftime("%B")
current_year = datetime.now().strftime("%Y")
today_date = datetime.now().strftime("%Y-%m-%d")

# =========================================================
# 🔒 SESSION MANAGEMENT
# =========================================================

defaults = {
    "logged_in": False,
    "user_role": None,
    "isp_id": None,
    "isp_name": "",
    "operator_name": "",
    "branding_mode": "Lynx Branding"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# 🔐 SECURITY FUNCTIONS
# =========================================================

def hash_password(password):
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(
        password.encode(),
        hashed.encode()
    )

def validate_phone(phone):
    return re.match(r'^[0-9]{11}$', phone)

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.rerun()

# =========================================================
# 🌐 TOP HEADER
# =========================================================

if st.session_state["logged_in"]:

    title = (
        st.session_state["isp_name"].upper()
        if st.session_state["branding_mode"] == "Own Branding"
        else "LYNX FIBER INTERNET"
    )

    role = f"{st.session_state['operator_name']} ({st.session_state['user_role']})"

    st.markdown(f"""
    <div class="wasooli-header">
        <div class="wasooli-brand">
            ⚡ {title}
        </div>

        <div class="wasooli-role-badge">
            👤 {role}
        </div>
    </div>
    """, unsafe_allow_html=True)

else:

    st.markdown("""
    <div class="wasooli-header">
        <div class="wasooli-brand">
            ⚡ LYNX FIBER SYSTEM
        </div>

        <div class="wasooli-role-badge">
            🔒 SECURED ACCESS
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# 🔐 LOGIN / REGISTER
# =========================================================

if not st.session_state["logged_in"]:

    _, center, _ = st.columns([1, 1.6, 1])

    with center:

        st.markdown("<br><br>", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs([
            "📲 Staff Login",
            "🔒 Admin Login",
            "📝 Register ISP"
        ])

        # =================================================
        # 👨‍🔧 STAFF LOGIN
        # =================================================

        with tab1:

            with st.form("staff_login"):

                s_user = st.text_input("Username")
                s_pass = st.text_input("Password", type="password")

                submit = st.form_submit_button("Login")

                if submit:

                    try:

                        res = supabase.table("isp_staff") \
                            .select("*, isp_companies(company_name, branding_mode)") \
                            .eq("username", s_user) \
                            .execute()

                        if len(res.data) == 0:
                            st.error("❌ User not found")

                        else:

                            user = res.data[0]

                            if verify_password(
                                s_pass,
                                user["password"]
                            ):

                                st.session_state["logged_in"] = True
                                st.session_state["user_role"] = "Staff"
                                st.session_state["isp_id"] = user["isp_id"]
                                st.session_state["operator_name"] = user["staff_name"]
                                st.session_state["isp_name"] = user["isp_companies"]["company_name"]
                                st.session_state["branding_mode"] = user["isp_companies"]["branding_mode"]

                                st.rerun()

                            else:
                                st.error("❌ Invalid password")

                    except Exception as e:
                        st.error(f"Error: {e}")

        # =================================================
        # 👑 ADMIN LOGIN
        # =================================================

        with tab2:

            with st.form("admin_login"):

                a_user = st.text_input("Admin Username")
                a_pass = st.text_input("Admin Password", type="password")

                submit = st.form_submit_button("Login")

                if submit:

                    try:

                        res = supabase.table("isp_companies") \
                            .select("*") \
                            .eq("username", a_user) \
                            .execute()

                        if len(res.data) == 0:
                            st.error("❌ Admin not found")

                        else:

                            admin = res.data[0]

                            if verify_password(
                                a_pass,
                                admin["password"]
                            ):

                                st.session_state["logged_in"] = True
                                st.session_state["user_role"] = "Admin"
                                st.session_state["isp_id"] = admin["id"]
                                st.session_state["operator_name"] = "Admin"
                                st.session_state["isp_name"] = admin["company_name"]
                                st.session_state["branding_mode"] = admin["branding_mode"]

                                st.rerun()

                            else:
                                st.error("❌ Invalid password")

                    except Exception as e:
                        st.error(f"Error: {e}")

        # =================================================
        # 📝 REGISTER ISP
        # =================================================

        with tab3:

            with st.form("register_isp"):

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

                submit = st.form_submit_button("Register ISP")

                if submit:

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

                            check = supabase.table("isp_companies") \
                                .select("id") \
                                .eq("username", r_user) \
                                .execute()

                            if len(check.data) > 0:
                                st.error("❌ Username already exists")

                            else:

                                secure_pass = hash_password(r_pass)

                                supabase.table("isp_companies").insert({

                                    "company_name": r_company,
                                    "username": r_user,
                                    "password": secure_pass,
                                    "phone": r_phone,
                                    "branding_mode": r_brand

                                }).execute()

                                st.success("✅ ISP Registered Successfully")

                        except Exception as e:
                            st.error(f"Registration Error: {e}")

# =========================================================
# 🚀 MAIN SYSTEM
# =========================================================

else:

    my_isp_id = st.session_state["isp_id"]
    is_admin = st.session_state["user_role"] == "Admin"

    st.sidebar.markdown(
        f"### Logged in as: `{st.session_state['user_role']}`"
    )

    if st.sidebar.button("🔒 Logout"):
        logout()

    # =====================================================
    # ➕ ADD CUSTOMER
    # =====================================================

    with st.sidebar.expander("➕ Add Customer", expanded=True):

        with st.form("add_customer"):

            c_name = st.text_input("Customer Name")
            c_user = st.text_input("PPPoE Username")
            c_phone = st.text_input("Phone Number")
            c_area = st.text_input("Area")

            c_prev = st.number_input(
                "Previous Balance",
                min_value=0,
                step=100
            )

            c_bill = st.number_input(
                "Monthly Bill",
                min_value=0,
                step=100
            )

            submit = st.form_submit_button("Save Customer")

            if submit:

                if not all([
                    c_name,
                    c_user,
                    c_phone,
                    c_area
                ]):
                    st.error("❌ Fill all fields")

                elif not validate_phone(c_phone):
                    st.error("❌ Invalid phone number")

                elif c_bill <= 0:
                    st.error("❌ Invalid bill")

                else:

                    try:

                        supabase.table("billing_users").insert({

                            "isp_id": my_isp_id,
                            "name": c_name,
                            "username": c_user,
                            "phone": c_phone,
                            "area": c_area,
                            "previous_balance": c_prev,
                            "current_bill": c_bill,
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

            with st.form("create_staff"):

                st_name = st.text_input("Staff Name")
                st_user = st.text_input("Username")
                st_pass = st.text_input("Password")

                submit = st.form_submit_button("Create Staff")

                if submit:

                    if not all([
                        st_name,
                        st_user,
                        st_pass
                    ]):
                        st.error("❌ Fill all fields")

                    else:

                        try:

                            check = supabase.table("isp_staff") \
                                .select("id") \
                                .eq("username", st_user) \
                                .execute()

                            if len(check.data) > 0:
                                st.error("❌ Username already exists")

                            else:

                                secure_pass = hash_password(st_pass)

                                supabase.table("isp_staff").insert({

                                    "isp_id": my_isp_id,
                                    "staff_name": st_name,
                                    "username": st_user,
                                    "password": secure_pass

                                }).execute()

                                st.success("✅ Staff Created")

                        except Exception as e:
                            st.error(f"Error: {e}")

    # =====================================================
    # 📊 LOAD DATA
    # =====================================================

    try:

        users = supabase.table("billing_users") \
            .select("*") \
            .eq("isp_id", my_isp_id) \
            .order("name") \
            .execute()

        history = supabase.table("billing_history") \
            .select("*") \
            .eq("isp_id", my_isp_id) \
            .execute()

        df_users = pd.DataFrame(users.data)
        df_history = pd.DataFrame(history.data)

    except Exception as e:

        st.error(f"Database Error: {e}")
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

            st.info("No customers added.")

        else:

            total = len(df_users)

            paid = len(
                df_users[df_users["status"] == "Paid"]
            )

            unpaid = len(
                df_users[df_users["status"] == "Unpaid"]
            )

            st.markdown(f"""
            <div class="metric-box-container">

                <div class="metric-box">
                    <div class="metric-box-title">
                        Total Customers
                    </div>

                    <div class="metric-box-value">
                        {total}
                    </div>
                </div>

                <div class="metric-box">
                    <div class="metric-box-title">
                        Paid
                    </div>

                    <div class="metric-box-value" style="color:green;">
                        {paid}
                    </div>
                </div>

                <div class="metric-box">
                    <div class="metric-box-title">
                        Unpaid
                    </div>

                    <div class="metric-box-value" style="color:red;">
                        {unpaid}
                    </div>
                </div>

            </div>
            """, unsafe_allow_html=True)

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
    # 📍 AREA ANALYTICS
    # =====================================================

    with tab2:

        if not df_users.empty:

            areas = ["All"] + list(
                df_users["area"].unique()
            )

            selected = st.selectbox(
                "Select Area",
                areas
            )

            if selected == "All":
                filtered = df_users
            else:
                filtered = df_users[
                    df_users["area"] == selected
                ]

            st.dataframe(
                filtered,
                use_container_width=True
            )

    # =====================================================
    # 📚 PAYMENT HISTORY
    # =====================================================

    if is_admin:

        with tab3:

            if df_history.empty:
                st.info("No payment history")

            else:

                st.dataframe(
                    df_history,
                    use_container_width=True
                )