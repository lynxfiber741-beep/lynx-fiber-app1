import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ====================================================================
# CONFIGURATION & EXACT PREMIUM APP MATCH THEME
# ====================================================================
st.set_page_config(
    page_title="Lynx Fiber Pvt Ltd - Dashboard",
    page_icon="🌐",
    layout="wide", 
    initial_sidebar_state="expanded"
)

DB_FILE = "wasoolee_core_pro.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- INJECTED DESIGN SYSTEM (EXACT MATCHING app121.wasooli.pk) ---
st.markdown("""
    <style>
        /* Top Header Strip Blue Color Match */
        [data-testid="stHeader"] {
            background-color: #0c7db1 !important;
        }
        /* Left Custom Dark Professional Sidebar */
        [data-testid="stSidebar"] {
            background-color: #1a222d !important;
            border-right: 1px solid #2d3748 !important;
        }
        /* Title text optimization */
        .company-header-title {
            color: #00e5ff;
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 5px;
            font-family: sans-serif;
        }
        .role-badge {
            color: #a0aec0;
            font-size: 13px;
            margin-bottom: 20px;
        }
        /* Financial Counter Boxes Style */
        .metric-card {
            background-color: #242f3d;
            border-left: 4px solid #00e5ff;
            padding: 18px;
            border-radius: 6px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.15);
            margin-bottom: 15px;
        }
        /* Buttons design matching original dashboard */
        .stButton>button {
            background-color: #0c7db1 !important;
            color: white !important;
            border-radius: 4px !important;
            border: none !important;
        }
    </style>
""", unsafe_allow_html=True)


