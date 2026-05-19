import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import urllib.parse
import os

st.set_page_config(page_title="Lynx Fiber Pvt Ltd - BSS Portal", layout="wide")

# ==================== 1. PERMANENT SQLITE DATABASE ENGINE ====================
DB_FILE = "lynx_fiber_master.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Areas Master Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS areas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_name TEXT UNIQUE
        )
    ''')
    
    # 2. Staff Accounts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS staff (
            username TEXT PRIMARY KEY,
            password TEXT,
            name TEXT,
            assigned_area TEXT
        )
    ''')
    
    # 3. Subscribers Master Table (Lifetime Records with Hardware Mapping)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id TEXT PRIMARY KEY,
            name TEXT,
            phone TEXT,
            area TEXT,
            package TEXT,
            tariff INTEGER,
            created_at TEXT,
            expiry TEXT,
            olt_pon TEXT,
            splitter TEXT
        )
    ''')
    
    # 4. Continuous Payment History Table (Never Deleted)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            pay_date TEXT,
            amount INTEGER,
            for_month TEXT,
            collector TEXT
        )
    ''')
    
    # 5. Expenses Vault Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            amount INTEGER,
            date TEXT
        )
    ''')
    
    # Insert Default Admin & Sample Data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM areas")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO areas (area_name) VALUES ('Sanghoi')")
        cursor.execute("INSERT INTO areas (area_name) VALUES ('Saeela')")
        cursor.execute("INSERT INTO areas (area_name) VALUES ('Jhelum Center')")
        
        cursor.execute("INSERT INTO staff VALUES ('ali123', '1122', 'Ali Raza', 'Sanghoi')")
        cursor.execute("INSERT INTO staff VALUES ('usman456', '4455', 'Usman Khan', 'Saeela')")
        
        cursor.execute("INSERT INTO subscribers VALUES ('LX-101', 'Zahid Mehmood', '+923001234567', 'Sanghoi', '10 Mbps', 1500, '2025-06-10', '2026-05-15', 'OLT-01_PON-3', '1:8-Spl_02')")
        cursor.execute("INSERT INTO subscribers VALUES ('LX-102', 'Raja Naeem', '+923129876543', 'Saeela', '20 Mbps', 2500, '2025-11-01', '2026-05-28', 'OLT-02_PON-1', '1:16-Spl_01')")
        
        cursor.execute("INSERT INTO payment_history (customer_id, pay_date, amount, for_month, collector) VALUES ('LX-101', '2026-04-12', 1500, 'April 2026', 'ali123')")
        cursor.execute("INSERT INTO expenses (description, amount, date) VALUES ('Generator Fuel', 3500, '2026-05-10')")
        
    conn.commit()
    conn.close()

# Initialize Database on boot
init_db()

# ==================== 2. SECURITY & SECURE ACCESS GATEWAY ====================
if "login_state" not in st.session_state:
    st.session_state["login_state"] = {"logged_in": False, "role": None, "username": None, "assigned_area": None}

if not st.session_state["login_state"]["logged_in"]:
    st.title("🏢 Lynx Fiber Pvt Ltd - Telecom BSS Portal")
    st.subheader("Manual Staff-Lock Billing & Network Provisioning Engine")
    
    with st.form("login_form"):
        user_input = st.text_input("Access Identity / Username").strip()
        pass_input = st.text_input("Security PIN / Password", type="password").strip()
        submit_login = st.form_submit_button("Authenticate Node")
        
        if submit_login:
            if user_input == "admin" and pass_input == "admin786":
                st.session_state["login_state"] = {"logged_in": True, "role": "Admin", "username": "Admin", "assigned_area": "All"}
                st.success("Master System Cleared. Syncing Core Dashboard...")
                st.rerun()
            else:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM staff WHERE username=? AND password=?", (user_input, pass_input))
                staff_match = cursor.fetchone()
                conn.close()
                
                if staff_match:
                    st.session_state["login_state"] = {
                        "logged_in": True, "role": "Staff", "username": staff_match["username"], "assigned_area": staff_match["assigned_area"]
                    }
                    st.success(f"Welcome {staff_match['name']}. Sector View Synchronized.")
                    st.rerun()
                else:
                    st.error("Access Forbidden: Invalid Identity or PIN Security Tokens.")
    st.stop()

# --- Shared Variables ---
today_str = datetime.now().strftime("%Y-%m-%d")

# Sidebar Session Management
st.sidebar.title(" Lynx Fiber Inc.")
st.sidebar.write(f"Active Identity: **{st.session_state['login_state']['username']}**")
st.sidebar.write(f"Grid Lock Scope: **{st.session_state['login_state']['assigned_area']}**")
if st.sidebar.button("🔒 Secure Session Logout", use_container_width=True):
    st.session_state["login_state"] = {"logged_in": False, "role": None, "username": None, "assigned_area": None}
    st.rerun()
st.sidebar.write("---")

# WHATSAPP TEMPLATE ENGINE HELPER
def trigger_whatsapp_alert(row, template_type, area):
    if template_type == "Regular Bill Alert":
        msg = f"Dear Customer {row['name']},\nYour Lynx Fiber internet subscription on {area} is due.\nMonthly Package Charges: {row['tariff']} PKR.\nExpiry Deadline: {row['expiry']}.\nKindly settle your bill to avoid speed caps.\nThank you!"
    elif template_type == "🚨 Service Expiry Cutoff":
        msg = f"URGENT NOTICE!\nDear Customer {row['name']},\nYour broadband connection link has EXPIRED on `{row['expiry']}`.\nYour network service line is marked for manual system cutoff. Please pay {row['tariff']} PKR immediately to restore internet data access.\nLynx Fiber Team."
    elif template_type == "✅ Payment Received Receipt":
        msg = f"Payment Confirmed!\nThank you Customer {row['name']}.\nWe have successfully received your monthly subscription payment of {row['tariff']} PKR.\nYour Lynx Fiber node line is extended and running active.\nInvoice Date: {datetime.now().strftime('%Y-%m-%d')}."
    
    return f"https://wa.me/{row['phone']}?text={urllib.parse.quote(msg)}"


# ==================== VIEW 1: STAFF DASHBOARD (Strict Area Lock View) ====================
if st.session_state["login_state"]["role"] == "Staff":
    user_area = st.session_state["login_state"]["assigned_area"]
    st.title(f"📱 Field Deployment Terminal | Zone: {user_area}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subscribers WHERE area=?", (user_area,))
    rows = cursor.fetchall()
    
    if not rows:
        st.warning(f"No active client terminal loops registered under {user_area} matrix.")
    else:
        for row in rows:
            is_dead = row["expiry"] < today_str
            status_banner = "🚨 SUSPENDED LINK" if is_dead else "🟢 FIBER LINK ACTIVE"
            
            with st.container(border=True):
                col_info, col_actions = st.columns([3, 1])
                with col_info:
                    st.markdown(f"### {row['name']} `[ID: {row['id']}]`")
                    st.write(f"Package: **{row['package']}** | Fees: **{row['tariff']} PKR** | Target Expiry: `{row['expiry']}`")
                    st.markdown(f"**Hardware Port Mapping:** Location: `{row['olt_pon']}` | Block Splitter: `{row['splitter']}`")
                    st.markdown(f"Link Diagnostics Status: **{status_banner}**")
                    
                    with st.expander("🕒 Historical Payment Sheets (1-Year Logging)"):
                        cursor.execute("SELECT pay_date, for_month, amount, collector FROM payment_history WHERE customer_id=?", (row["id"],))
                        logs = cursor.fetchall()
                        if logs:
                            st.dataframe(pd.DataFrame(logs, columns=["Pay_Date", "For_Month", "Amount", "Collector"]), use_container_width=True, hide_index=True)
                        else:
                            st.info("No past payments registered.")
                            
                with col_actions:
                    alert_mode = st.selectbox("Select Alert Type", ["Regular Bill Alert", "🚨 Service Expiry Cutoff", "✅ Payment Received Receipt"], key=f"tpl_{row['id']}")
                    wa_url = trigger_whatsapp_alert(row, alert_mode, user_area)
                    st.markdown(f'[@📲 Send WhatsApp Alert]({wa_url})', unsafe_allow_html=True)
                    st.write("")
                    
                    if st.button("Collect & Renew Cycle", key=f"pay_{row['id']}", use_container_width=True):
                        new_expiry = (datetime.now().date() + timedelta(days=30)).strftime("%Y-%m-%d")
                        cursor.execute("UPDATE subscribers SET expiry=? WHERE id=?", (new_expiry, row["id"]))
                        cursor.execute("INSERT INTO payment_history (customer_id, pay_date, amount, for_month, collector) VALUES (?, ?, ?, ?, ?)",
                                       (row["id"], today_str, row["tariff"], datetime.now().strftime("%B %Y"), st.session_state["login_state"]["username"]))
                        conn.commit()
                        st.success("Database Renewed!")
                        st.rerun()
    conn.close()

# ==================== VIEW 2: ADMIN MASTER CORE CONTROL CENTER ====================
else:
    st.title("🏢 Lynx Fiber Pvt Ltd - Centralized Enterprise Operations")
    
    # Live Financial Database Calculations
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(amount) FROM payment_history")
    total_gross = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_exp = cursor.fetchone()[0] or 0
    net_profit = total_gross - total_exp
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Gross Collections (PKR)", f"{total_gross} /-")
    col_m2.metric("Total Operational Expenses", f"{total_exp} /-")
    col_m3.metric("Net Clean Profits", f"{net_profit} /-")
    
    st.write("---")
    
    tab_overview, tab_expenses, tab_staff_mgmt, tab_cust = st.tabs([
        "📢 Central Monitor & Notifications", 
        "💸 Business Expense Tracker",
        "👥 Staff & Grid Assignment", 
        "➕ Provision New Node Connection"
    ])
    
    # TAB 1: CENTRAL MONITOR & ALL NOTIFICATIONS
    with tab_overview:
        st.subheader("🚨 Real-time Global Disconnection Requests")
        cursor.execute("SELECT * FROM subscribers WHERE expiry < ?", (today_str,))
        expired_rows = cursor.fetchall()
        
        if expired_rows:
            st.error(f"Alert: {len(expired_rows)} connections are currently expired across all network segments!")
            st.dataframe(pd.DataFrame(expired_rows, columns=["id", "name", "phone", "area", "package", "tariff", "created_at", "expiry", "olt_pon", "splitter"])[["id", "name", "area", "package", "expiry", "olt_pon"]], use_container_width=True, hide_index=True)
        else:
            st.success("All network terminal loops running in healthy green zones.")
            
        st.write("---")
        st.subheader("Segment Cluster View")
        
        cursor.execute("SELECT area_name FROM areas")
        all_areas = [r["area_name"] for r in cursor.fetchall()]
        
        if all_areas:
            selected_area = st.selectbox("Filter Network Segment Monitoring", all_areas)
            cursor.execute("SELECT * FROM subscribers WHERE area=?", (selected_area,))
            df_view = cursor.fetchall()
            
            for row in df_view:
                with st.container(border=True):
                    st.markdown(f"#### {row['name']} (`{row['id']}`) — Profile: {row['package']}")
                    st.write(f"Grid Node Path: **{row['olt_pon']}** | Splitter Reference: **{row['splitter']}** | Expiry: `{row['expiry']}`")
                    with st.expander("View Lifetime Payment Logs"):
                        cursor.execute("SELECT pay_date, for_month, amount, collector FROM payment_history WHERE customer_id=?", (row["id"],))
                        c_logs = cursor.fetchall()
                        if c_logs:
                            st.dataframe(pd.DataFrame(c_logs, columns=["Pay_Date", "For_Month", "Amount", "Collector"]), use_container_width=True, hide_index=True)
                        else:
                            st.info("No records found.")

    # TAB 2: BUSINESS EXPENSES MANAGEMENT
    with tab_expenses:
        st.subheader("💸 Cash Outflow & Network Operational Expenses")
        with st.form("expense_form", clear_on_submit=True):
            exp_desc = st.text_input("Expense Particular Description")
            exp_amt = st.number_input("Amount Paid Out (PKR)", min_value=0, step=50)
            if st.form_submit_button("Log Expense Voucher"):
                if exp_desc and exp_amt > 0:
                    cursor.execute("INSERT INTO expenses (description, amount, date) VALUES (?, ?, ?)", (exp_desc, exp_amt, today_str))
                    conn.commit()
                    st.success("Outflow Voucher Authenticated!")
                    st.rerun()
                    
        cursor.execute("SELECT description, amount, date FROM expenses")
        all_exp = cursor.fetchall()
        if all_exp:
            st.dataframe(pd.DataFrame(all_exp, columns=["Description", "Amount", "Date"]), use_container_width=True, hide_index=True)

    # TAB 3: STAFF MANAGEMENT & NEW AREA FACTORY
    with tab_staff_mgmt:
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.subheader("👥 System User Accounts Deployment")
            with st.form("create_staff_form", clear_on_submit=True):
                st_name = st.text_input("Staff Engineer Full Name")
                st_user = st.text_input("Choose Terminal Username").strip()
                st_pass = st.text_input("Set Security Password Token").strip()
                st_area = st.selectbox("Assign Dedicated Sector Node Block", all_areas if all_areas else ["None"])
                
                if st.form_submit_button("Deploy User Credentials"):
                    if st_user and st_pass and st_name and st_area != "None":
                        try:
                            cursor.execute("INSERT INTO staff VALUES (?, ?, ?, ?)", (st_user, st_pass, st_name, st_area))
                            conn.commit()
                            st.success(f"Staff access node initialized for {st_name} on {st_area}.")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("Username already exists!")
        with col_s2:
            st.subheader("🗺️ Add New Operational Network Areas")
            new_area_input = st.text_input("Enter New Area Title (e.g. Kala Gujran)").strip()
            if st.button("Deploy Area Node"):
                if new_area_input:
                    try:
                        cursor.execute("INSERT INTO areas (area_name) VALUES (?)", (new_area_input,))
                        conn.commit()
                        st.success(f"Area '{new_area_input}' successfully created.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Area already exists!")
                        
        st.write("---")
        st.subheader("Active System Access Registries")
        cursor.execute("SELECT username, name, assigned_area FROM staff")
        st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["Username", "Full Name", "Assigned Area"]), use_container_width=True, hide_index=True)

    # TAB 4: PROVISION NEW CONNECTION WITH PHYSICAL HARDWARE PORT MAPPING
    with tab_cust:
        st.subheader("➕ Provision New Fiber Loop Client Link")
        with st.form("admin_cust_form", clear_on_submit=True):
            c_id = st.text_input("Assign Unique Client Node Account ID")
            c_name = st.text_input("Client Full Name")
            c_phone = st.text_input("WhatsApp Primary Contact (e.g. +923001234567)")
            c_area = st.selectbox("Select Core Routing Area", all_areas if all_areas else ["None"])
            c_pkg = st.selectbox("Bandwidth Profile", ["10 Mbps", "15 Mbps", "20 Mbps", "30 Mbps"])
            c_tariff = st.number_input("Setup Monthly Base Rent Tariff (PKR)", min_value=0, step=100)
            
            st.markdown("##### 🛠️ Physical Network Port Mapping Configuration")
            c_olt = st.text_input("OLT Box & PON Port Assignment ID (e.g. OLT-02_PON-4)")
            c_splitter = st.text_input("Splitter Box Location Reference")
            
            if st.form_submit_button("Provision and Activate Broadband Link"):
                if c_id and c_name and c_phone and c_area != "None":
                    try:
                        init_expiry = (datetime.now().date() + timedelta(days=30)).strftime("%Y-%m-%d")
                        cursor.execute("INSERT INTO subscribers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                       (c_id, c_name, c_phone, c_area, c_pkg, c_tariff, today_str, init_expiry, c_olt, c_splitter))
                        conn.commit()
                        st.success(f"Subscriber {c_name} built and deployed under {c_area} database matrix configuration!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Client ID already exists!")
                        
    conn.close()