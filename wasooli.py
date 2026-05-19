import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ====================================================================
# 1. PREMIUM ULTIMATE WEB INTERFACE CONFIGURATION (WASOOLI STYLE)
# ====================================================================
st.set_page_config(
    page_title="Wasooli Cloud Software Engine",
    page_icon="⚡",
    layout="wide", # Poori screen use karne ke liye
    initial_sidebar_state="expanded"
)

# Database Connection (Postgres/SQLite wrapper)
def get_db_connection():
    conn = sqlite3.connect("wasooli_cloud.db")
    conn.row_factory = sqlite3.Row
    return conn

# Temporary Mock Session Data for testing (Replace with your actual auth session states)
if "user_data" not in st.session_state:
    st.session_state["user_data"] = {"role": "isp_owner", "company_id": 1}
current_company = st.session_state["user_data"]["company_id"]

# --- ORIGINAL INJECTED CSS FOR TRUE PREVIEW MATCH ---
st.markdown("""
    <style>
        /* Top Header Blue Strip Match */
        .stAppHeader {
            background-color: #0284c7 !important;
            color: white !important;
        }
        /* Left Sidebar Original Dark Menu Style */
        [data-testid="stSidebar"] {
            background-color: #111827 !important;
            border-right: 2px solid #22c55e !important; /* Green separator line */
        }
        /* Metric Card Boxes Styling */
        .metric-box {
            background-color: #1f2937;
            border: 1px solid #374151;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        /* Tables & Dataframes customized view */
        .stDataFrame {
            background-color: #111827;
            border-radius: 8px;
        }
        /* Buttons styling matching original cyan/blue elements */
        .stButton>button {
            background-color: #0284c7 !important;
            color: white !important;
            border-radius: 4px !important;
            border: none !important;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #0369a1 !important;
            border: none !important;
        }
    </style>
""", unsafe_allow_html=True)


# ====================================================================
# 2. LEFT SIDEBAR MENU TERMINAL (EXACT NAVIGATION MATCH)
# ====================================================================
st.sidebar.markdown("<h2 style='color: #22c55e; font-weight: bold; margin-bottom: 0px;'>⚡ WASOOLI!</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color: #9ca3af; font-size: 12px; margin-top: 0px;'>Cloud Software Engine</p>", unsafe_allow_html=True)
st.sidebar.write("---")

# Left Side Menu Options (Exactly like your left side panel screenshot)
menu_selection = st.sidebar.radio(
    "🖥️ MAIN PANEL NODE",
    [
        "📊 Dashboard Overview",
        "👤 Provision Subscriber",
        "📍 Network Areas (Nodes)",
        "📋 Live Directory",
        "⚙️ Run Monthly Billing",
        "💰 Accounts & Recovery"
    ]
)

st.sidebar.write("---")
st.sidebar.caption("🔒 Connected Node: Lynx Fiber Pvt Ltd")
st.sidebar.caption("📦 Active Operational System")


# ====================================================================
# 3. INTERFACE ROUTING ENGINE (PREVIEW CONTROLLER)
# ====================================================================

# --------------------------------------------------------------------
# MENU NODE 1: MAIN DASHBOARD OVERVIEW (With Core Metric Cards & Graphs)
# --------------------------------------------------------------------
if menu_selection == "📊 Dashboard Overview":
    st.markdown("<h2 style='color: #00f0ff;'>HELLO!! LYNX FIBER INTERNET</h2>", unsafe_allow_html=True)
    st.write("Real-time network operational overview and financial status summaries.")
    
    # Core Quick Action Buttons Row (Like Top Cyan Row of your old app)
    c1, c2, c3, c4 = st.columns(4)
    c1.button("📥 User/Dealer Application", use_container_width=True)
    c2.button("💾 BT Drivers Download", use_container_width=True)
    c3.button("🔗 Copy Query Link", use_container_width=True)
    c4.button("🧾 Download Monthly Bill", use_container_width=True)
    
    st.write("---")
    
    # Financial KPI Summary Row Cards (Total Receivable, Recovered, Outstanding)
    st.markdown("#### 📈 Financial Counter Summary")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown('<div class="metric-box"><p style="color: #9ca3af; margin:0;">👥 Active Users</p><h2 style="color: #22c55e; margin:0;">1,245</h2></div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="metric-box"><p style="color: #9ca3af; margin:0;">📈 Total Recovered</p><h2 style="color: #00f0ff; margin:0;">PKR 1,193,440</h2></div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="metric-box"><p style="color: #9ca3af; margin:0;">⚠️ Outstanding Ledger</p><h2 style="color: #ef4444; margin:0;">PKR 588,300</h2></div>', unsafe_allow_html=True)
        
    st.write("---")
    
    # Graphical Analytics Matrices Side-by-Side (Last 6 Months vs Package Wise)
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("##### 📊 Last 6 Month Receiving")
        # Dummy data matching your exact chart structure
        chart_data1 = pd.DataFrame({'Recovered Amount': [0, 0, 3000, 1193440, 588300, 209300]}, index=['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May'])
        st.bar_chart(chart_data1, color="#0284c7", use_container_width=True)
        
    with g2:
        st.markdown("##### 🎯 Users Package Wise Matrix")
        chart_data2 = pd.DataFrame({'Total Users': [385, 9, 34, 1, 341, 41, 209, 37]}, index=['12MB', '15MB', '10MB', '20MB', '9MB K', '12MB TW', '9MB E', '12MB E'])
        st.bar_chart(chart_data2, color="#22c55e", use_container_width=True)