# ====================================================================
# BACKEND: AUTOMATED INITIALIZATION (COMPLETED BACKEND ENGINE)
# ====================================================================
def build_wasoolee_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saas_companies (
            company_id TEXT PRIMARY KEY, admin_username TEXT UNIQUE, admin_password TEXT NOT NULL, company_name TEXT, status TEXT DEFAULT 'Active'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS network_areas (
            area_id INTEGER PRIMARY KEY AUTOINCREMENT, company_id TEXT, area_name TEXT NOT NULL, FOREIGN KEY(company_id) REFERENCES saas_companies(company_id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, company_id TEXT, custom_cust_id TEXT NOT NULL, name TEXT NOT NULL, cell_no TEXT, address TEXT, connection_type TEXT, package_internet TEXT, internet_amount REAL DEFAULT 0, package_cable TEXT, cable_amount REAL DEFAULT 0, area_id INTEGER, status TEXT DEFAULT 'Active', FOREIGN KEY(company_id) REFERENCES saas_companies(company_id) ON DELETE CASCADE, FOREIGN KEY(area_id) REFERENCES network_areas(area_id) ON DELETE SET NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices_ledger (
            invoice_id INTEGER PRIMARY KEY AUTOINCREMENT, company_id TEXT, custom_cust_id TEXT, billing_month TEXT, previous_dues REAL DEFAULT 0, current_bill REAL DEFAULT 0, total_payable REAL DEFAULT 0, amount_paid REAL DEFAULT 0, payment_status TEXT DEFAULT 'Unpaid'
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM saas_companies WHERE company_id='lynx_fiber'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO saas_companies VALUES ('lynx_fiber', 'lynxadmin', 'lynx786', 'Lynx Fiber Pvt Ltd', 'Active')")
        cursor.execute("INSERT INTO network_areas (company_id, area_name) VALUES ('lynx_fiber', 'Sanghoi System')")
        cursor.execute("INSERT INTO network_areas (company_id, area_name) VALUES ('lynx_fiber', 'Saeela System')")
    conn.commit()
    conn.close()

build_wasoolee_tables()

current_company = "lynx_fiber"


# ====================================================================
# SIDEBAR PANEL BRANDING & NAVIGATION DOCK
# ====================================================================
# Custom Brand Injection instead of generic labels
st.sidebar.markdown('<div class="company-header-title">🌐 Lynx Fiber Pvt Ltd</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="role-badge">Authenticated Role: <b>ISP_OWNER</b></div>', unsafe_allow_html=True)

st.sidebar.write("---")

# Clean vertical system navigation nodes
menu_selection = st.sidebar.radio(
    "🎛️ CONTROL PROFILE",
    [
        "📊 Dashboard Overview",
        "👤 Provision Subscriber",
        "📍 Manage Network Areas",
        "📋 Live Subscriber Directory",
        "⚙️ Run Monthly Billing",
        "💰 Recovery & Accounts Ledger"
    ],
    label_visibility="collapsed"
)

st.sidebar.write("---")
if st.sidebar.button("🔒 Secure Log Out", use_container_width=True):
    st.info("Session token released.")


# ====================================================================
# MAIN APPLICATION WORKFLOW ROUTER
# ====================================================================

# MODULE 1: MAIN GRAPHICAL INTERFACE DASHBOARD
if menu_selection == "📊 Dashboard Overview":
    st.markdown("<h2 style='color: #0c7db1;'>HELLO!! LYNX FIBER INTERNET</h2>", unsafe_allow_html=True)
    st.write("Real-time network operational overview and financial status summaries.")
    
    # Custom Application Navigation Shortcuts Grid
    c1, c2, c3, c4 = st.columns(4)
    c1.button("📥 User/Dealer Application", use_container_width=True)
    c2.button("💾 BT Drivers Download", use_container_width=True)
    c3.button("🔗 Copy Query Link", use_container_width=True)
    c4.button("🧾 Download Monthly Bill", use_container_width=True)
    
    st.write("---")
    
    # Financial Engine calculations
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM subscribers WHERE company_id=?", (current_company,))
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(total_payable), SUM(amount_paid) FROM invoices_ledger WHERE company_id=?", (current_company,))
    fin_data = cursor.fetchone()
    recv = float(fin_data[0]) if fin_data and fin_data[0] else 0.0
    paid = float(fin_data[1]) if fin_data and fin_data[1] else 0.0
    outst = recv - paid
    conn.close()

    # Premium Dashboard Counters Grid Row
    st.markdown("#### 📈 Financial Counter Summary")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="metric-card"><p style="color: #cbd5e0; margin:0; font-size:14px;">👤 Active Users</p><h2 style="color: #48bb78; margin:5px 0 0 0;">{total_users:,}</h2></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><p style="color: #cbd5e0; margin:0; font-size:14px;">💵 Total Recovered</p><h2 style="color: #00e5ff; margin:5px 0 0 0;">PKR {paid:,.2f}</h2></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><p style="color: #cbd5e0; margin:0; font-size:14px;">⚠️ Outstanding Ledger</p><h2 style="color: #f56565; margin:5px 0 0 0;">PKR {outst:,.2f}</h2></div>', unsafe_allow_html=True)
        
    st.write("---")
    
    # Analytical Visualizations
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("##### 📊 Last 6 Month Receiving")
        conn = get_db_connection()
        m_df = pd.read_sql_query("SELECT billing_month as [Month], SUM(amount_paid) as [Recovered Amount] FROM invoices_ledger WHERE company_id=? GROUP BY billing_month", conn, params=(current_company,))
        conn.close()
        if not m_df.empty:
            st.bar_chart(m_df.set_index("Month"), y="Recovered Amount", color="#0c7db1", use_container_width=True)
        else:
            st.info("Ledger records are currently empty. Visual metrics waiting for billing generation.")
        
    with g2:
        st.markdown("##### 🎯 Users Package Wise Matrix")
        conn = get_db_connection()
        p_df = pd.read_sql_query("SELECT package_internet as [Package Profile], COUNT(*) as [Total Users] FROM subscribers WHERE company_id=? GROUP BY package_internet", conn, params=(current_company,))
        conn.close()
        if not p_df.empty and p_df["Package Profile"].iloc[0] is not None:
            st.bar_chart(p_df.set_index("Package Profile"), y="Total Users", color="#48bb78", use_container_width=True)
        else:
            st.info("Subscriber configuration database index empty.")

# MODULE 2: SUBSCRIBER PROVISION PROTOCOL
elif menu_selection == "👤 Provision Subscriber":
    st.markdown("<h3 style='color: #00e5ff;'>📝 Subscriber Entry Protocol</h3>", unsafe_allow_html=True)
    
    conn = get_db_connection()
    areas_df = pd.read_sql_query("SELECT * FROM network_areas WHERE company_id=?", conn, params=(current_company,))
    conn.close()
    
    if areas_df.empty:
        st.warning("Pehle 'Manage Network Areas' node mein ja kar system sectors add karein.")
    else:
        area_mapping = dict(zip(areas_df["area_name"], areas_df["area_id"]))
        
        with st.form("sub_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                cust_id = st.text_input("Internet User ID / Custom Account ID (Unique)")
                name = st.text_input("Subscriber Full Name")
                cell = st.text_input("Cell Phone Number")
            with col2:
                sel_area = st.selectbox("Sublocality / Operational System Network", options=list(area_mapping.keys()))
                conn_type = st.selectbox("Connection Service Type", options=["Internet", "Cable", "Both"])
                addr = st.text_area("Installation Physical Address")
                
            st.markdown("#### 💰 Tariff Rates & Package Architecture Setup")
            p1, p2 = st.columns(2)
            with p1:
                p_net = st.text_input("Internet Package Profile Name (e.g., 20 Mbps Premium)")
                a_net = st.number_input("Monthly Internet Base Rate (PKR)", min_value=0.0)
            with p2:
                p_cab = st.text_input("Cable TV Package Profile Name")
                a_cab = st.number_input("Monthly Cable Base Rate (PKR)", min_value=0.0)
                
            if st.form_submit_button("⚡ Finalize & Write Subscriber Node"):
                if cust_id and name:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO subscribers (company_id, custom_cust_id, name, cell_no, address, connection_type, package_internet, internet_amount, package_cable, cable_amount, area_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                                   (current_company, cust_id, name, cell, addr, conn_type, p_net, a_net, p_cab, a_cab, area_mapping[sel_area]))
                    conn.commit()
                    conn.close()
                    st.success(f"Subscriber node updated! Asset created for {name}.")
                    st.rerun()

# MODULE 3: MANAGE SYSTEM NETWORK SECTORS
elif menu_selection == "📍 Manage Network Areas":
    st.markdown("<h3 style='color: #00e5ff;'>📍 Regional Network Node Architecture</h3>", unsafe_allow_html=True)
    col_in, col_vi = st.columns([1, 1.5])
    
    with col_in:
        with st.form("area_f", clear_on_submit=True):
            a_name = st.text_input("New System Node Name (e.g., Sanghoi System)")
            if st.form_submit_button("Deploy Sector Node") and a_name:
                conn = get_db_connection()
                conn.cursor().execute("INSERT INTO network_areas (company_id, area_name) VALUES (?, ?)", (current_company, a_name))
                conn.commit()
                conn.close()
                st.success("Network node database mapped!")
                st.rerun()
    with col_vi:
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT area_id as [Node ID], area_name as [Active System Sector] FROM network_areas WHERE company_id=?", conn, params=(current_company,))
        conn.close()
        st.dataframe(df, use_container_width=True, hide_index=True)

# MODULE 4: MASTER DIRECTORY LIVE DISPLAY
elif menu_selection == "📋 Live Subscriber Directory":
    st.markdown("<h3 style='color: #00e5ff;'>📋 Live Subscriber Master Directory</h3>", unsafe_allow_html=True)
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT custom_cust_id as [User ID], name as [Full Name], cell_no as [Phone], connection_type as [Service], (internet_amount+cable_amount) as [Tariff Rate (PKR)] FROM subscribers WHERE company_id=?", conn, params=(current_company,))
    conn.close()
    st.dataframe(df, use_container_width=True, hide_index=True)

# MODULE 5: MASS BILLING AUTOMATION MACHINE
elif menu_selection == "⚙️ Run Monthly Billing":
    st.markdown("<h3 style='color: #00e5ff;'>⚙️ Automated Monthly Invoicing System</h3>", unsafe_allow_html=True)
    target_m = st.selectbox("Select Target Billing Month Cycle", options=["May 2026", "June 2026", "July 2026"])
    
    if st.button("🚀 Trigger Bulk Invoicing Run Over Active Nodes", use_container_width=True):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subscribers WHERE company_id=?", (current_company,))
        subs = cursor.fetchall()
        
        for s in subs:
            bill = float(s["internet_amount"] or 0) + float(s["cable_amount"] or 0)
            cursor.execute("INSERT INTO invoices_ledger (company_id, custom_cust_id, billing_month, previous_dues, current_bill, total_payable, amount_paid, payment_status) VALUES (?, ?, ?, 0.0, ?, ?, 0.0, 'Unpaid')",
                           (current_company, s["custom_cust_id"], target_m, bill, bill))
        conn.commit()
        conn.close()
        st.success("Batch invoice system protocol complete.")

# MODULE 6: ACCOUNT RECOVERY CONTROL MATRIX
elif menu_selection == "💰 Recovery & Accounts Ledger":
    st.markdown("<h3 style='color: #00e5ff;'>💰 Central Accounts Recovery Ledger</h3>", unsafe_allow_html=True)
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT invoice_id as [Inv ID], custom_cust_id as [Account ID], billing_month as [Month Cycle], current_bill as [Base Charge], total_payable as [Net Demand], amount_paid as [Cash Recovered], payment_status as [System Status] FROM invoices_ledger WHERE company_id=?", conn, params=(current_company,))
    conn.close()
    st.dataframe(df, use_container_width=True, hide_index=True)