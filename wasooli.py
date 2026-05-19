import streamlit as st
import pandas as pd

# ====================================================================
# 1. ROOT HARDWARE ENGINE CONFIGURATION
# ====================================================================
st.set_page_config(
    page_title="Lynx Fiber Pvt Ltd",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded" # Sidebar system structural grid lock
)

# --- GLOBAL STYLING LAYER FOR EXACT UI SYNCHRONIZATION ---
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
    
    <style>
        /* 1. Reset Native Top Header Block padding spaces */
        [data-testid="stHeader"] {
            background-color: #0c7db1 !important;
            height: 3.5rem !important;
            z-index: 99;
        }
        
        /* 2. Lock Left Sidebar Width & Deep Slate Dark Background Color */
        [data-testid="stSidebar"] {
            background-color: #111625 !important;
            min-width: 85px !important;
            max-width: 85px !important;
            border-right: 1px solid #1e293b !important;
        }
        
        /* 3. Strip out default spacing wrapper paddings inside workspace container */
        .block-container {
            padding: 1.5rem 2rem !important;
            max-width: 100% !important;
        }
        
        /* 4. Custom Component Overrides for Compact Navigation Row Buttons */
        div.stButton > button {
            background-color: #1e293b !important;
            color: #94a3b8 !important;
            border: 1px solid #334155 !important;
            font-size: 20px !important;
            padding: 12px 0px !important;
            border-radius: 6px !important;
            transition: all 0.2s ease;
            margin-bottom: 5px;
        }
        div.stButton > button:hover {
            color: #00e5ff !important;
            border-color: #00e5ff !important;
            background-color: #111625 !important;
        }
        /* Highlight active link indicator block element state */
        div.stButton > button:focus, div.stButton > button:active {
            color: #ffffff !important;
            background-color: #0c7db1 !important;
            border-color: #00e5ff !important;
            box-shadow: none !important;
        }

        /* 5. Compact Financial Counter Display Layout Grid Cards */
        .kpi-card {
            background: #ffffff;
            border-radius: 6px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border-left: 4px solid #00e5ff;
        }
        .kpi-card.green-tag { border-left-color: #10b981; }
        .kpi-card.red-tag { border-left-color: #ef4444; }
        .kpi-label { color: #64748b; font-size: 13px; font-weight: 500; text-transform: uppercase; }
        .kpi-val { font-size: 26px; font-weight: 700; color: #1e293b; margin-top: 4px; }
    </style>
""", unsafe_allow_html=True)

# ====================================================================
# 2. STATE STORAGE PERSISTENCE PROTOCOL
# ====================================================================
if "current_panel" not in st.session_state:
    st.session_state.current_panel = "dashboard"

# ====================================================================
# 3. COMPACT ICON SIDEBAR CORE ENGINE
# ====================================================================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 20px 0; border-bottom: 1px solid #1e293b; margin-bottom: 20px;">
            <span style="color:#00e5ff; font-size:24px;"><i class="bi bi-globe"></i></span>
        </div>
    """, unsafe_allow_html=True)
    
    # Micro layout single key button tags matching custom panel matrix look
    if st.button("📊", key="side_dash", help="Dashboard Overview Profile", use_container_width=True):
        st.session_state.current_panel = "dashboard"
        
    if st.button("👥", key="side_users", help="Subscriber Operations profiles", use_container_width=True):
        st.session_state.current_panel = "users"
        
    if st.button("📍", key="side_net", help="Regional Operational Systems", use_container_width=True):
        st.session_state.current_panel = "network"
        
    if st.button("📈", key="side_ledger", help="Financial Ledger Database", use_container_width=True):
        st.session_state.current_panel = "ledger"

# ====================================================================
# 4. MASTER WORKSPACE ELEMENT ROUTER
# ====================================================================

# Top Header Information String Block
st.markdown("""
    <div style="background-color: #0c7db1; color: white; padding: 10px 20px; margin: -1.5rem -2rem 1.5rem -2rem; display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 15px; font-weight: 600; letter-spacing: 0.5px;">🌐 LYNX FIBER PVT LTD</span>
        <span style="font-size: 12px;"><i class="bi bi-person-circle"></i> Role: ISP_OWNER Dashboard</span>
    </div>
""", unsafe_allow_html=True)

if st.session_state.current_panel == "dashboard":
    # Workspace Subtitle Banner
    st.markdown("""
        <div class="mb-4">
            <h4 class="mb-1" style="color:#1e293b; font-weight:700;">HELLO!! LYNX FIBER INTERNET</h4>
            <p style="color:#64748b; font-size:13px; margin:0;">Real-time network operational overview and financial status summaries.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Row Layout for System Quick Trigger Option Buttons
    b1, b2, b3, b4 = st.columns(4)
    b1.button("📥 User/Dealer Application", key="sh_app", use_container_width=True)
    b2.button("💾 BT Drivers Download", key="sh_bt", use_container_width=True)
    b3.button("🔗 Copy Query Link", key="sh_lnk", use_container_width=True)
    b4.button("🧾 Download Monthly Bill", key="sh_bill", use_container_width=True)
    
    st.markdown("<br><h6 class='mb-3' style='color:#475569; font-weight:600;'>📊 Financial Counter Summary</h6>", unsafe_allow_html=True)
    
    # Financial Numeric Box Framework Matrix Setup
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="kpi-card"><div class="kpi-label">👤 Active Users</div><div class="kpi-val">1,245</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="kpi-card green-tag"><div class="kpi-label">💵 Total Recovered</div><div class="kpi-val">PKR 1,193,440</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="kpi-card red-tag"><div class="kpi-label">⚠️ Outstanding Ledger</div><div class="kpi-val">PKR 588,300</div></div>', unsafe_allow_html=True)
        
    st.markdown("<hr style='border-color:#cbd5e1;' class='my-4'>", unsafe_allow_html=True)
    
    # Visual Analytical Operational Performance Graphs Layout
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

elif st.session_state.current_panel == "users":
    st.markdown("<h4 style='color:#0c7db1; font-weight:700;'>👤 Subscriber Management Protocol</h4>", unsafe_allow_html=True)
    with st.form("sub_form_node"):
        r1, r2 = st.columns(2)
        r1.text_input("Account ID / System Code")
        r1.text_input("Subscriber Profile Name")
        r2.text_input("Active Mobile Connection String")
        r2.selectbox("Provision Service Type Line", ["Internet", "Cable", "Both"])
        st.form_submit_button("⚡ Append Record to Cloud Node")