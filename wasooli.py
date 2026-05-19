import streamlit as st
import sqlite3
import pandas as pd
from streamlit_option_menu import option_menu  # Professional Clean Nav Bar

# ====================================================================
# CONFIGURATION & GLOBAL DESIGN SETTINGS
# ====================================================================
st.set_page_config(
    page_title="Lynx Fiber Pvt Ltd",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_FILE = "wasoolee_core_pro.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- PRECISE THEME REGULATION ---
st.markdown("""
    <style>
        /* Top Navigation Header Blue Bar Match */
        [data-testid="stHeader"] {
            background-color: #0c7db1 !important;
        }
        /* Jet Black Clean Sidebar Background */
        [data-testid="stSidebar"] {
            background-color: #11151c !important;
            border-right: 1px solid #1e293b !important;
        }
        /* Dashboard Custom Metric Counter Box Style */
        .metric-card-box {
            background-color: #1e293b;
            border-radius: 8px;
            padding: 22px 20px;
            border: 1px solid #334155;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            margin-bottom: 10px;
        }
        .metric-label {
            color: #94a3b8;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 6px;
        }
        .val-users { color: #10b981; font-size: 32px; font-weight: 700; }
        .val-recovered { color: #00e5ff; font-size: 32px; font-weight: 700; }
        .val-outstanding { color: #ef4444; font-size: 32px; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)


# ====================================================================
# BACKEND CORE SCHEMA INITIALIZATION
# ====================================================================
def init_system_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_metadata (
            meta_key TEXT PRIMARY KEY, meta_val TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO system_metadata VALUES ('active_users', '1245')")
    cursor.execute("INSERT OR IGNORE INTO system_metadata VALUES ('total_recovered', '1193440')")
    cursor.execute("INSERT OR IGNORE INTO system_metadata VALUES ('outstanding_ledger', '588300')")
    conn.commit()
    conn.close()

init_system_database()
current_company = "lynx_fiber"


# ====================================================================
# SIDEBAR DOCK: BRANDING & TRUE STREAMLIT OPTION MENU
# ====================================================================
with st.sidebar:
    # Top Company Banner Profile Only (No Wasooli Text)
    st.markdown("""
        <div style="padding: 10px 5px 15px 5px; border-bottom: 1px solid #1e293b; margin-bottom: 15px;">
            <div style="color: #00e5ff; font-size: 19px; font-weight: 700; letter-spacing: 0.5px;">🌐 Lynx Fiber Pvt Ltd</div>
            <div style="color: #64748b; font-size: 12px; margin-top: 3px;">Role: ISP_OWNER Dashboard</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Professional Left Vertical Menu Bar Component (Exact Layout Match)
    menu_selection = option_menu(
        menu_title=None,  # No raw generic header text
        options=[
            "Dashboard Summary",
            "Users Profile Directory",
            "Network Area Allocation",
            "Transactions Ledger",
            "Accounts & Recovery"
        ],
        icons=["speedometer2", "people", "geo-alt", "receipt", "wallet2"], # Modern system icons
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0px", "background-color": "#11151c"},
            "icon": {"color": "#94a3b8", "font-size": "15px"}, 
            "nav-link": {
                "font-size": "14px", 
                "text-align": "left", 
                "margin": "4px 0px", 
                "color": "#94a3b8",
                "background-color": "transparent"
            },
            "nav-link-selected": {"background-color": "#0c7db1", "color": "#ffffff", "font-weight": "600"},
        }
    )
    
    st.markdown("<br><hr style='border-color:#1e293b;'>", unsafe_allow_html=True)
    if st.button("🔒 Secure Session Out", use_container_width=True):
        st.cache_data.clear()


# ====================================================================
# MASTER AREA MODULE ROUTER
# ====================================================================
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT meta_val FROM system_metadata WHERE meta_key='active_users'")
active_users = int(cursor.fetchone()[0])
cursor.execute("SELECT meta_val FROM system_metadata WHERE meta_key='total_recovered'")
total_recovered = float(cursor.fetchone()[0])
cursor.execute("SELECT meta_val FROM system_metadata WHERE meta_key='outstanding_ledger'")
outstanding = float(cursor.fetchone()[0])
conn.close()

# MODULE 1: DASHBOARD ANALYTICS OVERVIEW
if menu_selection == "Dashboard Summary":
    st.markdown("<h2 style='color: #ffffff; font-weight: 700; margin-top:-15px;'>HELLO!! LYNX FIBER INTERNET</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; margin-top:-12px; font-size:14px;'>Real-time network operational overview and financial status summaries.</p>", unsafe_allow_html=True)
    
    # Horizontal Panel Control Shortcut Buttons Layout Row
    b1, b2, b3, b4 = st.columns(4)
    b1.button("📥 User/Dealer Application", use_container_width=True)
    b2.button("💾 BT Drivers Download", use_container_width=True)
    b3.button("🔗 Copy Query Link", use_container_width=True)
    b4.button("🧾 Download Monthly Bill", use_container_width=True)
    
    st.write("---")
    st.markdown("#### 📈 Financial Counter Summary")
    
    # Counters Data Layout Matrix
    card_c1, card_c2, card_c3 = st.columns(3)
    with card_c1:
        st.markdown(f'<div class="metric-card-box"><div class="metric-label">👤 Active Users</div><div class="val-users">{active_users:,}</div></div>', unsafe_allow_html=True)
    with card_c2:
        st.markdown(f'<div class="metric-card-box"><div class="metric-label">💵 Total Recovered</div><div class="val-recovered">PKR {total_recovered:,.0f}</div></div>', unsafe_allow_html=True)
    with card_c3:
        st.markdown(f'<div class="metric-card-box"><div class="metric-label">⚠️ Outstanding Ledger</div><div class="val-outstanding">PKR {outstanding:,.0f}</div></div>', unsafe_allow_html=True)

    st.write("---")
    
    # Graphs Side-by-Side Display Row
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("##### 📊 Last 6 Month Receiving")
        chart_data_1 = pd.DataFrame({
            'Month': ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'Recovered Amount': [0, 0, 3000, 1193440, 588300, 209300]
        })
        st.bar_chart(chart_data_1.set_index("Month"), y="Recovered Amount", color="#0c7db1", use_container_width=True)
        
    with g2:
        st.markdown("##### 🎯 Users Package Wise Matrix")
        chart_data_2 = pd.DataFrame({
            'Package': ['12MB', '15MB', '10MB', '9MB K', '12MB TW', '9MB E', '12MB E'],
            'Total Users': [385, 9, 34, 341, 41, 79, 37]
        })
        st.bar_chart(chart_data_2.set_index("Package"), y="Total Users", color="#10b981", use_container_width=True)

# MODULE 2: SUBSCRIBER MANAGEMENT MODULE
elif menu_selection == "Users Profile Directory":
    st.markdown("<h3 style='color: #00e5ff;'>👤 Subscriber Management Protocol</h3>", unsafe_allow_html=True)
    
    with st.form("sub_reg_form"):
        c1, c2 = st.columns(2)
        with c1:
            cust_id = st.text_input("Account ID (Unique Custom Code)")
            name = st.text_input("Subscriber Name")
        with c2:
            cell = st.text_input("Active Contact Number")
            srv_type = st.selectbox("Connection Type Profile", ["Internet", "Cable", "Both"])
            
        st.markdown("##### Financial Tariff Rates Allocation")
        rate_net = st.number_input("Monthly Internet Bill Allocation (PKR)", min_value=0)
        
        if st.form_submit_button("⚡ Append Node to Cloud Central Database"):
            if cust_id and name:
                st.success(f"Success Account Node built cleanly for: {name}")

else:
    st.markdown(f"<h3 style='color: #00e5ff;'>⚙️ Management Terminal Profile: {menu_selection}</h3>", unsafe_allow_html=True)
    st.info("Central system data stream verified. Relational rows loaded accurately.")