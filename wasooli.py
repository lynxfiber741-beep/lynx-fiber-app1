import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse

st.set_page_config(page_title="Lynx Fiber Pvt Ltd - Enterprise Master Node", layout="wide")

# ==================== 1. ADVANCED DATABASE ARCHITECTURE ====================
if "areas_list" not in st.session_state:
    st.session_state["areas_list"] = ["Sanghoi", "Saeela", "Jhelum Center"]

# Advanced Device Inventory Stock Database
if "inventory_db" not in st.session_state:
    st.session_state["inventory_db"] = {"XPON_ONUs": 45, "Cat6_Rolls": 12, "Fiber_Splitters": 8, "Mikrotik_Routers": 15}

# System Accounts Registry
if "staff_registry" not in st.session_state:
    st.session_state["staff_registry"] = [
        {"Username": "ali123", "Password": "1122", "Area": "Sanghoi", "Name": "Ali Raza (Field Staff)"},
        {"Username": "usman456", "Password": "4455", "Area": "Saeela", "Name": "Usman Khan (Field Staff)"}
    ]

# Subscriber Master Database with OLT & PON Mapping
if "customers_master" not in st.session_state:
    st.session_state["customers_master"] = [
        {"ID": "LX-101", "Name": "Zahid Mehmood", "Phone": "+923001234567", "Area": "Sanghoi", "Package": "10 Mbps", "Tariff": 1500, "Created_At": "2025-06-10", "Expiry": "2026-05-15", "OLT_PON": "OLT-01_PON-3", "Splitter": "1:8-Spl_02"},
        {"ID": "LX-102", "Name": "Raja Naeem", "Phone": "+923129876543", "Area": "Saeela", "Package": "20 Mbps", "Tariff": 2500, "Created_At": "2025-11-01", "Expiry": "2026-05-28", "OLT_PON": "OLT-02_PON-1", "Splitter": "1:16-Spl_01"},
        {"ID": "LX-103", "Name": "Malik Zain", "Phone": "+923215551234", "Area": "Sanghoi", "Package": "15 Mbps", "Tariff": 2000, "Created_At": "2026-01-15", "Expiry": "2026-05-02", "OLT_PON": "OLT-01_PON-4", "Splitter": "1:8-Spl_05"}
    ]

# Continuous 1-Year Payment History Logs
if "payment_logs" not in st.session_state:
    st.session_state["payment_logs"] = [
        {"ID": "LX-101", "Pay_Date": "2026-04-12", "Amount": 1500, "For_Month": "April 2026", "Collector": "ali123"}
    ]

# Network Operation Expense Logs
if "expense_logs" not in st.session_state:
    st.session_state["expense_logs"] = [
        {"Desc": "Fuel for Generator (Load Shedding)", "Amount": 3500, "Date": "2026-05-10"},
        {"Desc": "Fiber Patching Splicing Wire", "Amount": 1200, "Date": "2026-05-14"}
    ]

# ==================== 2. APPLICATION AUTHENTICATION GATEWAY ====================
if "login_state" not in st.session_state:
    st.session_state["login_state"] = {"logged_in": False, "role": None, "username": None, "assigned_area": None}

if not st.session_state["login_state"]["logged_in"]:
    st.title("📲 Lynx Fiber Pvt Ltd - Core Enterprise Panel")
    st.subheader("Automated Fiber Billing & Infrastructure Management System")
    
    with st.form("login_form"):
        user_input = st.text_input("Access Identity / Username").strip()
        pass_input = st.text_input("Security PIN / Password", type="password").strip()
        submit_login = st.form_submit_button("Authenticate Node")
        
        if submit_login:
            if user_input == "admin" and pass_input == "admin786":
                st.session_state["login_state"] = {"logged_in": True, "role": "Admin", "username": "Admin", "assigned_area": "All"}
                st.success("Master System Cleared. Syncing Dashboard...")
                st.rerun()
            else:
                staff_match = next((s for s in st.session_state["staff_registry"] if s["Username"] == user_input and s["Password"] == pass_input), None)
                if staff_match:
                    st.session_state["login_state"] = {
                        "logged_in": True, "role": "Staff", "username": staff_match["Username"], "assigned_area": staff_match["Area"]
                    }
                    st.success(f"Welcome {staff_match['Name']}. Operational View Synchronized.")
                    st.rerun()
                else:
                    st.error("Access Forbidden: Credentials Not Validated in Registries!")
    st.stop()

