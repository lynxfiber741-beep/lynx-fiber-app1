import streamlit as st
import sqlite3
import pandas as pd

# ====================================================================
# 1. CORE APPLICATION CONFIGURATION
# ====================================================================
st.set_page_config(
    page_title="Lynx Fiber Pvt Ltd",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed" # Real app ki tarah full screen experience
)

DB_FILE = "wasoolee_core_pro.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# ====================================================================
# 2. DATABASE INITIALIZATION
# ====================================================================
def init_db():
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

init_db()

# Fetch Metrics
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT meta_val FROM system_metadata WHERE meta_key='active_users'")
active_users = int(cursor.fetchone()[0])
cursor.execute("SELECT meta_val FROM system_metadata WHERE meta_key='total_recovered'")
total_recovered = float(cursor.fetchone()[0])
cursor.execute("SELECT meta_val FROM system_metadata WHERE meta_key='outstanding_ledger'")
outstanding = float(cursor.fetchone()[0])
conn.close()

# ====================================================================
# 3. HIGH-FIDELITY BOOTSTRAP INTERFACE INJECTION
# ====================================================================
# Hum yahan custom pure HTML use kar rahe hain taaki Streamlit ka bikhra look mukammal khatam ho jaye.

# URL query string se menu change karne ka mechanism
query_params = st.query_params
if "menu" not in query_params:
    st.query_params["menu"] = "dashboard"
current_menu = st.query_params["menu"]

