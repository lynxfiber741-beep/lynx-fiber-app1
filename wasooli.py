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
    # ====================================================================
# STEP 3: CORE DASHBOARD & SUBSCRIBER REGISTRATION VIEW
# ====================================================================

# User session state data nikalen
user_data = st.session_state["auth_session"]
current_company = user_data["company_id"]

# --- DYNAMIC DATABASE CONTROLLERS FOR INTERFACE ---
def fetch_company_areas(comp_id):
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM network_areas WHERE company_id=?", conn, params=(comp_id,))
    conn.close()
    return df

def register_new_subscriber(cust_id, name, cell, cnic, address, conn_type, pkg_net, amt_net, pkg_cable, amt_cable, area_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO subscribers (
                company_id, custom_cust_id, name, cell_no, cnic, address, 
                connection_type, package_internet, internet_amount, 
                package_cable, cable_amount, area_id, status, date_created
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', ?)
        """, (current_company, cust_id, name, cell, cnic, address, conn_type, pkg_net, amt_net, pkg_cable, amt_cable, area_id, datetime.now().date()))
        conn.commit()
        success = True
    except Exception as e:
        st.error(f"Database Write Error: {e}")
        success = False
    finally:
        conn.close()
    return success

# --- ROUTING CONTROL BASED ON USER ROLE ---
if user_data["role"] == "isp_owner":
    st.title(f"📊 Centralized Enterprise Operations — {user_data['company_name']}")
    
    # Navigation tabs inside the ISP dashboard
    menu_tabs = st.tabs([
        "👤 Provision New Subscriber", 
        "📍 Manage Network Areas", 
        "📋 Live Subscriber Directory"
    ])
    
    # ----------------------------------------------------------------
    # TAB 1: CUSTOMER PROFILE REGISTRATION VIEW
    # ----------------------------------------------------------------
    with menu_tabs[0]:
        st.markdown("<h3 style='color: #00f0ff;'>📝 Subscriber Entry Protocol</h3>", unsafe_allow_html=True)
        
        # Pull area allocations live from data store
        areas_df = fetch_company_areas(current_company)
        
        if areas_df.empty:
            st.warning("⚠️ Koi Network Area nahi mila! Pehle 'Manage Network Areas' tab mein ja kar Sanghoi ya Saeela System create karein.")
        else:
            # Dropdown dict mapping mapping
            area_mapping = dict(zip(areas_df["area_name"], areas_df["area_id"]))
            
            with st.form("subscriber_registration_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    cust_id = st.text_input("Internet User ID / Custom Account ID (Unique)", placeholder="e.g., LNX-9982").strip()
                    cust_name = st.text_input("Subscriber Full Name").strip()
                    cell_no = st.text_input("Cell Phone Number").strip()
                    cnic_no = st.text_input("CNIC Number (Optional)").strip()
                
                with col2:
                    selected_area_name = st.selectbox("Sublocality / Operational System Network", options=list(area_mapping.keys()))
                    conn_type = st.selectbox("Connection Service Type", options=["Internet", "Cable", "Both"])
                    address = st.text_area("Installation Physical Address").strip()
                
                st.write("---")
                st.markdown("#### 💰 Tariff Rates & Package Architecture Setup")
                
                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    pkg_internet = st.text_input("Internet Package Profile Name", placeholder="e.g., 20 Mbps Premium")
                    internet_amount = st.number_input("Monthly Internet Base Rate (PKR)", min_value=0.0, step=50.0)
                
                with p_col2:
                    pkg_cable = st.text_input("Cable TV Package Profile Name", placeholder="e.g., Digital HD Max")
                    cable_amount = st.number_input("Monthly Cable Base Rate (PKR)", min_value=0.0, step=50.0)
                
                submit_subscriber = st.form_submit_button("⚡ Finalize & Write Subscriber Node")
                
                if submit_subscriber:
                    if not cust_id or not cust_name:
                        st.error("❌ Form Submission Rejected! 'User ID' aur 'Name' fields lazmi hain.")
                    else:
                        chosen_area_id = area_mapping[selected_area_name]
                        if register_new_subscriber(cust_id, cust_name, cell_no, cnic_no, address, conn_type, pkg_internet, internet_amount, pkg_cable, cable_amount, chosen_area_id):
                            st.success(f"🎉 Core Node Registered! Subscriber '{cust_name}' data securely deployed on DB.")
                            st.rerun()

    # ----------------------------------------------------------------
    # TAB 2: REGIONAL NETWORK SYSTEMS MANAGEMENT (Sanghoi, Saeela etc.)
    # ----------------------------------------------------------------
    with menu_tabs[1]:
        st.markdown("<h3 style='color: #00f0ff;'>📍 Regional Network Node Architecture</h3>", unsafe_allow_html=True)
        
        col_input, col_view = st.columns([1, 1.5])
        
        with col_input:
            st.markdown("##### Add New Distribution Sector")
            with st.form("add_area_form", clear_on_submit=True):
                new_area_name = st.text_input("Area / System Name", placeholder="e.g., Sanghoi System").strip()
                add_area_btn = st.form_submit_button("Deploy Sector")
                
                if add_area_btn and new_area_name:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO network_areas (company_id, area_name) VALUES (?, ?)", (current_company, new_area_name))
                    conn.commit()
                    conn.close()
                    st.success(f"Sector '{new_area_name}' deployed successfully!")
                    st.rerun()
        
        with col_view:
            st.markdown("##### Configured Distribution Sectors")
            fresh_areas = fetch_company_areas(current_company)
            if not fresh_areas.empty:
                st.dataframe(fresh_areas[["area_id", "area_name"]], use_container_width=True, hide_index=True)
            else:
                st.info("Filhal koi area register nahi hai.")

    # ----------------------------------------------------------------
    # TAB 3: LIVE SUBSCRIBER DIRECTORY ENGINE
    # ----------------------------------------------------------------
    with menu_tabs[2]:
        st.markdown("<h3 style='color: #00f0ff;'>📋 Live Subscriber Grid Array</h3>", unsafe_allow_html=True)
        conn = get_db_connection()
        subs_df = pd.read_sql_query("""
            SELECT s.custom_cust_id as [User ID], s.name as [Name], s.cell_no as [Phone], 
                   a.area_name as [Network System], s.connection_type as [Type], 
                   (s.internet_amount + s.cable_amount) as [Total Tariff Rate], s.status as [Status]
            FROM subscribers s
            LEFT JOIN network_areas a ON s.area_id = a.area_id
            WHERE s.company_id = ?
        """, conn, params=(current_company,))
        conn.close()
        
        if not subs_df.empty:
            st.dataframe(subs_df, use_container_width=True, hide_index=True)
        else:
            st.info("No active subscribers provisioned in the current node directory.")

elif user_data["role"] == "super_admin":
    st.title("🌐 SaaS Platforms Global Control Tower Console")
    st.write("Welcome, Master Controller. All systems functional.")
    # ====================================================================
# STEP 4: BILLING ENGINE, MONTHLY INVOICE LEDGER & RECOVERY CONTROLLER
# ====================================================================

# Yeh code aapke existing 'if user_data["role"] == "isp_owner":' ke navigation tabs ke andar mazeed tabs barhayega.
# Hum upar wale st.tabs ko update kar rahe hain taaki naye features smoothly link ho sakein.

# Pehle se mojood tabs ke sath in do naye tabs ko bi include karlein jahan tabs declare huay hain:
# menu_tabs = st.tabs(["👤 Provision New Subscriber", "📍 Manage Network Areas", "📋 Live Subscriber Directory", "⚙️ Run Monthly Billing", "💰 Billing & Recovery Ledger"])

# --- DATABASE LOGIC FOR BILLING OPERATIONS ---
def generate_bulk_invoices_for_month(comp_id, target_month):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch all active subscribers for this company
    cursor.execute("SELECT * FROM subscribers WHERE company_id=? AND status='Active'", (comp_id,))
    subscribers = cursor.fetchall()
    
    generated_count = 0
    skipped_count = 0
    
    for sub in subscribers:
        cust_id = sub["custom_cust_id"]
        
        # Check if invoice already exists for this customer and this month to prevent duplicate billing
        cursor.execute("SELECT COUNT(*) FROM invoices_ledger WHERE company_id=? AND custom_cust_id=? AND billing_month=?", (comp_id, cust_id, target_month))
        if cursor.fetchone()[0] > 0:
            skipped_count += 1
            continue
            
        # Calculate Current Month Bill based on Tariff rates
        current_bill = float(sub["internet_amount"] or 0) + float(sub["cable_amount"] or 0)
        
        # Fetch Outstanding Previous Dues from the immediate last invoice (if any)
        cursor.execute("""
            SELECT (total_payable - amount_paid) as outstanding 
            FROM invoices_ledger 
            WHERE company_id=? AND custom_cust_id=? 
            ORDER BY invoice_id DESC LIMIT 1
        """, (comp_id, cust_id))
        last_invoice = cursor.fetchone()
        previous_dues = float(last_invoice["outstanding"]) if last_invoice else 0.0
        
        total_payable = previous_dues + current_bill
        
        # Insert finalized invoice row into the ledger
        cursor.execute("""
            INSERT INTO invoices_ledger (
                company_id, custom_cust_id, billing_month, previous_dues, 
                current_bill, total_payable, amount_paid, payment_status
            ) VALUES (?, ?, ?, ?, ?, ?, 0.0, 'Unpaid')
        """, (comp_id, cust_id, target_month, previous_dues, current_bill, total_payable))
        
        generated_count += 1
        
    conn.commit()
    conn.close()
    return generated_count, skipped_count

def update_invoice_payment(invoice_id, paid_amount, collector_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch original total payable amount
    cursor.execute("SELECT total_payable FROM invoices_ledger WHERE invoice_id=?", (invoice_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
        
    total_payable = float(row["total_payable"])
    
    # Determine absolute status based on verification parameters
    if paid_amount >= total_payable:
        status = "Paid"
    elif paid_amount > 0:
        status = "Partial"
    else:
        status = "Unpaid"
        
    cursor.execute("""
        UPDATE invoices_ledger 
        SET amount_paid=?, payment_status=?, collected_by=?, date_collected=?
        WHERE invoice_id=?
    """, (paid_amount, status, collector_id, datetime.now().date(), invoice_id))
    
    conn.commit()
    conn.close()
    return True


# --- MODIFIED ISP NAVIGATION PANEL WITH INCLUDED BILLING MODULES ---
# Purane menu_tabs line ko is line se replace karlein jo neeche di gayi hai:
if user_data["role"] == "isp_owner":
    # Refreshed tabs array
    menu_tabs = st.tabs([
        "👤 Provision New Subscriber", 
        "📍 Manage Network Areas", 
        "📋 Live Subscriber Directory",
        "⚙️ Run Monthly Billing",
        "💰 Billing & Recovery Ledger"
    ])

    # Note: Tab 0, 1, aur 2 ka code aapka wahi rahega jo Step 3 mein tha. 
    # Hum seedha chalte hain Tab 3 aur Tab 4 ki initialization par:

    # ----------------------------------------------------------------
    # TAB 4: BULK MONTHLY BILL GENERATION ENGINE
    # ----------------------------------------------------------------
    with menu_tabs[3]:
        st.markdown("<h3 style='color: #00f0ff;'>⚙️ Automated Monthly Invoicing System</h3>", unsafe_allow_html=True)
        st.write("Is module se aap poore system ke active users ka bill single-click par generate kar sakte hain.")
        
        # Select target billing month dynamic selection
        current_year = datetime.now().year
        months_list = [f"{m} {current_year}" for m in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]]
        
        # Default select current month index contextually
        current_month_name = datetime.now().strftime("%B %Y")
        default_idx = months_list.index(current_month_name) if current_month_name in months_list else 0
        
        target_month = st.selectbox("Select Target Billing Cycle Month", options=months_list, index=default_idx)
        
        if st.button("🚀 Trigger Bulk Invoicing Run", use_container_width=True):
            with st.spinner("Processing system ledgers and compiling outstanding balances..."):
                gen, skip = generate_bulk_invoices_for_month(current_company, target_month)
                st.success(f"🎉 Processing Complete! Generated: **{gen}** new invoices. Skipped: **{skip}** entries (Already exist).")
                st.rerun()

    # ----------------------------------------------------------------
    # TAB 5: LIVE RECOVERY LEDGER & COLLECTION MANAGER
    # ----------------------------------------------------------------
    with menu_tabs[4]:
        st.markdown("<h3 style='color: #00f0ff;'>💰 Central Accounts Recovery Ledger</h3>", unsafe_allow_html=True)
        
        # Filter ledger view by network system
        f_areas = fetch_company_areas(current_company)
        area_options = ["All Areas"] + list(f_areas["area_name"].values)
        selected_filter_area = st.selectbox("Filter Ledger List by System Node", options=area_options)
        
        conn = get_db_connection()
        
        query = """
            SELECT i.invoice_id, i.custom_cust_id as [User ID], s.name as [Subscriber], 
                   a.area_name as [Area], i.billing_month as [Month], i.previous_dues as [Prev Dues], 
                   i.current_bill as [Current Bill], i.total_payable as [Net Payable], 
                   i.amount_paid as [Amount Paid], i.payment_status as [Status]
            FROM invoices_ledger i
            JOIN subscribers s ON i.custom_cust_id = s.custom_cust_id AND i.company_id = s.company_id
            LEFT JOIN network_areas a ON s.area_id = a.area_id
            WHERE i.company_id = ?
        """
        
        if selected_filter_area != "All Areas":
            query += " AND a.area_name = ?"
            ledger_df = pd.read_sql_query(query, conn, params=(current_company, selected_filter_area))
        else:
            ledger_df = pd.read_sql_query(query, conn, params=(current_company,))
            
        conn.close()
        
        if ledger_df.empty:
            st.info("No invoice records found for the selection. Please run the billing engine first.")
        else:
            # Display interactive dataframe with status highlights
            st.dataframe(ledger_df, use_container_width=True, hide_index=True)
            
            st.write("---")
            st.markdown("#### 💵 Manual Collection Overrides (Receive Payment From Desk)")
            
            # Select specific invoice to pay
            invoice_ids = ledger_df["invoice_id"].tolist()
            selected_inv_id = st.selectbox("Select Invoice ID to Update Payment", options=invoice_ids)
            
            # Show details of selected invoice
            selected_row = ledger_df[ledger_df["invoice_id"] == selected_inv_id].iloc[0]
            st.warning(f"Updating payment for **{selected_row['Subscriber']}** ({selected_row['User ID']}). Total Outstanding: **PKR {selected_row['Net Payable']}**")
            
            with st.form("payment_collection_form"):
                cash_received = st.number_input("Enter Amount Received (PKR)", min_value=0.0, max_value=float(selected_row['Net Payable']), value=float(selected_row['Net Payable']))
                submit_payment = st.form_submit_button("💰 Record Collection Receipt")
                
                if submit_payment:
                    if update_invoice_payment(selected_inv_id, cash_received, collector_id=None):
                        st.success(f"Payment updated successfully for Invoice #{selected_inv_id}!")
                        st.rerun()
                        # ====================================================================
# STEP 5: INTERACTIVE ANALYTICAL DASHBOARD (FINANCIAL GRAPHS & METRICS)
# ====================================================================

# Yeh section aapke 'if user_data["role"] == "isp_owner":' block ke andar sub se top par real-time counters aur visual charts add karega.
# Isko aap tabs se upar lagayenge taaki pure control panel ka overview hamesha screen par dikhta rahe.

st.markdown("---")
st.markdown("<h3 style='color: #00f0ff;'>⚡ Real-Time Network & Financial Analytics</h3>", unsafe_allow_html=True)

conn = get_db_connection()

# 1. COMPUTE CORE METRICS LIVE FROM LEDGERS
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM subscribers WHERE company_id=? AND status='Active'", (current_company,))
total_active_subs = cursor.fetchone()[0]

cursor.execute("SELECT SUM(total_payable), SUM(amount_paid) FROM invoices_ledger WHERE company_id=?", (current_company,))
financial_row = cursor.fetchone()
total_receivable = float(financial_row[0]) if financial_row and financial_row[0] else 0.0
total_recovered = float(financial_row[1]) if financial_row and financial_row[1] else 0.0
total_outstanding = total_receivable - total_recovered

conn.close()

# --- METRIC CARDS ROW DISPLAY ---
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.metric(label="👥 Active Subscribers Node", value=f"{total_active_subs} Users")
with m_col2:
    st.metric(label="📈 Total Cash Recovered", value=f"PKR {total_recovered:,.2f}", delta=f"Active Node")
with m_col3:
    st.metric(label="⚠️ Outstanding Balance Ledger", value=f"PKR {total_outstanding:,.2f}", delta="- Remaining", delta_color="inverse")

st.write("---")

# --- GRAPH LAYOUT MATRIX ---
g_col1, g_col2 = st.columns(2)

with g_col1:
    st.markdown("##### 📊 Monthly Recovery Timeline (Last 6 Months)")
    # Pull monthly transactional trends from system history
    conn = get_db_connection()
    monthly_data_df = pd.read_sql_query("""
        SELECT billing_month as [Month], SUM(amount_paid) as [Recovered Amount]
        FROM invoices_ledger
        WHERE company_id = ?
        GROUP BY billing_month
    """, conn, params=(current_company,))
    conn.close()
    
    if not monthly_data_df.empty:
        # Render a clean, reactive bar chart matching old metrics
        st.bar_chart(data=monthly_data_df.set_index("Month"), y="Recovered Amount", color="#00f0ff", use_container_width=True)
    else:
        st.info("Analytics engine waiting for monthly invoices to structure graph visualizations.")

with g_col2:
    st.markdown("##### 🎯 Service Package Distribution Matrix")
    # Pull active packages categorization profiles
    conn = get_db_connection()
    package_data_df = pd.read_sql_query("""
        SELECT package_internet as [Package Profile], COUNT(*) as [Total Users]
        FROM subscribers
        WHERE company_id = ? AND status='Active' AND package_internet IS NOT NULL AND package_internet != ''
        GROUP BY package_internet
    """, conn, params=(current_company,))
    conn.close()
    
    if not package_data_df.empty:
        # Render a dynamic horizontal or vertical column array
        st.bar_chart(data=package_data_df.set_index("Package Profile"), y="Total Users", color="#22c55e", use_container_width=True)
    else:
        st.info("Add user profiles with explicit package plans to map data matrices.")
        
st.markdown("---")