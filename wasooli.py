import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

DB_FILE = "wasoolee_core_pro.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def build_wasoolee_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Enable foreign keys constraint enforcement
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. SAAS LICENSING TABLE (For SaaS Subscriptions management)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saas_companies (
            company_id TEXT PRIMARY KEY,       -- e.g., 'lynx_fiber', 'alpha_net'
            company_name TEXT NOT NULL,
            admin_username TEXT UNIQUE,
            admin_password TEXT NOT NULL,
            status TEXT DEFAULT 'Active',      -- Active, Suspended
            license_expiry DATE
        )
    ''')
    
    # 2. AREAS TABLE (Regional network management - Sanghoi, Saeela etc.)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS network_areas (
            area_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id TEXT,
            area_name TEXT NOT NULL,
            FOREIGN KEY(company_id) REFERENCES saas_companies(company_id) ON DELETE CASCADE
        )
    ''')
    
    # 3. RECOVERY OFFICERS / STAFF TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recovery_staff (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id TEXT,
            staff_name TEXT NOT NULL,
            username TEXT UNIQUE,
            password TEXT NOT NULL,
            allocated_area_id INTEGER,
            status TEXT DEFAULT 'Active',
            FOREIGN KEY(company_id) REFERENCES saas_companies(company_id) ON DELETE CASCADE,
            FOREIGN KEY(allocated_area_id) REFERENCES network_areas(area_id) ON DELETE SET NULL
        )
    ''')
    
    # 4. SUBSCRIBERS MASTER TABLE (Original Wasooli Registrations Schema)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id TEXT,
            custom_cust_id TEXT NOT NULL,      -- User Internet ID
            name TEXT NOT NULL,
            cell_no TEXT,
            cnic TEXT,
            address TEXT,
            connection_type TEXT,              -- Internet, Cable, or Both
            package_internet TEXT,
            internet_amount REAL DEFAULT 0,
            package_cable TEXT,
            cable_amount REAL DEFAULT 0,
            area_id INTEGER,
            status TEXT DEFAULT 'Active',      -- Active, Suspended
            date_created DATE,
            FOREIGN KEY(company_id) REFERENCES saas_companies(company_id) ON DELETE CASCADE,
            FOREIGN KEY(area_id) REFERENCES network_areas(area_id) ON DELETE SET NULL
        )
    ''')
    
    # 5. TRANSACTIONS & INVOICE LEDGER (For generating graphs and records)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices_ledger (
            invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id TEXT,
            custom_cust_id TEXT,
            billing_month TEXT,                -- e.g., 'May 2026'
            previous_dues REAL DEFAULT 0,
            current_bill REAL DEFAULT 0,
            total_payable REAL DEFAULT 0,
            amount_paid REAL DEFAULT 0,
            payment_status TEXT DEFAULT 'Unpaid', -- Paid, Unpaid, Partial
            collected_by INTEGER,              -- staff_id reference
            date_collected DATE,
            FOREIGN KEY(company_id) REFERENCES saas_companies(company_id) ON DELETE CASCADE,
            FOREIGN KEY(collected_by) REFERENCES recovery_staff(staff_id) ON DELETE SET NULL
        )
    ''')
    
    # --- SEED DEFAULT SUPER ADMIN & LYNX DATA ---
    cursor.execute("SELECT COUNT(*) FROM saas_companies WHERE company_id='lynx_fiber'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO saas_companies (company_id, company_name, admin_username, admin_password, status, license_expiry) 
            VALUES ('lynx_fiber', 'Lynx Fiber Pvt Ltd', 'lynxadmin', 'lynx786', 'Active', '2027-12-31')
        """)
        # Seed seed system configurations
        cursor.execute("INSERT INTO network_areas (company_id, area_name) VALUES ('lynx_fiber', 'Sanghoi System')")
        cursor.execute("INSERT INTO network_areas (company_id, area_name) VALUES ('lynx_fiber', 'Saeela System')")
        
    conn.commit()
    conn.close()

# Execute Database initialization on run
build_wasoolee_tables()
st.success("⚡ Step 1 Completed: Multi-Tenant Schema Initialized Successfully!")
# ====================================================================
# STEP 2: SECURE MULTI-TENANT LOGIN ENGINE (SUPER ADMIN / ISP / STAFF)
# ====================================================================

# Session state initialize karein agar pehle se nahi hai
if "auth_session" not in st.session_state:
    st.session_state["auth_session"] = {
        "is_logged_in": False,
        "role": None,          # 'super_admin', 'isp_owner', 'staff'
        "company_id": None,    # e.g., 'lynx_fiber'
        "company_name": None,  # For UI Display
        "staff_id": None,      # Staff identification tracking
        "allocated_area": None # Staff restrictive view mapping
    }

def process_login(username, password):
    # 1. Check for Super Admin (Platform Owner / LogicLabs View)
    if username == "superadmin" and password == "wasooli786":
        st.session_state["auth_session"] = {
            "is_logged_in": True,
            "role": "super_admin",
            "company_id": "saas_master",
            "company_name": "SaaS Global Master Control",
            "staff_id": None,
            "allocated_area": None
        }
        return True, "Welcome Creator! Access Granted to Master System Console."

    conn = get_db_connection()
    cursor = conn.cursor()

    # 2. Check for ISP Tenant Login (e.g., lynxadmin)
    cursor.execute("""
        SELECT * FROM saas_companies 
        WHERE admin_username=? AND admin_password=?
    """, (username, password))
    isp_match = cursor.fetchone()

    if isp_match:
        if isp_match["status"] != "Active":
            conn.close()
            return False, "Access Suspended! Please clear your SaaS license dues."
        
        st.session_state["auth_session"] = {
            "is_logged_in": True,
            "role": "isp_owner",
            "company_id": isp_match["company_id"],
            "company_name": isp_match["company_name"],
            "staff_id": None,
            "allocated_area": None
        }
        conn.close()
        return True, f"Login Successful! Connected to {isp_match['company_name']} Node."

    # 3. Check for Field Recovery Staff Login
    cursor.execute("""
        SELECT s.*, c.company_name, c.status as company_status 
        FROM recovery_staff s
        JOIN saas_companies c ON s.company_id = c.company_id
        WHERE s.username=? AND s.password=? AND s.status='Active'
    """, (username, password))
    staff_match = cursor.fetchone()
    conn.close()

    if staff_match:
        if staff_match["company_status"] != "Active":
            return False, "Parent ISP Company is currently suspended by SaaS Master."
        
        st.session_state["auth_session"] = {
            "is_logged_in": True,
            "role": "staff",
            "company_id": staff_match["company_id"],
            "company_name": staff_match["company_name"],
            "staff_id": staff_match["staff_id"],
            "allocated_area": staff_match["allocated_area_id"]
        }
        return True, f"Staff Access Granted. Welcome back, {staff_match['staff_name']}."

    return False, "Access Refused: Invalid credentials or account blocked by system."


# --- LOGIN USER INTERFACE SCREEN ---
if not st.session_state["auth_session"]["is_logged_in"]:
    st.write("---")
    st.markdown("<h2 style='text-align: center; color: #00f0ff;'>🔒 WASOOLEE ENTERPRISE PORTAL LOG IN</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'>Multi-Tenant Telecom Billing & Field Recovery Node</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("wasoolee_login_form"):
            input_user = st.text_input("Username / Admin ID / Staff ID").strip()
            input_pass = st.text_input("Security Passcode", type="password").strip()
            submit_btn = st.form_submit_button("Authenticate & Connect")
            
            if submit_btn:
                success, msg = process_login(input_user, input_pass)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    st.stop() # Prevents further code execution if user is not logged in

# --- APP NAVIGATION BAR (Showed after login) ---
st.sidebar.markdown(f"<h3 style='color:#00f0ff;'>🌐 {st.session_state['auth_session']['company_name']}</h3>", unsafe_allow_html=True)
st.sidebar.write(f"Authenticated Role: **{st.session_state['auth_session']['role'].upper()}**")
st.sidebar.write("---")

if st.sidebar.button("🔒 Secure Log Out", use_container_width=True):
    st.session_state["auth_session"] = {"is_logged_in": False, "role": None, "company_id": None, "company_name": None, "staff_id": None, "allocated_area": None}
    st.rerun()