st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
    
    <style>
        /* Hide all default Streamlit branding, bars and wrapper spaces */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding: 0rem !important; max-width: 100% !important;}
        [data-testid="stHeader"] {display: none !important;}
        
        /* Global Reset */
        body {
            background-color: #f4f6f9 !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        }
        
        /* Layout Structure */
        .app-wrapper {
            display: flex;
            height: 100vh;
            overflow: hidden;
        }
        
        /* Sleek Left Sidebar Node Match */
        .custom-sidebar {
            width: 70px;
            background-color: #111625;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 15px;
            box-shadow: 2px 0 5px rgba(0,0,0,0.1);
            z-index: 100;
        }
        .sidebar-logo {
            color: #00e5ff;
            font-size: 24px;
            margin-bottom: 30px;
        }
        .nav-item-link {
            color: #64748b;
            font-size: 20px;
            margin-bottom: 22px;
            cursor: pointer;
            transition: all 0.2s ease;
            width: 100%;
            text-align: center;
            padding: 8px 0;
            display: block;
            text-decoration: none;
        }
        .nav-item-link:hover {
            color: #00e5ff;
        }
        .nav-item-link.active-node {
            color: #ffffff;
            background-color: #1e293b;
            border-left: 3px solid #00e5ff;
        }
        
        /* Main Application Workspace */
        .main-workspace {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            background-color: #f4f6f9;
            overflow-y: auto;
        }
        
        /* Premium Top Blue Navigation Strip */
        .top-blue-strip {
            background-color: #0c7db1;
            color: white;
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .company-brand-txt {
            font-size: 16px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        
        /* Workspace Margin Trimming */
        .content-body {
            padding: 20px;
        }
        
        /* Compact Metrics Cards Layout Grid */
        .kpi-card {
            background: white;
            border-radius: 6px;
            padding: 15px 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 4px solid #00e5ff;
        }
        .kpi-card.recovered-border { border-left-color: #10b981; }
        .kpi-card.outstanding-border { border-left-color: #ef4444; }
        
        .kpi-title {
            color: #64748b;
            font-size: 13px;
            font-weight: 500;
            text-transform: uppercase;
        }
        .kpi-value {
            font-size: 26px;
            font-weight: 700;
            color: #1e293b;
            margin-top: 5px;
        }
        
        /* Action Shortcut Buttons Styling */
        .action-btn-custom {
            background-color: #ffffff;
            color: #334155;
            border: 1px solid #e2e8f0;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 500;
            border-radius: 4px;
            transition: all 0.2s;
            text-align: center;
            width: 100%;
            display: inline-block;
        }
        .action-btn-custom:hover {
            background-color: #f8fafc;
            border-color: #cbd5e1;
            color: #0c7db1;
        }
    </style>
""", unsafe_allow_html=True)

# ====================================================================
# 4. DRAW THE EXACT STRUCTURAL VIEW INTERFACE
# ====================================================================
# Yahan hum left side bar aur top blue row render kar rahe hain.

sidebar_html = f"""
<div class="app-wrapper">
    <div class="custom-sidebar">
        <div class="sidebar-logo"><i class="bi bi-globe"></i></div>
        <a href="?menu=dashboard" class="nav-item-link {'active-node' if current_menu == 'dashboard' else ''}" title="Dashboard"><i class="bi bi-speedometer2"></i></a>
        <a href="?menu=users" class="nav-item-link {'active-node' if current_menu == 'users' else ''}" title="Users"><i class="bi bi-people"></i></a>
        <a href="?menu=network" class="nav-item-link {'active-node' if current_menu == 'network' else ''}" title="Network Systems"><i class="bi bi-geo-alt"></i></a>
        <a href="?menu=ledger" class="nav-item-link {'active-node' if current_menu == 'ledger' else ''}" title="Ledger"><i class="bi bi-receipt"></i></a>
        <a href="?menu=accounts" class="nav-item-link {'active-node' if current_menu == 'accounts' else ''}" title="Recovery"><i class="bi bi-wallet2"></i></a>
    </div>
    
    <div class="main-workspace">
        <div class="top-blue-strip">
            <div class="company-brand-txt">🌐 LYNX FIBER PVT LTD</div>
            <div style="font-size: 13px;"><i class="bi bi-person-circle"></i> Role: ISP_OWNER</div>
        </div>
"""
st.markdown(sidebar_html, unsafe_allow_html=True)

# Container Body Open
st.markdown('<div class="content-body">', unsafe_allow_html=True)

# ROUTER BLOCK FOR VIEWS
if current_menu == "dashboard":
    # Greeting Block Header
    st.markdown("""
        <div class="mb-4">
            <h4 class="mb-1" style="color:#1e293b; font-weight:700;">HELLO!! LYNX FIBER INTERNET</h4>
            <p style="color:#64748b; font-size:13px; margin:0;">Real-time network operational overview and financial status summaries.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Grid Row of Dashboard Top Buttons Shortcuts
    st.markdown("""
        <div class="row g-2 mb-4">
            <div class="col-md-3"><div class="action-btn-custom"><i class="bi bi-download"></i> User/Dealer Application</div></div>
            <div class="col-md-3"><div class="action-btn-custom"><i class="bi bi-hdd-network"></i> BT Drivers Download</div></div>
            <div class="col-md-3"><div class="action-btn-custom"><i class="bi bi-link-45deg"></i> Copy Query Link</div></div>
            <div class="col-md-3"><div class="action-btn-custom"><i class="bi bi-file-earmark-text"></i> Download Monthly Bill</div></div>
        </div>
        <h6 class="mb-3" style="color:#475569; font-weight:600;">📊 Financial Counter Summary</h6>
    """, unsafe_allow_html=True)
    
    # Core Summary Grid Boxes Match (Compact Cards Style)
    st.markdown(f"""
        <div class="row g-3 mb-4">
            <div class="col-md-4">
                <div class="kpi-card">
                    <div class="kpi-title">👤 Active Users</div>
                    <div class="kpi-value">{active_users:,}</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="kpi-card recovered-border">
                    <div class="kpi-title">💵 Total Recovered</div>
                    <div class="kpi-value">PKR {total_recovered:,.0f}</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="kpi-card outstanding-border">
                    <div class="kpi-title">⚠️ Outstanding Ledger</div>
                    <div class="kpi-value">PKR {outstanding:,.0f}</div>
                </div>
            </div>
        </div>
        <hr style="border-color:#cbd5e1;">
    """, unsafe_allow_html=True)
    
    # Graphs Data Workspace Render Area
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("<span style='color:#475569; font-weight:600; font-size:14px;'>📊 Last 6 Month Receiving</span>", unsafe_allow_html=True)
        chart_data_1 = pd.DataFrame({
            'Month': ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'Recovered Amount': [0, 0, 3000, 1193440, 588300, 209300]
        })
        st.bar_chart(chart_data_1.set_index("Month"), y="Recovered Amount", color="#0c7db1", use_container_width=True)
        
    with g2:
        st.markdown("<span style='color:#475569; font-weight:600; font-size:14px;'>🎯 Users Package Wise Matrix</span>", unsafe_allow_html=True)
        chart_data_2 = pd.DataFrame({
            'Package': ['12MB', '15MB', '10MB', '9MB K', '12MB TW', '9MB E', '12MB E'],
            'Total Users': [385, 9, 34, 341, 41, 79, 37]
        })
        st.bar_chart(chart_data_2.set_index("Package"), y="Total Users", color="#10b981", use_container_width=True)

elif current_menu == "users":
    st.markdown("<h4 style='color: #0c7db1; font-weight:700;'>👤 Subscriber Master Protocol</h4><br>", unsafe_allow_html=True)
    # Streamlit elements can blend seamlessly into forms when structured in rows
    with st.form("sub_form"):
        r1, r2 = st.columns(2)
        r1.text_input("Internet User ID / Custom Account ID")
        r1.text_input("Subscriber Name")
        r2.text_input("Active Mobile Number")
        r2.selectbox("Connection Profile Type", ["Internet", "Cable", "Both"])
        st.form_submit_button("⚡ Append Record to Core Node")

else:
    st.markdown(f"<h4 style='color: #0c7db1;'>⚙️ System Module Cluster Active</h4>", unsafe_allow_html=True)
    st.info(f"Dynamic view initialized for option node parameter. Relational framework links running safe.")

# Closures for layout HTML wrappers
st.markdown('</div></div></div>', unsafe_allow_html=True)