# --------------------------------------------------------------------
# MENU NODE 2: PROVISION NEW SUBSCRIBER (Form Entry)
# --------------------------------------------------------------------
elif menu_selection == "👤 Provision Subscriber":
    st.markdown("<h3 style='color: #00f0ff;'>📝 Subscriber Entry Protocol</h3>", unsafe_allow_html=True)
    
    with st.form("subscriber_form"):
        col1, col2 = st.columns(2)
        with col1:
            cust_id = st.text_input("Internet User ID / Custom Account ID (Unique)", placeholder="e.g., LNX-9982")
            fullname = st.text_input("Subscriber Full Name")
            phone = st.text_input("Cell Phone Number")
        with col2:
            sublocality = st.selectbox("Sublocality / Operational System Network", options=["Sanghoi System", "Saeela System"])
            conn_type = st.selectbox("Connection Service Type", options=["Internet", "Cable", "Both"])
            address = st.text_area("Installation Physical Address")
            
        st.markdown("##### 💰 Tariff Rates & Package Architecture Setup")
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            pkg_internet = st.text_input("Internet Package Profile Name", placeholder="e.g., 20 Mbps Premium")
            amount_internet = st.number_input("Monthly Internet Base Rate (PKR)", min_value=0.0, step=50.0)
        with p_col2:
            pkg_cable = st.text_input("Cable TV Package Profile Name", placeholder="e.g., Digital HD Max")
            amount_cable = st.number_input("Monthly Cable Base Rate (PKR)", min_value=0.0, step=50.0)
            
        submit = st.form_submit_button("⚡ Finalize & Write Subscriber Node")
        if submit:
            st.success(f"Subscriber {fullname} successfully queued to {sublocality} cloud cluster!")

# --------------------------------------------------------------------
# MENU NODE 3: MANAGE NETWORK AREAS
# --------------------------------------------------------------------
elif menu_selection == "📍 Network Areas (Nodes)":
    st.markdown("<h3 style='color: #00f0ff;'>📍 Manage Network Regional Systems</h3>", unsafe_allow_html=True)
    # Area insert and view logic goes here...
    st.info("System linked with active distribution nodes: Sanghoi System & Saeela System.")

# --------------------------------------------------------------------
# MENU NODE 4: LIVE DIRECTORY LIST
# --------------------------------------------------------------------
elif menu_selection == "📋 Live Directory":
    st.markdown("<h3 style='color: #00f0ff;'>📋 Live Subscriber Master Directory</h3>", unsafe_allow_html=True)
    # Interactive dataframe listing table
    st.caption("Active entries synchronized over central cloud database.")

# --------------------------------------------------------------------
# MENU NODE 5: RUN MONTHLY BILLING
# --------------------------------------------------------------------
elif menu_selection == "⚙️ Run Monthly Billing":
    st.markdown("<h3 style='color: #00f0ff;'>⚙️ Automated Monthly Invoicing System</h3>", unsafe_allow_html=True)
    # Bulk invoicing button terminal
    st.button("🚀 Trigger Bulk Invoicing Run")

# --------------------------------------------------------------------
# MENU NODE 6: ACCOUNTS & RECOVERY CENTRAL LEDGER
# --------------------------------------------------------------------
elif menu_selection == "💰 Accounts & Recovery":
    st.markdown("<h3 style='color: #00f0ff;'>💰 Central Accounts Recovery Ledger</h3>", unsafe_allow_html=True)
    # Desktop collection system rows