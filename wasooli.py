import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

# --- MULTI-TENANT ENTERPRISE CLOUD CONFIGURATION ---
st.set_page_config(page_title="Wasoolee SaaS - Telecom Billing Engine", layout="wide")

# Premium Neon Cyber Dark Theme For Global SaaS Sales
st.markdown("""
    <style>
    .stApp { background-color: #060913; color: #f1f5f9; }
    div[data-testid="stMetricValue"] { color: #00f0ff !important; font-family: monospace; font-size: 2.3rem; }
    .isp-card {
        background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
        border: 1px solid #1f2937; padding: 20px; border-radius: 12px; margin-bottom: 15px;
    }
    .badge-paid { background-color: rgba(16, 185, 129, 0.15); color: #10b981; padding: 4px 12px; border-radius: 20px; font-weight: bold; border: 1px solid #10b981; }
    .badge-unpaid { background-color: rgba(239, 68, 68, 0.15); color: #ef4444; padding: 4px 12px; border-radius: 20px; font-weight: bold; border: 1px solid #ef4444; }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "wasoolee_saas_core.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_saas_database():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Tenants Table (Duniya bhar ke ISPs jo aapko kiraya denge)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isp_name TEXT UNIQUE,
            owner_name TEXT,
            contact_phone TEXT,
            license_expiry TEXT,
            account_status TEXT DEFAULT 'Active'
        )
    ''')
    
    # 2. Multi-Tenant Subscribers Master (Bound by isp_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS global_subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isp_id INTEGER,
            customer_id TEXT,
            name TEXT,
            phone TEXT,
            area TEXT,
            package TEXT,
            tariff INTEGER,
            next_due_date TEXT,
            FOREIGN KEY(isp_id) REFERENCES tenants(id)
        )
    ''')
    
    # 3. Global Financial General Ledger (Double Entry Token)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dynamic_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isp_id INTEGER,
            customer_id TEXT,
            date_posted TEXT,
            amount_processed INTEGER,
            billing_month TEXT,
            status TEXT DEFAULT 'Unpaid'
        )
    ''')
    
    # Seed Initial Platforms for Testing Commercial Model
    cursor.execute("SELECT COUNT(*) FROM tenants")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO tenants (isp_name, owner_name, contact_phone, license_expiry, account_status) VALUES ('Lynx Fiber Pvt Ltd', 'Umer Wazir', '+923315336673', '2027-12-31', 'Active')")
        cursor.execute("INSERT INTO tenants (isp_name, owner_name, contact_phone, license_expiry, account_status) VALUES ('Alpha Net Telecom', 'Raja Khan', '+923215943786', '2026-06-01', 'Active')")
        
        # Seed Lynx Fiber Customers (isp_id = 1)
        cursor.execute("INSERT INTO global_subscribers (isp_id, customer_id, name, phone, area, package, tariff, next_due_date) VALUES (1, 'LX-901', 'Zahid Mehmood', '+923001234567', 'Sanghoi', '10 Mbps', 1500, '2026-06-01')")
        cursor.execute("INSERT INTO dynamic_ledger (isp_id, customer_id, date_posted, amount_processed, billing_month, status) VALUES (1, 'LX-901', '2026-05-01', 1500, 'May 2026', 'Unpaid')")
        
    conn.commit()
    conn.close()

init_saas_database()

# ==================== SAAS MULTI-PORTAL ACCESS SECURITY ====================
if "saas_token" not in st.session_state:
    st.session_state["saas_token"] = {"logged_in": False, "role": None, "tenant_id": None, "tenant_name": None}

if not st.session_state["saas_token"]["logged_in"]:
    st.markdown("<br><br><h1 style='text-align:center; color:#00f0ff; letter-spacing:2px;'>⚡ WASOOLEE CLOUD SOFTWARE ENGINE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8b949e;'>Global Multi-Tenant ISP Provisioning & Subscription Suite</p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.8, 1])
    with c2:
        with st.form("saas_login"):
            login_identity = st.text_input("ISP Tenant Username / Admin ID").strip()
            login_pin = st.text_input("System Security PIN", type="password").strip()
            if st.form_submit_button("Launch Command Core"):
                if login_identity == "superadmin" and login_pin == "wasooli786":
                    st.session_state["saas_token"] = {"logged_in": True, "role": "Super_Admin", "tenant_id": 0, "tenant_name": "SaaS Platform Owner"}
                    st.rerun()
                else:
                    conn = get_db()
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM tenants WHERE isp_name=? AND account_status='Active'", (login_identity,))
                    tenant_match = cursor.fetchone()
                    conn.close()
                    
                    if tenant_match and login_pin == "1234": # Standard trial pin for all ISPs
                        st.session_state["saas_token"] = {
                            "logged_in": True, "role": "ISP_Tenant", "tenant_id": tenant_match["id"], "tenant_name": tenant_match["isp_name"]
                        }
                        st.rerun()
                    else:
                        st.error("Access Refused: Secure Token Verification Failed or Account Blocked by SaaS Owner.")
    st.stop()

# Shared Global State variables
today_iso = datetime.now().strftime("%Y-%m-%d")

# Sidebar SaaS Operations
st.sidebar.markdown("<h2 style='color:#00f0ff;'>🌐 WASOOLEE PANEL</h2>", unsafe_allow_html=True)
st.sidebar.write(f"Session Matrix: **{st.session_state['saas_token']['role']}**")
st.sidebar.write(f"Corporate entity: **{st.session_state['saas_token']['tenant_name']}**")
st.sidebar.write("---")
if st.sidebar.button("🔒 Terminate Cloud Access Link", use_container_width=True):
    st.session_state["saas_token"] = {"logged_in": False, "role": None, "tenant_id": None, "tenant_name": None}
    st.rerun()


# ==================== PORTAL VIEW 1: SUPER ADMIN CONTROL ROOM (Aapka Dashboard) ====================
if st.session_state["saas_token"]["role"] == "Super_Admin":
    st.markdown("## 👑 Super-Admin SaaS Revenue Command Module")
    st.write("Yahan se aap Pakistan bhar ke saare ISPs aur unki subscription fees control karte hain.")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Platform Analytics Metrics
    cursor.execute("SELECT COUNT(*) FROM tenants")
    total_isps = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM global_subscribers")
    total_global_users = cursor.fetchone()[0]
    
    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("Total Client ISPs Registered", f"{total_isps} Companies")
    col_s2.metric("Total End-User Network Nodes", f"{total_global_users} Active Customers")
    col_s3.metric("SaaS Platform Status", "LICENSED & SECURE")
    
    st.write("---")
    
    t_manage_isp, t_add_isp = st.tabs(["🗺️ Active ISP Core Directory", "➕ Provision New Client ISP Company"])
    
    with t_manage_isp:
        cursor.execute("SELECT * FROM tenants")
        all_tenants = cursor.fetchall()
        
        for tenant in all_tenants:
            st.markdown(f"""
                <div class='isp-card'>
                    <h3 style='margin:0; color:#00f0ff;'>🏢 ISP Name: {tenant['isp_name']}</h3>
                    <p style='margin:5px 0;'>System Owner: <b>{tenant['owner_name']}</b> | Helpline: <b>{tenant['contact_phone']}</b></p>
                    <p style='margin:5px 0;'>SaaS Sub-License Expiry Lock: <code style='color:#ffdd67;'>{tenant['license_expiry']}</code> | Status Protocol: <b>{tenant['account_status']}</b></p>
                </div>
            """, unsafe_allow_html=True)
            
            # Action controls to manage separate business platforms
            c_ac1, c_ac2 = st.columns([2, 1])
            with c_ac1:
                status_toggle = st.selectbox(f"Modify Licensing Protocol for {tenant['isp_name']}", ["Active", "Suspended / Blocked"], key=f"t_status_{tenant['id']}")
            with c_ac2:
                st.write("<br>", unsafe_allow_html=True)
                if st.button("Apply Security Rule", key=f"t_btn_{tenant['id']}", use_container_width=True):
                    cursor.execute("UPDATE tenants SET account_status=? WHERE id=?", (status_toggle, tenant["id"]))
                    conn.commit()
                    st.success(f"Security Matrix Modified for {tenant['isp_name']}!")
                    st.rerun()

    with t_add_isp:
        st.markdown("### ➕ Onboard New Broadband Provider Sub-License")
        with st.form("add_isp_form", clear_on_submit=True):
            new_isp_name = st.text_input("Broadband Company Name (e.g., Jhelum Fiber)")
            new_isp_owner = st.text_input("Managing Director Legal Name")
            new_isp_phone = st.text_input("Primary Office WhatsApp Line")
            new_isp_expiry = st.date_input("SaaS License Expiry Term Limit")
            
            if st.form_submit_button("Inject Tenant Partition into Cloud"):
                if new_isp_name and new_isp_owner:
                    try:
                        cursor.execute("INSERT INTO tenants (isp_name, owner_name, contact_phone, license_expiry, account_status) VALUES (?, ?, ?, ?, 'Active')",
                                       (new_isp_name, new_isp_owner, new_isp_phone, new_isp_expiry.strftime("%Y-%m-%d")))
                        conn.commit()
                        st.success(f"Database Partition Built for '{new_isp_name}'. Account Password is set to '1234' by default.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Operation Rejected: Corporate label already allocated in network nodes.")
    conn.close()


# ==================== PORTAL VIEW 2: TENANT ISP WORKSTATION (Aapke Customers Ka Panel) ====================
elif st.session_state["saas_token"]["role"] == "ISP_Tenant":
    current_isp_id = st.session_state["saas_token"]["tenant_id"]
    st.markdown(f"## 🏢 Corporate Workspace Panel: <span style='color:#00f0ff;'>{st.session_state['saas_token']['tenant_name']}</span>", unsafe_allow_html=True)
    st.write("Yeh aapka apna portal hai jahan har ISP sirf aur sirf apna alag data chalayega.")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Isolated Database Extraction for Current Active Tenant Only
    cursor.execute("SELECT COUNT(*) FROM global_subscribers WHERE isp_id=?", (current_isp_id,))
    tenant_users = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(amount_processed) FROM dynamic_ledger WHERE isp_id=? AND status='Paid'", (current_isp_id,))
    tenant_rev = cursor.fetchone()[0] or 0
    
    col_t1, col_t2 = st.columns(2)
    col_t1.metric("Your Active Subscriber Loops", f"{tenant_users} Registered Nodes")
    col_t2.metric("Your Monthly Gross Collections", f"PKR {tenant_rev:,} /-")
    
    st.write("---")
    
    t_client_ledger, t_add_client = st.tabs(["📜 Secure Client Billing Registry", "🔌 Register New Node Subscriber"])
    
    with t_client_ledger:
        cursor.execute("""
            SELECT s.*, l.amount_processed, l.billing_month, l.status as payment_status, l.id as ledger_id
            FROM global_subscribers s
            LEFT JOIN dynamic_ledger l ON s.customer_id = l.customer_id AND s.isp_id = l.isp_id
            WHERE s.isp_id=?
        """, (current_isp_id,))
        my_clients = cursor.fetchall()
        
        for cli in my_clients:
            badge_class = "badge-paid" if cli["payment_status"] == "Paid" else "badge-unpaid"
            with st.markdown(f"""
                <div class='isp-card'>
                    <h4 style='margin:0; color:#ffffff;'>Client: {cli['name']} <code style='color:#00f0ff;'>[{cli['customer_id']}]</code></h4>
                    <p style='margin:5px 0; color:#8b949e;'>Network Sector Area: <b>{cli['area']}</b> | Bandwidth Profile: <b>{cli['package']}</b></p>
                    <p style='margin:5px 0; color:#8b949e;'>Billing Invoice Term: <b>{cli['billing_month']}</b> &nbsp;&nbsp;&nbsp;&nbsp; Current Dues Check: <span class='{badge_class}'>{cli['payment_status']} ({cli['tariff']} PKR)</span></p>
                </div>
            """, unsafe_allow_html=True):
                
                if cli["payment_status"] != "Paid":
                    if st.button(f"Post Collection Receipt for {cli['customer_id']}", key=f"pay_node_{cli['ledger_id']}", use_container_width=True):
                        cursor.execute("UPDATE dynamic_ledger SET status='Paid' WHERE id=?", (cli["ledger_id"],))
                        conn.commit()
                        st.success(f"Payment entry synchronized into system ledger database for account {cli['customer_id']}.")
                        st.rerun()

    with t_add_client:
        st.markdown("### 🔌 Register New Node Under Your Corporate Account")
        with st.form("isp_cust_form", clear_on_submit=True):
            i_cid = st.text_input("Customer ID Account Block (e.g., LX-500)")
            i_name = st.text_input("Subscriber Full Legal Name")
            i_phone = st.text_input("WhatsApp Comms Line")
            i_area = st.text_input("Regional Distribution Grid Sector")
            i_pkg = st.selectbox("Allocated Bandwidth Profile", ["10 Mbps", "20 Mbps", "50 Mbps Dedicated"])
            i_tariff = st.number_input("Monthly Line Access Charge (PKR)", min_value=0, step=100, value=1500)
            
            if st.form_submit_button("Inject Subscriber Profile into Your Matrix"):
                if i_cid and i_name and i_phone:
                    cursor.execute("INSERT INTO global_subscribers (isp_id, customer_id, name, phone, area, package, tariff, next_due_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                   (current_isp_id, i_cid, i_name, i_phone, i_area, i_pkg, i_tariff, (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")))
                    
                    # Generate starting monthly balance ledger invoice voucher statement bound to current isp id
                    cursor.execute("INSERT INTO dynamic_ledger (isp_id, customer_id, date_posted, amount_processed, billing_month, status) VALUES (?, ?, ?, ?, ?, 'Unpaid')",
                                   (current_isp_id, i_cid, today_iso, i_tariff, datetime.now().strftime("%B %Y")))
                    conn.commit()
                    st.success("Subscriber Profile Configured and Deployed in Your Dedicated Secure Cloud Node Ledger.")
                    st.rerun()
    conn.close()