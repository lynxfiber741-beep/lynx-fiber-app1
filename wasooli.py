import streamlit as st
import enum
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, Enum
from sqlalchemy.orm import declarative_base, sessionmaker

# ✅ Wide Screen Layout Settings
st.set_page_config(page_title="Lynx Fiber App Portal", layout="wide")

# LIVE SUPABASE CONNECTION
DATABASE_URL = "postgresql://postgres.snbmurjcggthdvxyxyrd:DlLaglY98SkOzDq2@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

Base = declarative_base()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

# Master Licensing Table
class TenantLicense(Base):
    __tablename__ = 'tenant_licenses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    isp_name = Column(String(100), nullable=False, unique=True)
    license_key = Column(String(100), nullable=False, unique=True)
    expiry_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)

class CustomerStatus(enum.Enum):
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    TERMINATED = "Terminated"

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    status = Column(Enum(CustomerStatus))

Base.metadata.create_all(engine)

# ==============================================================================
# 🔑 LICENSE LOCK SYSTEM
# ==============================================================================
db = SessionLocal()
client_license = db.query(TenantLicense).filter(TenantLicense.license_key == "LNX-PREMIUM-2026").first()

if not client_license:
    client_license = TenantLicense(
        isp_name="Lynx Internet Fiber",
        license_key="LNX-PREMIUM-2026",
        expiry_date=date(2026, 6, 21),  # Next Month Expiry
        is_active=True
    )
    db.add(client_license)
    db.commit()

current_date = datetime.utcnow().date()
is_licensed = client_license.is_active and (client_license.expiry_date >= current_date)

if not is_licensed:
    st.error("❌ APPLICATION LICENSE EXPIRED / SUSPENDED")
    st.markdown(f"""
        <div style="padding:30px; background-color:#FEE2E2; border-radius:10px; border:2px solid #EF4444; text-align:center;">
            <h2 style="color:#991B1B;">App Usage Restrictions Active</h2>
            <p style="color:#7F1D1D; font-size:18px;">Aapka is software ko istemal karne ka monthly period khatam ho chuka hai.</p>
            <p style="font-weight:bold; color:#111827; font-size:20px;">Kindly contact software owner (Umer Wazir) for renewal dues.</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# VISUAL FRONTEND (LYNX DASHBOARD)
# ==============================================================================
st.markdown("""
    <style>
    .main-title { font-size:32px; font-weight:bold; color:#1E3A8A; margin-bottom:5px; }
    .sub-title { font-size:16px; color:#6B7280; margin-bottom:25px; }
    .card-box { padding:20px; border-radius:10px; background-color:#F3F4F6; border-left: 5px solid #2563EB; margin-bottom:15px; }
    .card-title { font-size:14px; color:#4B5563; text-transform:uppercase; font-weight:bold; }
    .card-value { font-size:28px; font-weight:bold; color:#111827; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Lynx Internet Fiber - Dashboard Summary</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">Licensed App Panel for: <b>{client_license.isp_name}</b></div>', unsafe_allow_html=True)

total_cust = db.query(Customer).count()
db.close()

col1, col2 = st.columns(2)
with col1:
    st.markdown(f'<div class="card-box"><div class="card-title">📊 Total Registered Subscriptions</div><div class="card-value">{total_cust}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="card-box" style="border-left-color: #10B981;"><div class="card-title">📅 License Expiry Account Date</div><div class="card-value">{client_license.expiry_date.strftime("%d-%B-%Y")}</div></div>', unsafe_allow_html=True)

st.sidebar.success("License Status: Verified & Paid")
st.sidebar.info(f"Account Access Valid Until: {client_license.expiry_date}")