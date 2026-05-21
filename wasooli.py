import streamlit as st
import enum
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, Date, ForeignKey, Enum, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# ✅ Sabse upar wide layout set kiya taake koi error na aaye
st.set_page_config(page_title="Lynx Fiber ISP Billing System", layout="wide")

# 1. LIVE SUPABASE CONNECTION
DATABASE_URL = "postgresql://postgres.snbmurjcggthdvxyxyrd:DlLaglY98SkOzDq2@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

Base = declarative_base()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

class CustomerStatus(enum.Enum):
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    TERMINATED = "Terminated"

class ComplaintStatus(enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    status = Column(Enum(CustomerStatus), default=CustomerStatus.ACTIVE)

class Complaint(Base):
    __tablename__ = 'complaints'
    id = Column(Integer, primary_key=True)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.OPEN)

Base.metadata.create_all(engine)

# Custom Styling
st.markdown("""
    <style>
    .main-title { font-size:32px; font-weight:bold; color:#1E3A8A; margin-bottom:5px; }
    .sub-title { font-size:16px; color:#6B7280; margin-bottom:25px; }
    .card-box { padding:20px; border-radius:10px; background-color:#F3F4F6; border-left: 5px solid #2563EB; margin-bottom:15px; }
    .card-title { font-size:14px; color:#4B5563; text-transform:uppercase; font-weight:bold; }
    .card-value { font-size:28px; font-weight:bold; color:#111827; }
    </style>
""", unsafe_allow_html=True)

# ✅ Badla hua Text (Lynx Dashboard)
st.markdown('<div class="main-title">Lynx Internet Fiber - Dashboard Summary</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Core Administration Control Panel</div>', unsafe_allow_html=True)

db = SessionLocal()
try:
    total_cust = db.query(Customer).count()
    active_cust = db.query(Customer).filter(Customer.status == CustomerStatus.ACTIVE).count()
    inactive_cust = db.query(Customer).filter(Customer.status != CustomerStatus.ACTIVE).count()
    open_complaints = db.query(Complaint).filter(Complaint.status == ComplaintStatus.OPEN).count()
    resolved_complaints = db.query(Complaint).filter(Complaint.status == ComplaintStatus.RESOLVED).count()
finally:
    db.close()

st.subheader("🛠️ Complaints & Support Module")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="card-box" style="border-left-color: #EF4444;"><div class="card-title">🚨 Total Complaints Recieved</div><div class="card-value">{open_complaints + resolved_complaints}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="card-box" style="border-left-color: #F59E0B;"><div class="card-title">⚠️ Open / Pending Issues</div><div class="card-value">{open_complaints}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="card-box" style="border-left-color: #10B981;"><div class="card-title">✅ Resolved Tickets</div><div class="card-value">{resolved_complaints}</div></div>', unsafe_allow_html=True)

st.markdown("---")
st.subheader("👥 User Status & Receivables Summary")
col4, col5, col6 = st.columns(3)
with col4:
    st.markdown(f'<div class="card-box" style="border-left-color: #3B82F6;"><div class="card-title">📊 Total Registered Subscriptions</div><div class="card-value">{total_cust}</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="card-box" style="border-left-color: #10B981;"><div class="card-title">🟢 Active Users (Online)</div><div class="card-value">{active_cust}</div></div>', unsafe_allow_html=True)
with col6:
    st.markdown(f'<div class="card-box" style="border-left-color: #DC2626;"><div class="card-title">🔴 Not Active Users</div><div class="card-value">{inactive_cust}</div></div>', unsafe_allow_html=True)

st.sidebar.success("Supabase Engine: Connected")
st.sidebar.info("Use the multi-page menu system to manage your Lynx Internet Fiber network.")