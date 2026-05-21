import streamlit as st
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, ForeignKey, Enum, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import enum

# ✅ Is file mein bhi full-screen setup sabse upar kar diya bina error ke
st.set_page_config(page_title="Lynx Customers Setup", layout="wide")

DATABASE_URL = "postgresql://postgres.snbmurjcggthdvxyxyrd:DlLaglY98SkOzDq2@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class BillingType(enum.Enum):
    MONTHLY_FIXED = "Monthly-Fixed"
    CARD_SYSTEM = "Card-System"

class CustomerStatus(enum.Enum):
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    TERMINATED = "Terminated"

class Package(Base):
    __tablename__ = 'packages'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class SubArea(Base):
    __tablename__ = 'sub_areas'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_code = Column(String, unique=True)
    name = Column(String)
    father_name = Column(String)
    phone = Column(String)
    package_id = Column(Integer, ForeignKey('packages.id'))
    sub_area_id = Column(Integer, ForeignKey('sub_areas.id'))
    monthly_discount = Column(Numeric)
    billing_type = Column(Enum(BillingType))
    status = Column(Enum(CustomerStatus))
    registration_date = Column(Date)

st.title("👤 Lynx Internet Fiber - Customer Profile Setup")

db = SessionLocal()
packages = db.query(Package).all()
sub_areas = db.query(SubArea).all()

if not packages or not sub_areas:
    st.warning("⚠️ Pehle 'Packages & Areas' waale page par ja kar settings complete karein!")
else:
    with st.form("add_customer_form"):
        col1, col2 = st.columns(2)
        with col1:
            c_code = st.text_input("Customer Code (Unique ID)", "LNX-001")
            c_name = st.text_input("Customer Name")
            f_name = st.text_input("Father Name")
            phone = st.text_input("Mobile / Contact Number")
        with col2:
            p_opts = {p.name: p.id for p in packages}
            sel_p = st.selectbox("Internet Plan / Package", list(p_opts.keys()))
            a_opts = {sa.name: sa.id for sa in sub_areas}
            sel_a = st.selectbox("Sub Area Link", list(a_opts.keys()))
            disc = st.number_input("Monthly Discount (PKR)", min_value=0, value=0)
            b_type = st.selectbox("Billing Cycle Type", ["Monthly-Fixed", "Card-System"])
            
        if st.form_submit_button("💾 Save Customer Profile"):
            new_c = Customer(
                customer_code=c_code, name=c_name, father_name=f_name, phone=phone,
                package_id=p_opts[sel_p], sub_area_id=a_opts[sel_a],
                monthly_discount=Decimal(disc), billing_type=BillingType(b_type), status=CustomerStatus.ACTIVE,
                registration_date=datetime.utcnow().date()
            )
            db.add(new_c)
            db.commit()
            st.success(f"🎉 Customer '{c_name}' successfully live database par add ho gaya!")
db.close()