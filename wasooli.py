import streamlit as st
import pandas as pd

# ====================================================================
# 1. ROOT VIEWPORT CONFIGURATION
# ====================================================================
st.set_page_config(
    page_title="Lynx Fiber Pvt Ltd",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- MASTER LAYOUT & SIDEBAR STYLE CLEAN OVERRIDE ---
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
    
    <style>
        /* Streamlit raw interface hide rules */
        [data-testid="stHeader"], footer, #MainMenu { display: none !important; visibility: hidden; }
        .block-container { padding: 0rem !important; max-width: 100% !important; margin: 0 !important; }
        [data-testid="stAppViewContainer"] { padding: 0px !important; background-color: #f4f6f9; }
        
        /* Fixed Horizontal Blue Brand Ribbon */
        .top-brand-ribbon {
            background-color: #0c7db1;
            color: #ffffff;
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            position: fixed;
            top: 0; left: 70px; right: 0;
            height: 50px;
            z-index: 999;
        }
        
        /* Left Fixed Icon Strip Container */
        .left-icon-dock {
            width: 70px;
            background-color: #111625;
            position: fixed;
            top: 0; bottom: 0; left: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 15px;
            z-index: 1000;
        }
        
        /* Safe Workspace Rendering Area padding adjustment */
        .workspace-core-body {
            margin-left: 70px;
            margin-top: 50px;
            padding: 24px;
            background-color: #f4f6f9;
            min-height: calc(100vh - 50px);
        }

        /* Compact Financial Matrices Setup */
        .summary-card {
            background: #ffffff;
            border-radius: 6px;
            padding: 18px 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border-left: 4px solid #00e5ff;
        }
        .summary-card.green-tag { border-left-color: #10b981; }
        .summary-card.red-tag { border-left-color: #ef4444; }
        .card-meta-label { color: #64748b; font-size: 13px; font-weight: 500; text-transform: uppercase; }
        .card-meta-val { font-size: 28px; font-weight: 700; color: #1e293b; margin-top: 4px; }
    </style>
""", unsafe_allow_html=True)

# ====================================================================
# 2. STATE PERSISTENCE ENGINE (ROUTING CONTROLLER)
# ====================================================================
if "active_panel" not in st.session_state:
    st.session_state.active_panel = "dashboard"

# ====================================================================
# 3. INTERFACE BRAND RIBBON & SIDEBAR GENERATION
# ====================================================================
# Horizontal Ribbon Content Layout
st.markdown("""
    <div class="top-brand-ribbon">
        <div style="font-size:16px; font-weight:600; letter-spacing:0.5px;">🌐 LYNX FIBER PVT LTD</div>
        <div style="font-size:13px; font-weight:500;"><i class="bi bi-person-circle"></i> Profile: ISP_OWNER</div>
    </div>
""", unsafe_allow_html=True)

# Sidebar Native Interactive Buttons Layer Structure
with st.container():
    st.markdown('<div class="left-icon-dock">', unsafe_allow_html=True)
    st.markdown('<div style="color:#00e5ff; font-size:24px; margin-bottom:30px;"><i class="bi bi-globe"></i></div>', unsafe_allow_html=True)
    
    # Interactive Native Streamlit Buttons Styled Invisibly onto Dock
    if st.button("📊", key="btn_dash", help="Dashboard View", use_container_width=True):
        st.session_state.active_panel = "dashboard"
    if st.button("👥", key="btn_users", help="Subscriber Base Profiles", use_container_width=True):
        st.session_state.active_panel = "users"
    if st.button("📍", key="btn_network", help="Network Node Sectors", use_container_width=True):
        st.session_state.active_panel = "network"
    if st.button("📈", key="btn_ledger", help="Ledger Ledger System", use_container_width=True):
        st.session_state.active_panel = "ledger"
        
    st.markdown('</div>', unsafe_allow_html=True)

# ====================================================================
# 4. WORKSPACE DATA DISPLAY DISPATCHER
# ====================================================================
st.markdown('<div class="workspace-core-body">', unsafe_allow_html=True)

if st.session_state.active_panel == "dashboard":
    # Screen Welcome Banner Header
    st.markdown("""
        <div class="mb-4">
            <h4 class="mb-1" style="color:#1e293b; font-weight:700;">HELLO!! LYNX FIBER INTERNET</h4>
            <p style="color:#64748b; font-size:13px; margin:0;">Real-time network operational overview and financial status summaries.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Operation Commands Rows
    c1, c2, c3, c4 = st.columns(4)
    c1.button("📥 User/Dealer Application", key="app_dl", use_container_width=True)
    c2.button("💾 BT Drivers Download", key="bt_dl", use_container_width=True)
    c3.button("🔗 Copy Query Link", key="cp_lnk", use_container_width=True)
    c4.button("🧾 Download Monthly Bill", key="dw_bl", use_container_width=True)
    
    st.markdown("<br><h6 class='mb-3' style='color:#475569; font-weight:600;'>📊 Financial Counter Summary</h6>", unsafe_allow_html=True)
    
    # Matching Screen Core Financial KPI Indicators Grid Box Row
    card_r1, card_r2, card_r3 = st.columns(3)
    with card_r1:
        st.markdown('<div class="summary-card"><div class="card-meta-label">👤 Active Users</div><div class="card-meta-val">1,245</div></div>', unsafe_allow_html=True)
    with card_r2:
        st.markdown('<div class="summary-card green-tag"><div class="card-meta-label">💵 Total Recovered</div><div class="card-meta-val">PKR 1,193,440</div></div>', unsafe_allow_html=True)
    with card_r3:
        st.markdown('<div class="summary-card red-tag"><div class="card-meta-label">⚠️ Outstanding Ledger</div><div class="card-meta-val">PKR 588,300</div></div>', unsafe_allow_html=True)
        
    st.markdown("<hr style='border-color:#cbd5e1;' class='my-4'>", unsafe_allow_html=True)
    
    # Charts Structural Data Blocks
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

elif st.session_state.active_panel == "users":
    st.markdown("<h4 style='color:#0c7db1; font-weight:700;'>👤 Subscriber Profile Core Directory</h4><br>", unsafe_allow_html=True)
    with st.form("sub_entry_form"):
        r1, r2 = st.columns(2)
        r1.text_input("Internet User ID / Custom Account ID")
        r1.text_input("Subscriber Profile Name")
        r2.text_input("Active Mobile Connection")
        r2.selectbox("Connection Profile Type", ["Internet", "Cable", "Both"])
        st.form_submit_button("⚡ Append Record to Core")

else:
    st.markdown(f"<h4 style='color:#0c7db1;'>⚙️ Operational Control Module Active</h4>", unsafe_allow_html=True)
    st.info(f"System profile section mapped securely. Relational infrastructure active.")

st.markdown('</div>', unsafe_allow_html=True)