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