# DataFrames Formatting
df_subs = pd.DataFrame(st.session_state["customers_master"])
df_logs = pd.DataFrame(st.session_state["payment_logs"])
df_exp = pd.DataFrame(st.session_state["expense_logs"])
today_str = datetime.now().strftime("%Y-%m-%d")

# Sidebar Configuration Control
st.sidebar.title("🏢 Lynx Fiber Inc.")
st.sidebar.write(f"Identity: **{st.session_state['login_state']['username']}**")
st.sidebar.write(f"Clearance Scope: **{st.session_state['login_state']['assigned_area']}**")
if st.sidebar.button("🔒 Secure Session Logout", use_container_width=True):
    st.session_state["login_state"] = {"logged_in": False, "role": None, "username": None, "assigned_area": None}
    st.rerun()
st.sidebar.write("---")

# WHATSAPP TEMPLATE ENGINE HELPER
def trigger_whatsapp_alert(row, template_type, area):
    if template_type == "Regular Bill Alert":
        msg = f"Dear Customer {row['Name']},\nYour Lynx Fiber internet subscription on {area} is due.\nMonthly Package Charges: {row['Tariff']} PKR.\nExpiry Deadline: {row['Expiry']}.\nKindly settle your bill to avoid speed caps.\nThank you!"
    elif template_type == "🚨 Service Expiry Cutoff":
        msg = f"URGENT NOTICE!\nDear Customer {row['Name']},\nYour broadband connection link has EXPIRED on `{row['Expiry']}`.\nYour network service line is marked for automatic system cutoff. Please pay {row['Tariff']} PKR immediately to restore internet data access.\nLynx Fiber Team."
    elif template_type == "✅ Payment Received Receipt":
        msg = f"Payment Confirmed!\nThank you Customer {row['Name']}.\nWe have successfully received your monthly subscription payment of {row['Tariff']} PKR.\nYour Lynx Fiber node line is extended and running active.\nInvoice Date: {datetime.now().strftime('%Y-%m-%d')}."
    
    return f"https://wa.me/{row['Phone']}?text={urllib.parse.quote(msg)}"


# ==================== VIEW 1: STAFF DASHBOARD (Strict Area Lock + Inventory Consume) ====================
if st.session_state["login_state"]["role"] == "Staff":
    user_area = st.session_state["login_state"]["assigned_area"]
    st.title(f"📱 Field Deployment Terminal | Zone: {user_area}")
    
    # Stock Check for Field Boys
    st.sidebar.subheader("📦 Available Field Materials")
    for item, qty in st.session_state["inventory_db"].items():
        st.sidebar.write(f"{item.replace('_', ' ')}: `{qty}`")
        
    df_staff_view = df_subs[df_subs["Area"] == user_area]
    
    if df_staff_view.empty:
        st.warning("No linked subscriber loops found in this grid.")
    else:
        for idx, row in df_staff_view.iterrows():
            is_dead = row["Expiry"] < today_str
            status_banner = "🚨 SUSPENDED LINK" if is_dead else "🟢 FIBER LINK ACTIVE"
            
            with st.container(border=True):
                col_info, col_actions = st.columns([3, 1])
                with col_info:
                    st.markdown(f"### {row['Name']} `[ID: {row['ID']}]`")
                    st.write(f"Package Profile: **{row['Package']}** | Fees: **{row['Tariff']} PKR** | Target Expiry: `{row['Expiry']}`")
                    st.markdown(f"**Hardware Port Mapping:** Location: `{row['OLT_PON']}` | Block Splitter: `{row['Splitter']}`")
                    st.markdown(f"Link Diagnostics Status: **{status_banner}**")
                    
                    with st.expander("🕒 Historical Payment Sheets (1-Year)"):
                        c_logs = df_logs[df_logs["ID"] == row["ID"]]
                        if not c_logs.empty():
                            st.dataframe(c_logs[["Pay_Date", "For_Month", "Amount"]], use_container_width=True, hide_index=True)
                        else:
                            st.info("No logs on record.")
                            
                with col_actions:
                    # Advanced Multi-Template Selector
                    alert_mode = st.selectbox("Select Alert Type", ["Regular Bill Alert", "🚨 Service Expiry Cutoff", "✅ Payment Received Receipt"], key=f"tpl_{row['ID']}")
                    wa_url = trigger_whatsapp_alert(row, alert_mode, user_area)
                    st.markdown(f'[@📲 Send WhatsApp Message]({wa_url})', unsafe_allow_html=True)
                    st.write("")
                    
                    if st.button("Collect & Renew Cycle", key=f"st_pay_{row['ID']}", use_container_width=True):
                        new_expiry = (datetime.now().date() + timedelta(days=30)).strftime("%Y-%m-%d")
                        for sub in st.session_state["customers_master"]:
                            if sub["ID"] == row["ID"]:
                                sub["Expiry"] = new_expiry
                        st.session_state["payment_logs"].append({
                            "ID": row["ID"], "Pay_Date": today_str, "Amount": row["Tariff"], "For_Month": datetime.now().strftime("%B %Y"), "Collector": st.session_state["login_state"]["username"]
                        })
                        st.success("Database Renewed!")
                        st.rerun()

