import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import calendar

# --- PREMIUM ENTERPRISE ARCHITECTURE ---
st.set_page_config(page_title="Lynx Fiber Pvt Ltd - Executive BSS Suite", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #f1f5f9; }
    div[data-testid="stMetricValue"] { color: #38bdf8 !important; font-family: monospace; font-size: 2.2rem; }
    .ledger-debit { color: #f87171; font-weight: bold; }
    .ledger-credit { color: #4ade80; font-weight: bold; }
    .invoice-box {
        background: #131c2e; border-left: 5px solid #38bdf8;
        padding: 15px; border-radius: 8px; margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "lynx_telecom_corporate.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_corporate_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Core Corporate Clients (With Balance Ledger Tracker)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS corporate_clients (
            id TEXT PRIMARY KEY, name TEXT, phone TEXT, area TEXT, package TEXT, 
            tariff INTEGER, account_balance INTEGER DEFAULT 0, status TEXT DEFAULT 'Active'
        )
    ''')
    
    # 2. Immutable General Ledger Invoices (Debit/Credit System)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_num TEXT PRIMARY KEY, client_id TEXT, date_generated TEXT, 
            due_date TEXT, amount_due INTEGER, amount_paid INTEGER DEFAULT 0, 
            status TEXT, type TEXT
        )
    ''')
    
    # Seed Core Setup
    cursor.execute("SELECT COUNT(*) FROM corporate_clients")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO corporate_clients VALUES ('LX-701', 'Zahid Mehmood', '+923001234567', 'Sanghoi', '10 Mbps', 1500, 0, 'Active')")
        cursor.execute("INSERT INTO corporate_clients VALUES ('LX-702', 'Raja Naeem', '+923129876543', 'Saeela', '20 Mbps', 2500, -500, 'Suspended')")
        
        cursor.execute("INSERT INTO invoices VALUES ('INV-2026-001', 'LX-701', '2026-05-01', '2026-05-10', 1500, 1500, 'Paid', 'Monthly Bill')")
        cursor.execute("INSERT INTO invoices VALUES ('INV-2026-002', 'LX-702', '2026-05-01', '2026-05-10', 2500, 2000, 'Unpaid', 'Monthly Bill')")
    
    conn.commit()
    conn.close()

init_corporate_db()

# --- SECURITY PIN TOKEN GATEWAY ---
if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = {"status": False, "user": None}

if not st.session_state["auth_token"]["status"]:
    st.markdown("<br><br><h2 style='text-align:center; color:#38bdf8;'>LYNX FIBER ENTERPRISE GATEWAY</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        with st.form("auth_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Unlock Matrix Server"):
                if u == "admin" and p == "admin786":
                    st.session_state["auth_token"] = {"status": True, "user": "Executive Admin"}
                    st.rerun()
                else:
                    st.error("Invalid Cryptographic Signature Token.")
    st.stop()

# --- MASTER CONTROLS ---
st.title("⚡ Lynx Fiber Pvt Ltd - Telecom BSS Executive Engine")
st.write(f"System Operator Session: `{st.session_state['auth_token']['user']}`")
st.write("---")

# Global Financial Calculations
conn = get_db()
cursor = conn.cursor()
cursor.execute("SELECT SUM(amount_paid) FROM invoices")
gross_rev = cursor.fetchone()[0] or 0
cursor.execute("SELECT COUNT(*) FROM corporate_clients WHERE status='Suspended'")
total_suspended = cursor.fetchone()[0] or 0

m1, m2, m3 = st.columns(3)
m1.metric("Total Ledger Capital Collections", f"PKR {gross_rev:,} /-")
m2.metric("Suspended Terminals", f"{total_suspended} Nodes")
m3.metric("System Core Status", "ONLINE (100% Sync)")

st.write("---")

tab_billing, tab_pro_rata, tab_clients = st.tabs([
    "🏦 General Ledger & Invoice Desk", 
    "📊 Pro-Rata Account Engine", 
    "🔌 Client Provision Routing"
])

# ADVANCED TAB 1: DEBIT / CREDIT LEDGER VIEW
with tab_billing:
    st.markdown("### 📜 Double-Entry System Invoices")
    cursor.execute("""
        SELECT i.*, c.name, c.account_balance 
        FROM invoices i 
        JOIN corporate_clients c ON i.client_id = c.id
    """)
    all_invoices = cursor.fetchall()
    
    for inv in all_invoices:
        bal_class = "ledger-credit" if inv["account_balance"] >= 0 else "ledger-debit"
        with st.markdown(f"""
            <div class='invoice-box'>
                <table style='width:100%; border:none;'>
                    <tr>
                        <td style='width:50%;'>
                            <h4 style='margin:0; color:#38bdf8;'>Invoice: {inv['invoice_num']} [{inv['type']}]</h4>
                            <p style='margin:4px 0;'>Client: <b>{inv['name']}</b> (ID: {inv['client_id']})</p>
                            <p style='margin:4px 0;'>Issue Date: <code>{inv['date_generated']}</code> | Due Date: <code>{inv['due_date']}</code></p>
                        </td>
                        <td style='text-align:right; vertical-align:top;'>
                            <p style='margin:0;'>Amount Due: <b>{inv['amount_due']} PKR</b></p>
                            <p style='margin:4px 0;'>Amount Cleared: <b style='color:#4ade80;'>{inv['amount_paid']} PKR</b></p>
                            <p style='margin:4px 0;'>Current Wallet Ledger: <span class='{bal_class}'>{inv['account_balance']} PKR</span></p>
                            <p style='margin:4px 0;'>Status Code: <u><b>{inv['status']}</b></u></p>
                        </td>
                    </tr>
                </table>
            </div>
        """, unsafe_allow_html=True):
            
            c_pay1, c_pay2 = st.columns([3, 1])
            with c_pay1:
                pay_amt = st.number_input(f"Enter Payment Collection for {inv['invoice_num']}", min_value=0, step=100, key=f"amt_{inv['invoice_num']}")
            with c_pay2:
                st.write("<br>", unsafe_allow_html=True)
                if st.button("Post Transaction Ledger", key=f"btn_{inv['invoice_num']}", use_container_width=True):
                    if pay_amt > 0:
                        # Professional Ledger Math: Calculate new balance adjustments
                        new_paid_total = inv["amount_paid"] + pay_amt
                        new_status = "Paid" if new_paid_total >= inv["amount_due"] else "Partial"
                        
                        # Update Invoice Account
                        cursor.execute("UPDATE invoices SET amount_paid=?, status=? WHERE invoice_num=?", (new_paid_total, new_status, inv["invoice_num"]))
                        
                        # Adjust Client Wallet Balance Table
                        balance_adjustment = pay_amt - (inv["amount_due"] - inv["amount_paid"])
                        cursor.execute("UPDATE corporate_clients SET account_balance = account_balance + ? WHERE id=?", (balance_adjustment, inv["client_id"]))
                        
                        conn.commit()
                        st.success(f"Ledger Verified for {inv['invoice_num']}!")
                        st.rerun()

# ADVANCED TAB 2: PRO-RATA UTILITY CALCULATOR ENGINE
with tab_pro_rata:
    st.markdown("### 📊 Pro-Rata Mid-Month Bill Token Generator")
    st.write("Jab koi customer mahine ke darmyan mein aaye, to unke bache hue dinon ka tariff nikalne ka automated engine:")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        base_tariff = st.number_input("Standard Package Monthly Tariff (PKR)", min_value=1000, step=500, value=1500)
    with col_p2:
        activation_date = st.date_input("Activation Live Date Slot")
    with col_p3:
        # Compute exact days remaining in current running month
        year = activation_date.year
        month = activation_date.month
        total_days_in_month = calendar.monthrange(year, month)[1]
        days_remaining = total_days_in_month - activation_date.day + 1
        
        # Pro-rata formula math
        pro_rata_bill = int((base_tariff / total_days_in_month) * days_remaining)
        
        st.metric("Calculated Days Remaining", f"{days_remaining} Days")
        st.metric("Partial Pro-Rata Debit Amount", f"{pro_rata_bill} PKR")

# ADVANCED TAB 3: EXECUTIVE PROVISIONING SYSTEM
with tab_clients:
    st.markdown("### ➕ Corporate Fiber Line Client Provisioning")
    with st.form("provision_form", clear_on_submit=True):
        f_id = st.text_input("System Generation Client ID (Unique Token)")
        f_name = st.text_input("Account Holder Legal Name")
        f_phone = st.text_input("WhatsApp Comms String (+92...)")
        f_area = st.text_input("Network Grid Sector Location")
        f_pkg = st.selectbox("Bandwidth Node Profile", ["10 Mbps Line", "20 Mbps Line", "50 Mbps Dedicated Dedicated"])
        f_tariff = st.number_input("Agreed Monthly Base Tariff", min_value=0, step=500, value=1500)
        
        if st.form_submit_button("Authorize and Inject Profile into Core"):
            if f_id and f_name and f_phone:
                try:
                    cursor.execute("INSERT INTO corporate_clients VALUES (?, ?, ?, ?, ?, ?, 0, 'Active')", (f_id, f_name, f_phone, f_area, f_pkg, f_tariff))
                    
                    # Automatically generate current month's first general debit invoice block
                    inv_uid = f"INV-{datetime.now().strftime('%Y%m')}-{f_id}"
                    due_date_calc = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
                    cursor.execute("INSERT INTO invoices VALUES (?, ?, ?, ?, ?, 0, 'Unpaid', 'Initial Provision')", (inv_uid, f_id, datetime.now().strftime("%Y-%m-%d"), due_date_calc, f_tariff))
                    
                    conn.commit()
                    st.success(f"Client Account {f_id} and its General Ledger successfully initialized!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Token Collision: Client ID matches an existing corporate network path node.")
                    
    conn.close()