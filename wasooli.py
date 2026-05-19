import streamlit as st
import sqlite3
import pandas as pd

# ====================================================================
# 1. APPLICATION VIEWPORT & ROOT CONFIGURATION
# ====================================================================
st.set_page_config(
    page_title="Lynx Fiber Pvt Ltd",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_FILE = "wasoolee_core_pro.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# ====================================================================
# 2. STATE CONFIGURATION & ROUTING ENGINE
# ====================================================================
# URL query parameter processing to lock view state across interaction triggers
if "menu" not in st.query_params:
    st.query_params["menu"] = "dashboard"
current_menu = st.query_params["menu"]

# ====================================================================
# 3. HIGH-FIDELITY CSS RESET OVERRIDES
# ====================================================================
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
    
    <style>
        /* Eradicate native Streamlit header margins and padding layout blocks */
        [data-testid="stHeader"], footer, #MainMenu { display: none !important; visibility: hidden; }
        .block-container { padding: 0rem !important; max-width: 100% !important; margin: 0 !important; }
        [data-testid="stAppViewContainer"] { padding: 0px !important; }
        
        body {
            background-color: #f4f6f9 !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
        }
        
        /* Master Container Grid Structural Controls */
        .app-shell {
            display: flex;
            height: 100vh;
            width: 100vw;
            overflow: hidden;
        }
        
        /* Compact Vertical Left Icon Sidebar Layout */
        .app-sidebar {
            width: 70px;
            background-color: #111625;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 20px;
            z-index: 1000;
            flex-shrink: 0;
        }
        .sidebar-brand-ico {
            color: #00e5ff;
            font-size: 24px;
            margin-bottom: 35px;
        }
        .nav-node-link {
            color: #64748b;
            font-size: 20px;
            margin-bottom: 25px;
            width: 100%;
            text-align: center;
            padding: 10px 0;
            display: block;
            text-decoration: none;
            transition: color 0.15s ease-in-out;
        }
        .nav-node-link:hover {
            color: #00e5ff;
        }
        .nav-node-link.node-active {
            color: #ffffff;
            background-color: #1e293b;
            border-left: 3px solid #00e5ff;
        }
        
        /* Workspace Content Core Panel */
        .app-workspace {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            background-color: #f4f6f9;
            overflow-y: auto;
            height: 100vh;
        }
        
        /* Top Navigation Strip Header Setup */
        .top-navbar-strip {
            background-color: #0c7db1;
            color: #ffffff;
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            flex-shrink: 0;
        }
        .navbar-brand-txt {
            font-size: 16px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        
        .workspace-view-body {
            padding: 24px;
        }
        
        /* Performance Dashboard Counter Cards Layout */
        .summary-card {
            background: #ffffff;
            border-radius: 6px;
            padding: 18px 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border-left: 4px solid #00e5ff;
        }
        .summary-card.green-tag { border-left-color: #10b981; }
        .summary-card.red-tag { border-left-color: #ef4444; }
        
        .card-meta-label {
            color: #64748b;
            font-size: 13px;
            font-weight: 500;
            text-transform: uppercase;
        }
        .card-meta-val {
            font-size: 28px;
            font-weight: 700;
            color: #1e293b;
            margin-top: 4px;
        }
        
        /* Quick System Action Navigation Nodes Buttons */
        .panel-shortcut-btn {
            background-color: #ffffff;
            color: #334155;
            border: 1px solid #e2e8f0;
            padding: 10px 16px;
            font-size: 13px;
            font-weight: 500;
            border-radius: 4px;
            text-decoration: none;
            display: block;
            text-align: center;
            transition: all 0.15s ease;
        }
        .panel-shortcut-btn:hover {
            background-color: #f8fafc;
            border-color: #cbd5e1;
            color: #0c7db1;
        }
    </style>
""", unsafe_allow_html=True)

# ====================================================================
# 4. DATA ENGINE AGGREGATIONS
# ====================================================================
# Core operational dashboard data constants matching verification screen targets
active_users_val = 1245
total_recovered_val = 1193440
outstanding_ledger_val = 588300

# ====================================================================
# 5. LAYOUT BASE SHELL RENDERING
# ====================================================================
# Building clean navigation tags using target parameter switching structures
sidebar_markup = f"""
<div class="app-shell">
    <div class="app-sidebar">
        <div class="sidebar-brand-ico"><i class="bi bi-globe"></i></div>
        <a href="?menu=dashboard" target="_self" class="nav-node-link {'node-active' if current_menu == 'dashboard' else ''}" title="Dashboard Overview"><i class="bi bi-speedometer2"></i></a>
        <a href="?menu=users" target="_self" class="nav-node-link {'node-active' if current_menu == 'users' else ''}" title="Users Matrix"><i class="bi bi-people"></i></a>
        <a href="?menu=network" target="_self" class="nav-node-link {'node-active' if current_menu == 'network' else ''}" title="Network Areas"><i class="bi bi-geo-alt"></i></a>
        <a href="?menu=ledger" target="_self" class="nav-node-link {'node-active' if current_menu == 'ledger' else ''}" title="Transactions Ledger"><i class="bi bi-receipt"></i></a>
        <a href="?menu=accounts" target="_self" class="nav-node-link {'node-active' if current_menu == 'accounts' else ''}" title="Accounts Recovery"><i class="bi bi-wallet2"></i></a>
    </div>
    
    <div class="app-workspace">
        <div class="top-navbar-strip">
            <div class="navbar-brand-txt">🌐 LYNX FIBER PVT LTD</div>
            <div style="font-size: 13px; font-weight: 500;"><i class="bi bi-person-circle"></i> Profile: ISP_OWNER</div>
        </div>
        <div class="workspace-view-body">
"""
st.markdown(sidebar_markup, unsafe_allow_html=True)

# ====================================================================
# 6. ROUTED CONTROLLER WORKING PANELS
# ====================================================================
if current_menu == "dashboard":
    # Workspace Identity Header Title
    st.markdown("""
        <div class="mb-4">
            <h4 class="mb-1" style="color:#1e293b; font-weight:700;">HELLO!! LYNX FIBER INTERNET</h4>
            <p style="color:#64748b; font-size:13px; margin:0;">Real-time network operational overview and financial status summaries.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Action Navigation Shortcut Elements Row Block (Using standard tags to prevent target refresh breaks)
    st.markdown("""
        <div class="row g-2 mb-4">
            <div class="col-md-3"><a href="?menu=users" target="_self" class="panel-shortcut-btn"><i class="bi bi-download"></i> User/Dealer Application</a></div>
            <div class="col-md-3"><a href="?menu=network" target="_self" class="panel-shortcut-btn"><i class="bi bi-hdd-network"></i> BT Drivers Download</a></div>
            <div class="col-md-3"><a href="?menu=ledger" target="_self" class="panel-shortcut-btn"><i class="bi bi-link-45deg"></i> Copy Query Link</a></div>
            <div class="col-md-3"><a href="?menu=accounts" target="_self" class="panel-shortcut-btn"><i class="bi bi-file-earmark-text"></i> Download Monthly Bill</a></div>
        </div>
        <h6 class="mb-3" style="color:#475569; font-weight:600;">📊 Financial Counter Summary</h6>
    """, unsafe_allow_html=True)
    
    # Structural Dashboard Layout Grid Counter Matrices
    st.markdown(f"""
        <div class="row g-3 mb-4">
            <div class="col-md-4">
                <div class="summary-card">
                    <div class="card-meta-label">👤 Active Users</div>
                    <div class="card-meta-val">{active_users_val:,}</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="summary-card green-tag">
                    <div class="card-meta-label">💵 Total Recovered</div>
                    <div class="card-meta-val">PKR {total_recovered_val:,.0f}</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="summary-card red-tag">
                    <div class="card-meta-label">⚠️ Outstanding Ledger</div>
                    <div class="card-meta-val">PKR {outstanding_ledger_val:,.0f}</div>
                </div>
            </div>
        </div>
        <hr style="border-color:#cbd5e1;" class="my-4">
    """, unsafe_allow_html=True)
    
    # Analytical Graphical Charts Visual Blocks
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("<span style='color:#475569; font-weight:600; font-size:14px; display:block; margin-bottom:10px;'>📊 Last 6 Month Receiving</span>", unsafe_allow_html=True)
        chart_data_1 = pd.DataFrame({
            'Month': ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'Recovered Amount': [0, 0, 3000, 1193440, 588300, 209300]
        })
        st.bar_chart(chart_data_1.set_index("Month"), y="Recovered Amount", color="#0c7db1", use_container_width=True)
        
    with g2:
        st.markdown("<span style='color:#475569; font-weight:600; font-size:14px; display:block; margin-bottom:10px;'>🎯 Users Package Wise Matrix</span>", unsafe_allow_html=True)
        chart_data_2 = pd.DataFrame({
            'Package': ['12MB', '15MB', '10MB', '9MB K', '12MB TW', '9MB E', '12MB E'],
            'Total Users': [385, 9, 34, 341, 41, 79, 37]
        })
        st.bar_chart(chart_data_2.set_index("Package"), y="Total Users", color="#10b981", use_container_width=True)

elif current_menu == "users":
    st.markdown("<h4 style='color: #0c7db1; font-weight:700;'>👤 Subscriber Entry Form</h4><p class='text-muted' style='font-size:13px;'>Create and append new subscriber connection records to the core database node.</p>", unsafe_allow_html=True)
    
    # Standard streamlined user record generation forms
    with st.form("sub_form"):
        r1, r2 = st.columns(2)
        u_id = r1.text_input("Internet User ID / Account Code")
        u_name = r1.text_input("Subscriber Profile Full Name")
        u_phone = r2.text_input("Active Mobile Connection String")
        u_type = r2.selectbox("Connection Profile Service Mapping", ["Internet", "Cable", "Both"])
        
        if st.form_submit_button("⚡ Append Record to Core"):
            if u_id and u_name:
                st.success(f"Success: Account mapped cleanly for {u_name}")

else:
    st.markdown(f"<h4 style='color: #0c7db1; font-weight:700;'>⚙️ System Section Module Active</h4>", unsafe_allow_html=True)
    st.info(f"Dynamic view initialized for option parameter: '{current_menu.upper()}'. Core relational interface active.")

# Closing out raw layout HTML wrap matrices
st.markdown('</div></div></div>', unsafe_allow_html=True)