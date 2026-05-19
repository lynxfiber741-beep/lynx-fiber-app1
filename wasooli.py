import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ====================================================================
# CONFIGURATION & REAL INTERFACE CORE SETUP
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

# --- EXACT DASHBOARD LAYOUT CSS INJECTION ---
st.markdown("""
    <style>
        /* 1. Reset Top Header Color & Spacing */
        [data-testid="stHeader"] {
            background-color: #1266f1 !important;
            height: 3.5rem;
        }
        
        /* 2. Narrow Jet-Black Left Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #11151c !important;
            min-width: 140px !important;
            max-width: 180px !important;
            border-right: 1px solid #1e222b !important;
        }
        
        /* 3. Hide Default Streamlit Widgets Elements inside Sidebar */
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
            display: none !important;
        }
        
        /* Remove Default Radio Selection Indicators and Boxes */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
            gap: 15px !important;
            padding-top: 20px;
        }
        
        /* Transforming standard options into clean rounded indicator rows */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
            background-color: transparent !important;
            border: none !important;
            padding: 8px 10px !important;
            color: #94a3b8 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            width: 100%;
        }
        
        /* Hide default selection circles */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label [data-testid="stRadioButtonToLabelWithGap"] > div:first-child {
            display: none !important;
        }
        
        /* Text alignment inside buttons */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
            font-size: 14px !important;
            font-weight: 500 !important;
            margin: 0 !important;
        }

        /* Hover and Active selection color matrix match */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
            color: #00e5ff !important;
            cursor: pointer;
        }
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] [data-checked="true"] label {
            color: #ffffff !important;
            background-color: #1e293b !important;
            border-left: 4px solid #00e5ff !important;
            border-radius: 0px 4px 4px 0px;
        }

        /* 4. Financial Counter Display Cards Setup */
        .counter-card {
            background-color: #1e2530;
            border-radius: 6px;
            padding: 24px 20px;
            border: 1px solid #2a3444;
            text-align: left;
        }
        .counter-label {
            color: #94a3b8;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .val-users { color: #10b981; font-size: 34px; font-weight: 700; }
        .val-recovered { color: #00e5ff; font-size: 34px; font-weight: 700; }
        .val-outstanding { color: #ef4444; font-size: 34px; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# ====================================================================
# CORE RECOVERY LOGIC & INSTANTIATION
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

# ====================================================================
# SIDEBAR NAVIGATION ROUTER (MINIMAL LAYOUT NODE)
# ====================================================================
with st.sidebar:
    st.markdown("<div style='padding: 10px 5px; color:#00e5ff; font-weight:700; font-size:14px;'>🌐 Lynx Fiber</div>", unsafe_allow_html=True)
    
    # Precise UI matching control panel items list
    app_mode = st.radio(
        "CORE_MENU",
        [
            "📊 Dashboard Summary",
            "👥 Users Directory",
            "📍 Area Profiles",
            "📈 Ledger Transactions",
            "⚙️ System Settings"
        ]
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🔒 Log Out", use_container_width=True):
        st.cache_data.clear()

# ====================================================================
# ROUTED WORKSPACE VIEWS
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

if app_mode == "📊 Dashboard Summary":
    # Screen Identity Nodes
    st.markdown("<h2 style='color: #ffffff; font-weight: 700; margin-top:-15px;'>HELLO!! LYNX FIBER INTERNET</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; margin-top:-12px; font-size:14px;'>Real-time network operational overview and financial status summaries.</p>", unsafe_allow_html=True)
    
    # Command Row Structure Match
    btn_c1, btn_c2, btn_c3, btn_c4 = st.columns(4)
    btn_c1.button("📥 User/Dealer Application", use_container_width=True)
    btn_c2.button("💾 BT Drivers Download", use_container_width=True)
    btn_c3.button("🔗 Copy Query Link", use_container_width=True)
    btn_c4.button("🧾 Download Monthly Bill", use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📈 Financial Counter Summary")
    
    # Exact Counter Layout Rendering (Matches 1,245 Active State Profile)
    card_c1, card_c2, card_c3 = st.columns(3)
    with card_c1:
        st.markdown(f"""
            <div class="counter-card">
                <div class="counter-label">👤 Active Users</div>
                <div class="val-users">{active_users:,}</div>
            </div>
        """, unsafe_allow_html=True)
    with card_c2:
        st.markdown(f"""
            <div class="counter-card">
                <div class="counter-label">💵 Total Recovered</div>
                <div class="val-recovered">PKR {total_recovered:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)
    with card_c3:
        st.markdown(f"""
            <div class="counter-card">
                <div class="counter-label">⚠️ Outstanding Ledger</div>
                <div class="val-outstanding">PKR {outstanding:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><hr style='border-color:#2a3444;'>", unsafe_allow_html=True)
    
    # Analytical Visual Charts
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("##### 📊 Last 6 Month Receiving")
        chart_data_1 = pd.DataFrame({
            'Month': ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'Recovered Amount': [0, 0, 3000, 1193440, 588300, 209300]
        })
        st.bar_chart(chart_data_1.set_index("Month"), y="Recovered Amount", color="#1266f1", use_container_width=True)
        
    with g2:
        st.markdown("##### 🎯 Users Package Wise Matrix")
        chart_data_2 = pd.DataFrame({
            'Package': ['12MB', '15MB', '10MB', '9MB K', '12MB TW', '9MB E', '12MB E'],
            'Total Users': [385, 9, 34, 341, 41, 79, 37]
        })
        st.bar_chart(chart_data_2.set_index("Package"), y="Total Users", color="#10b981", use_container_width=True)

elif app_mode == "👥 Users Directory":
    st.markdown("<h3 style='color: #00e5ff;'>👤 Subscriber Configuration Node</h3>", unsafe_allow_html=True)
    
    with st.form("subscriber_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            cust_id = st.text_input("Internet User ID / Account ID")
            full_name = st.text_input("Subscriber Name")
        with col_b:
            phone = st.text_input("Contact Number")
            srv_type = st.selectbox("Service Provision Type", ["Internet", "Cable", "Both"])
            
        st.markdown("##### Tariff Mapping")
        net_p = st.number_input("Internet Rate (PKR)", min_value=0)
        
        if st.form_submit_button("Save Subscriber Profile"):
            if cust_id and full_name:
                st.success(f"Record successfully initialized for {full_name}.")