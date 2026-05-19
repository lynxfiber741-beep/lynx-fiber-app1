import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import urllib.parse

# --- ENTERPRISE THEME CONFIGURATION (MODERN CYBER DARK) ---
st.set_page_config(
    page_title="Lynx Fiber Pvt Ltd - Core BSS Suite", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Custom CSS Injection for Premium Look & Feel
st.markdown("""
    <style>
    /* Main Background & Fonts */
    .stApp {
        background: radial-gradient(circle, #0d1117 0%, #07090e 100%);
        color: #e6edf3;
    }
    /* Metric Cards Styling */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #00ffd2 !important;
        font-family: 'Courier New', monospace;
    }
    div[data-testid="stMetricLabel"] {
        color: #8b949e !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    /* Custom Container Blocks */
    .element-container div.stMarkdown div {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Glassmorphism Dynamic Cards */
    .customer-card {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    .customer-card:hover {
        border-color: #00ffd2;
        box-shadow: 0 4px 20px rgba(0, 255, 210, 0.15);
    }
    /* Badges */
    .badge-active {
        background-color: rgba(46, 160, 67, 0.15);
        color: #3fb950;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        border: 1px solid rgba(46, 160, 67, 0.3);
    }
    .badge-expired {
        background-color: rgba(248, 81, 73, 0.15);
        color: #f85149;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        border: 1px solid rgba(248, 81, 73, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# ==================== 1. CORE ROBUST SQL DATABASE ENGINE ====================
DB_FILE = "lynx_core_engine.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_core_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Grid Sectors Master Table
    cursor.execute('CREATE TABLE IF NOT EXISTS sectors (id INTEGER PRIMARY KEY AUTOINCREMENT, sector_name TEXT UNIQUE)')
    
    # Security Credentials Registry Table
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, full_name TEXT, assigned_sector TEXT)')
    
    # Master Client Loops Table (Hardware Nodes Coupled)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id TEXT PRIMARY KEY, name TEXT, phone TEXT, sector TEXT, package TEXT, 
            tariff INTEGER, date_joined TEXT, date_expiry TEXT, olt_pon TEXT, splitter TEXT
        )
    ''')
    
    # Vault Transactions Ledger (Lifetime Billing Data)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT, client_id TEXT, timestamp TEXT, 
            amount_paid INTEGER, billing_period TEXT, operator TEXT
        )
    ''')
    
    # Internal Operational Expenditures Table
    cursor.execute('CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, amount INTEGER, date_logged TEXT)')
    
    # Seed Initial Safe Protocols if System is Empty
    cursor.execute("SELECT COUNT(*) FROM sectors")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO sectors (sector_name) VALUES ('Sanghoi')")
        cursor.execute("INSERT INTO sectors (sector_name) VALUES ('Saeela')")
        cursor.execute("INSERT INTO sectors (sector_name) VALUES ('Jhelum Center')")
        
        cursor.execute("INSERT INTO users VALUES ('ali123', '1122', 'Ali Raza', 'Sanghoi')")
        cursor.execute("INSERT INTO users VALUES ('usman456', '4455', 'Usman Khan', 'Saeela')")
        
        cursor.execute("INSERT INTO clients VALUES ('LX-101', 'Zahid Mehmood', '+923001234567', 'Sanghoi', '10 Mbps', 1500, '2025-06-10', '2026-05-15', 'OLT-01_PON-3', '1:8-Spl_02')")
        cursor.execute("INSERT INTO clients VALUES ('LX-102', 'Raja Naeem', '+923129876543', 'Saeela', '20 Mbps', 2500, '2025-11-01', '2026-05-28', 'OLT-02_PON-1', '1:16-Spl_01')")
        
        cursor.execute("INSERT INTO ledger (client_id, timestamp, amount_paid, billing_period, operator) VALUES ('LX-101', '2026-04-12', 1500, 'April 2026', 'ali123')")
        cursor.execute("INSERT INTO expenses (description, amount, date_logged) VALUES ('Main Generator Fuel', 3500, '2026-05-10')")
    
    conn.commit()
    conn.close()

init_core_db()

# ==================== 2. ADVANCED TOKEN SESSION SECURITY ====================
if "session_token" not in st.session_state:
    st.session_state["session_token"] = {"auth": False, "role": None, "user": None, "scope": None}

if not st.session_state["session_token"]["auth"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
            <div style='text-align: center;'>
                <h1 style='color: #00ffd2; font-family: monospace; letter-spacing: 2px;'>⚡ LYNX FIBER PVT LTD</h1>
                <p style='color: #8b949e;'>Broadband Operation Support System (BOSS) Gateway</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            s_user = st.text_input("Identity Token / Username").strip()
            s_pass = st.text_input("Access PIN / Password", type="password").strip()
            auth_btn = st.button("Unlock Enterprise Terminal", use_container_width=True)
            
            if auth_btn:
                if s_user == "admin" and s_pass == "admin786":
                    st.session_state["session_token"] = {"auth": True, "role": "Master_Admin", "user": "Executive Admin", "scope": "Global"}
                    st.rerun()
                else:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (s_user, s_pass))
                    user_row = cursor.fetchone()
                    conn.close()
                    
                    if user_row:
                        st.session_state["session_token"] = {
                            "auth": True, "role": "Field_Operator", "user": user_row["full_name"], "scope": user_row["assigned_sector"]
                        }
                        st.rerun()
                    else:
                        st.error("System Refusal: Cryptographic Verification Failed.")
    st.stop()

# Shared Global Logic
today_iso = datetime.now().strftime("%Y-%m-%d")

# Sidebar Architecture
st.sidebar.markdown(f"<h2 style='color: #00ffd2;'>🎛️ LYNX CORE v3</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f"User: **{st.session_state['session_token']['user']}**")
st.sidebar.markdown(f"Scope Matrix: `{st.session_state['session_token']['scope']}`")
st.sidebar.write("---")
if st.sidebar.button("🔒 Terminate Session Securely", use_container_width=True):
    st.session_state["session_token"] = {"auth": False, "role": None, "user": None, "scope": None}
    st.rerun()

# WhatsApp Global Messaging String Factory
def build_wa_payload(client, alert_style, zone):
    if alert_style == "Invoice Bill Notification":
        text = f"💡 *LYNX FIBER SUBSCRIPTION DUE*\n\nDear Customer *{client['name']}*,\nYour high-speed broadband connection in sector *{zone}* requires renewal.\n\n💵 *Tariff Dues:* {client['tariff']} PKR\n📅 *Expiry Date:* {client['date_expiry']}\n\nPlease pay your bill to enjoy uninterrupted network speeds."
    elif alert_style == "🚨 High Priority Service Disconnect Warning":
        text = f"🚨 *CRITICAL INTERNET SUSPENSION ALERT*\n\nCustomer *{client['name']}* [ID: {client['id']}],\nYour link has *EXPIRED* on `{client['date_expiry']}`.\n\nYour port line is currently queued for system cutoff. Please clear dues of *{client['tariff']} PKR* to bypass automatic suspension."
    elif alert_style == "✅ Formal Payment Invoice Confirmation":
        text = f"✅ *LYNX FIBER PAYMENT RECEIVED*\n\nThank you *{client['name']}*,\nWe have successfully logged your subscription payment of *{client['tariff']} PKR*.\n\n📈 Your network node profile has been extended for 30 Days.\n*Transaction Date:* {datetime.now().strftime('%Y-%m-%d')}"
    return f"https://wa.me/{client['phone']}?text={urllib.parse.quote(text)}"


# ==================== VIEW 1: FIELD OPERATOR DASHBOARD (Strict Scope-Locked UI) ====================
if st.session_state["session_token"]["role"] == "Field_Operator":
    operator_sector = st.session_state["session_token"]["scope"]
    st.markdown(f"## 📱 Field Ledger Node | Zone: <span style='color:#00ffd2;'>{operator_sector}</span>", unsafe_allow_html=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE sector=?", (operator_sector,))
    clients_list = cursor.fetchall()
    
    if not clients_list:
        st.info("No network terminals assigned to your active grid sector.")
    else:
        for cli in clients_list:
            expired = cli["date_expiry"] < today_iso
            status_html = "<span class='badge-expired'>🚨 DISCONNECTED</span>" if expired else "<span class='badge-active'>🟢 INTERNET ACTIVE</span>"
            
            # Glassmorphism Card Rendering
            st.markdown(f"""
                <div class='customer-card'>
                    <table style='width:100%; border:none; border-collapse:collapse;'>
                        <tr>
                            <td style='width:70%; vertical-align:top;'>
                                <h3 style='margin:0; color:#ffffff;'>{cli['name']} <code style='color:#00ffd2; font-size:1rem;'>[{cli['id']}]</code></h3>
                                <p style='margin:5px 0; color:#8b949e;'>Profile Package: <b style='color:#e6edf3;'>{cli['package']}</b> | Monthly Rate: <b style='color:#e6edf3;'>{cli['tariff']} PKR</b></p>
                                <p style='margin:5px 0; font-size:0.9rem; color:#8b949e;'>🧬 Port Mapping: <code>{cli['olt_pon']}</code> | Distribution Splitter: <code>{cli['splitter']}</code></p>
                                <p style='margin:5px 0; color:#8b949e;'>Target Expiry: <code style='color:#ffdd67;'>{cli['date_expiry']}</code> &nbsp;&nbsp;&nbsp;&nbsp; Link Status: {status_html}</p>
                            </td>
                        </tr>
                    </table>
                </div>
            """, unsafe_allow_html=True)
            
            # Form actions nested directly in clean column interfaces below cards
            act_c1, act_c2, act_c3 = st.columns([2, 1, 1])
            with act_c1:
                alert_type = st.selectbox("Action Template Engine", ["Invoice Bill Notification", "🚨 High Priority Service Disconnect Warning", "✅ Formal Payment Invoice Confirmation"], key=f"alert_sel_{cli['id']}")
            with act_c2:
                wa_link = build_wa_payload(cli, alert_type, operator_sector)
                st.markdown(f"<a href='{wa_link}' target='_blank'><button style='width:100%; padding:7px; background-color:#2ea44f; color:white; border:none; border-radius:6px; cursor:pointer; font-weight:bold;'>📲 Execute WhatsApp</button></a>", unsafe_allow_html=True)
            with act_c3:
                if st.button("Collect & Extend 30D", key=f"btn_pay_{cli['id']}", use_container_width=True):
                    extended_date = (datetime.now().date() + timedelta(days=30)).strftime("%Y-%m-%d")
                    cursor.execute("UPDATE clients SET date_expiry=? WHERE id=?", (extended_date, cli["id"]))
                    cursor.execute("INSERT INTO ledger (client_id, timestamp, amount_paid, billing_period, operator) VALUES (?, ?, ?, ?, ?)",
                                   (cli["id"], today_iso, cli["tariff"], datetime.now().strftime("%B %Y"), st.session_state["session_token"]["user"]))
                    conn.commit()
                    st.success(f"Link Refreshed for {cli['name']}!")
                    st.rerun()
            st.markdown("<div style='margin-bottom:25px;'></div>", unsafe_allow_html=True)
    conn.close()

# ==================== VIEW 2: EXECUTIVE MASTER ADMIN ENGINE ====================
else:
    st.markdown("## 🏢 Executive Control System Dashboard", unsafe_allow_html=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Financial Analytics Database Pulls
    cursor.execute("SELECT SUM(amount_paid) FROM ledger")
    gross_val = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM expenses")
    expenses_val = cursor.fetchone()[0] or 0
    clean_profit = gross_val - expenses_val
    
    # Render Financial Glass Cards Block
    m_c1, m_c2, m_c3 = st.columns(3)
    m_c1.metric("Gross Accounts Collection", f"PKR {gross_val:,} /-")
    m_c2.metric("Total Infrastructure Outflows", f"PKR {expenses_val:,} /-")
    m_c3.metric("Net Business Yield (Clean Profit)", f"PKR {clean_profit:,} /-")
    
    st.write("---")
    
    t_monitor, t_expenses, t_staff, t_provision = st.tabs([
        "📡 Universal Core Monitoring Node", 
        "💸 Business Outflow Ledger", 
        "👥 Operator Management Rooms", 
        "🔌 Build New Subscriber Link"
    ])
    
    # ADMIN TAB 1: UNIVERSAL REALTIME EXPIRED & MONITORING ALERTS
    with t_monitor:
        st.markdown("### 🚨 Global Grid Suspension Requests")
        cursor.execute("SELECT id, name, sector, package, date_expiry, olt_pon FROM clients WHERE date_expiry < ?", (today_iso,))
        expired_dataset = cursor.fetchall()
        
        if expired_dataset:
            df_exp = pd.DataFrame(expired_dataset, columns=["Account ID", "Client Name", "Sector", "Package Bandwidth", "Expiry Date", "Core OLT PON Path"])
            st.dataframe(df_exp, use_container_width=True, hide_index=True)
        else:
            st.success("Universal Data Sync Complete: Zero active termination requests flagged on the core.")
            
        st.write("---")
        st.markdown("### 🗺️ Sector Network Segments Directory")
        cursor.execute("SELECT sector_name FROM sectors")
        available_sectors = [r["sector_name"] for r in cursor.fetchall()]
        
        if available_sectors:
            chosen_sector = st.selectbox("Select Target Cluster to Monitor", available_sectors)
            cursor.execute("SELECT * FROM clients WHERE sector=?", (chosen_sector,))
            filtered_clients = cursor.fetchall()
            
            for client_node in filtered_clients:
                is_node_dead = client_node["date_expiry"] < today_iso
                badge_html = "<span class='badge-expired'>🚨 DISCONNECTED</span>" if is_node_dead else "<span class='badge-active'>🟢 LIVE LINK</span>"
                
                st.markdown(f"""
                    <div class='customer-card'>
                        <h4 style='margin:0; color:#00ffd2;'>{client_node['name']} (ID: {client_node['id']})</h4>
                        <p style='margin:5px 0;'>Grid Segment Path: <b>{client_node['olt_pon']}</b> | Box Splitter Ref: <b>{client_node['splitter']}</b></p>
                        <p style='margin:5px 0;'>Active Billing Rate: <b>{client_node['tariff']} PKR</b> | Expiry Target Lock: <code>{client_node['date_expiry']}</code> &nbsp;&nbsp; {badge_html}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"Inspect Financial History Logs for {client_node['name']}"):
                    cursor.execute("SELECT timestamp, billing_period, amount_paid, operator FROM ledger WHERE client_id=?", (client_node["id"],))
                    history_logs = cursor.fetchall()
                    if history_logs:
                        st.dataframe(pd.DataFrame(history_logs, columns=["Date Paid", "For Billing Month", "Amount Settled (PKR)", "Authorized Collector"]), use_container_width=True, hide_index=True)
                    else:
                        st.info("No prior digital ledger vouchers found for this node loop.")

    # ADMIN TAB 2: INFRASTRUCTURE EXPENDITURES
    with t_expenses:
        st.markdown("### 💸 Log New Infrastructure Asset Voucher")
        with st.form("admin_exp_form", clear_on_submit=True):
            in_desc = st.text_input("Voucher Line Item Description (e.g., Core Splicing Wire, Main Office Rent)")
            in_amt = st.number_input("Total Amount Paid Out (PKR)", min_value=0, step=100)
            if st.form_submit_button("Commit Outflow Entry"):
                if in_desc and in_amt > 0:
                    cursor.execute("INSERT INTO expenses (description, amount, date_logged) VALUES (?, ?, ?)", (in_desc, in_amt, today_iso))
                    conn.commit()
                    st.success("Expense Recorded in Core Ledger Table.")
                    st.rerun()
                    
        cursor.execute("SELECT description, amount, date_logged FROM expenses")
        exp_table = cursor.fetchall()
        if exp_table:
            st.dataframe(pd.DataFrame(exp_table, columns=["Line Item Description", "Amount Settled (PKR)", "Log Date"]), use_container_width=True, hide_index=True)

    # ADMIN TAB 3: STAFF & REGIONAL MANAGEMENT SECTORS Factory
    with t_staff:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("### 👥 Deploy New Operator Credentials")
            with st.form("admin_staff_form", clear_on_submit=True):
                u_fullname = st.text_input("Operator Full Legal Name")
                u_username = st.text_input("Create Terminal Login ID").strip()
                u_password = st.text_input("Set Security Password PIN").strip()
                u_sector = st.selectbox("Lock Operator to Grid Segment", available_sectors if available_sectors else ["None"])
                
                if st.form_submit_button("Authorize Profile Setup"):
                    if u_fullname and u_username and u_password and u_sector != "None":
                        try:
                            cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (u_username, u_password, u_fullname, u_sector))
                            conn.commit()
                            st.success(f"Access granted to {u_fullname} for {u_sector} grid matrix.")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("Operation Denied: Username matches existing security record.")
        with col_m2:
            st.markdown("### 🗺️ Initialize New Regional Sector Nodes")
            new_sec_name = st.text_input("Enter New Operational Region Label (e.g. Kala Gujran, Jhelum Cantt)").strip()
            if st.button("Deploy Matrix Segment Node"):
                if new_sec_name:
                    try:
                        cursor.execute("INSERT INTO sectors (sector_name) VALUES (?)", (new_area_input))
                        conn.commit()
                        st.success(f"New Matrix Node '{new_sec_name}' is now fully operational.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Matrix Node configuration already logged.")
                        
        st.write("---")
        st.markdown("### Active Security Registries Verified")
        cursor.execute("SELECT username, full_name, assigned_sector FROM users")
        st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["Login ID", "Full Name", "Assigned Grid Area"]), use_container_width=True, hide_index=True)

    # ADMIN TAB 4: CLIENT LOOP PROVISI