# ==================== VIEW 2: ADMIN MASTER CORE CONTROL CENTER ====================
else:
    st.title("🏢 Lynx Fiber Pvt Ltd - Centralized Enterprise Operations")
    
    # Financial Analytics Calculation Panel
    total_gross_revenue = df_logs["Amount"].sum()
    total_expenses = df_exp["Amount"].sum() if not df_exp.empty else 0
    net_profit = total_gross_revenue - total_expenses
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Gross Collections (PKR)", f"{total_gross_revenue} /-")
    col_m2.metric("Total Operational Expenses", f"{total_expenses} /-")
    col_m3.metric("Net Clean Profits", f"{net_profit} /-")
    
    st.write("---")
    
    tab_overview, tab_inventory, tab_expenses, tab_staff_mgmt, tab_cust = st.tabs([
        "📢 Central Monitor & Notifications", 
        "📦 Hardware Stock Inventory",
        "💸 Business Expense Tracker",
        "👥 Staff & Grid Assignment", 
        "➕ Provision New Node Connection"
    ])
    
    # ADVANCED TAB 1: CENTRAL NOTIFICATIONS HUB
    with tab_overview:
        st.subheader("🚨 Real-time Global Disconnection Requests")
        expired_master = df_subs[df_subs["Expiry"] < today_str]
        if not expired_master.empty():
            st.error(f"Alert: {len(expired_master)} connections are currently expired across all network segments!")
            st.dataframe(expired_master[["ID", "Name", "Area", "Package", "Expiry", "OLT_PON"]], use_container_width=True, hide_index=True)
        else:
            st.success("All network terminal loops running in healthy green zones.")
            
        st.write("---")
        st.subheader("Segment Cluster View")
        selected_area = st.selectbox("Filter Network Segment Monitoring", st.session_state["areas_list"])
        df_admin_view = df_subs[df_subs["Area"] == selected_area]
        
        for idx, row in df_admin_view.iterrows():
            with st.container(border=True):
                st.markdown(f"#### {row['Name']} (`{row['ID']}`) — Profile: {row['Package']}")
                st.write(f"Grid Node Path: **{row['OLT_PON']}** | Hardware Node Splitter: **{row['Splitter']}** | Expiry: `{row['Expiry']}`")
                with st.expander("View Lifetime Payment Logs"):
                    st.dataframe(df_logs[df_logs["ID"] == row["ID"]][["Pay_Date", "For_Month", "Amount", "Collector"]], use_container_width=True, hide_index=True)

    # ADVANCED TAB 2: INVENTORY STOCK MANAGEMENT
    with tab_inventory:
        st.subheader("📦 Fiber Hardware Inventory Core Ledger")
        c_i1, c_i2 = st.columns(2)
        with c_i1:
            st.write("Current Stock Reserves:")
            st.json(st.session_state["inventory_db"])
        with c_i2:
            st.write("📥 Restock Material Logistics Form")
            item_to_stock = st.selectbox("Select Material Asset", list(st.session_state["inventory_db"].keys()))
            qty_to_add = st.number_input("Log Quantity Pack Received", min_value=1, step=1)
            if st.button("Commit Materials into Stock"):
                st.session_state["inventory_db"][item_to_stock] += qty_to_add
                st.success(f"Material {item_to_stock} stock pools expanded.")
                st.rerun()

    # ADVANCED TAB 3: BUSINESS EXPENSES MANAGEMENT
    with tab_expenses:
        st.subheader("💸 Cash Outflow & Network Operational Expenses")
        with st.form("expense_form", clear_on_submit=True):
            exp_desc = st.text_input("Expense Particular Description (e.g., Office Rent, Splicing Machine Repair)")
            exp_amt = st.number_input("Amount Paid Out (PKR)", min_value=0, step=50)
            if st.form_submit_button("Log Expense Voucher"):
                if exp_desc and exp_amt > 0:
                    st.session_state["expense_logs"].append({"Desc": exp_desc, "Amount": exp_amt, "Date": today_str})
                    st.success("Outflow Voucher Authenticated!")
                    st.rerun()
        if not df_exp.empty:
            st.dataframe(df_exp, use_container_width=True, hide_index=True)

    # ADVANCED TAB 4: STAFF CREATION WITH GRID COUPLING
    with tab_staff_mgmt:
        st.subheader("👥 System User Accounts Deployment")
        with st.form("create_staff_form", clear_on_submit=True):
            st_name = st.text_input("Staff Engineer Full Name")
            st_user = st.text_input("Choose Terminal Username").strip()
            st_pass = st.text_input("Set Security Password Token").strip()
            st_area = st.selectbox("Assign Dedicated Sector Node Block", st.session_state["areas_list"])
            
            if st.form_submit_button("Deploy User Credentials"):
                if st_user and st_pass and st_name:
                    st.session_state["staff_registry"].append({"Username": st_user, "Password": st_pass, "Area": st_area, "Name": st_name})
                    st.success(f"Staff access node initialized for {st_name} on {st_area}.")
                    st.rerun()
                    
        st.write("---")
        st.subheader("Active System Access Registries")
        st.dataframe(pd.DataFrame(st.session_state["staff_registry"]), use_container_width=True, hide_index=True)

    # ADVANCED TAB 5: PROVISION NEW NODE WITH PORT SEGMENTATION
    with tab_cust:
        st.subheader("➕ Provision New Fiber Loop Client Link")
        with st.form("admin_cust_form", clear_on_submit=True):
            c_id = st.text_input("Assign Unique Client Node Account ID")
            c_name = st.text_input("Client Full Name")
            c_phone = st.text_input("WhatsApp Primary Contact (with country code, e.g. +923001234567)")
            c_area = st.selectbox("Select Core Routing Area", st.session_state["areas_list"])
            c_pkg = st.selectbox("Bandwidth Profile", ["10 Mbps", "15 Mbps", "20 Mbps", "30 Mbps"])
            c_tariff = st.number_input("Setup Monthly Base Rent Tariff (PKR)", min_value=0, step=100)
            
            st.markdown("##### 🛠️ Physical Network Port Mapping Configuration")
            c_olt = st.text_input("OLT Box & PON Port Assignment ID (e.g. OLT-02_PON-4)")
            c_splitter = st.text_input("Splitter Box Location Reference (e.g. 1:8-Spl_SectorG)")
            
            # Auto Hardware Consumption Selection
            consume_onu = st.checkbox("Automatically deduct 1 ONU asset unit from Inventory Stock", value=True)
            
            if st.form_submit_button("Provision and Active Broadband Link"):
                if c_id and c_name and c_phone:
                    if consume_onu and st.session_state["inventory_db"]["XPON_ONUs"] > 0:
                        st.session_state["inventory_db"]["XPON_ONUs"] -= 1
                    
                    st.session_state["customers_master"].append({
                        "ID": c_id, "Name": c_name, "Phone": c_phone, "Area": c_area,
                        "Package": c_pkg, "Tariff": c_tariff,
                        "Created_At": today_str,
                        "Expiry": (datetime.now().date() + timedelta(days=30)).strftime("%Y-%m-%d"),
                        "OLT_PON": c_olt if c_olt else "Not_Mapped",
                        "Splitter": c_splitter if c_splitter else "Not_Mapped"
                    })
                    st.success(f"Subscriber node loop built and deployed under {c_area} matrix configuration!")
                    st.rerun()