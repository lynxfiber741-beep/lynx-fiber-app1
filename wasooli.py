import streamlit as st
import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, Date, ForeignKey, Enum, Text, func
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# ==============================================================================
# 1. DATABASE CONNECTION (SUPABASE)
# ==============================================================================
DATABASE_URL = "postgresql://postgres.snbmurjcggthdvxyxyrd:DlLaglY98SkOzDq2@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

Base = declarative_base()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

# ==============================================================================
# 2. ENUMS & DATABASE MODELS
# ==============================================================================
class CustomerStatus(enum.Enum):
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    TERMINATED = "Terminated"

class BillingType(enum.Enum):
    MONTHLY_FIXED = "Monthly-Fixed"
    CARD_SYSTEM = "Card-System"

class InvoiceStatus(enum.Enum):
    UNPAID = "Unpaid"
    PARTIALLY_PAID = "Partially Paid"
    PAID = "Paid"

class PaymentMethod(enum.Enum):
    CASH = "Cash"
    BANK_TRANSFER = "Bank Transfer"
    EASYPAISA = "EasyPaisa"
    JAZZCASH = "JazzCash"

class ComplaintStatus(enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"

class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    packages = relationship("Package", back_populates="company", cascade="all, delete-orphan")

class Package(Base):
    __tablename__ = 'packages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete="CASCADE"), nullable=False)
    package_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    purchase_price = Column(Numeric(10, 2), nullable=False)
    sale_price = Column(Numeric(10, 2), nullable=False)
    company = relationship("Company", back_populates="packages")
    customers = relationship("Customer", back_populates="package")

class Area(Base):
    __tablename__ = 'areas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    sub_areas = relationship("SubArea", back_populates="area", cascade="all, delete-orphan")

class SubArea(Base):
    __tablename__ = 'sub_areas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    area_id = Column(Integer, ForeignKey('areas.id', ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    area = relationship("Area", back_populates="sub_areas")
    customers = relationship("Customer", back_populates="sub_area")

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    father_name = Column(String(100))
    phone = Column(String(20), nullable=False)
    package_id = Column(Integer, ForeignKey('packages.id'), nullable=False)
    sub_area_id = Column(Integer, ForeignKey('sub_areas.id'), nullable=False)
    monthly_discount = Column(Numeric(10, 2), default=0.00)
    status = Column(Enum(CustomerStatus), default=CustomerStatus.ACTIVE)
    billing_type = Column(Enum(BillingType), default=BillingType.MONTHLY_FIXED)
    registration_date = Column(Date, default=datetime.utcnow().date)
    package = relationship("Package", back_populates="customers")
    sub_area = relationship("SubArea", back_populates="customers")
    invoices = relationship("Invoice", back_populates="customer")
    complaints = relationship("Complaint", back_populates="customer")

class Invoice(Base):
    __tablename__ = 'invoices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete="CASCADE"), nullable=False)
    billing_month = Column(String(30), nullable=False)
    total_payable = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.UNPAID)
    customer = relationship("Customer", back_populates="invoices")

class Complaint(Base):
    __tablename__ = 'complaints'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.OPEN)
    customer = relationship("Customer", back_populates="complaints")

# Tables create karne ke liye background execution
Base.metadata.create_all(engine)

# ==============================================================================
# 3. STREAMLIT FRONTEND INTERFACE
# ==============================================================================
st.set_page_config(page_title="Lynx Fiber ISP Billing", layout="wide")

# Sidebar navigation
st.sidebar.title("Lynx Fiber Management")
menu = st.sidebar.radio("Go to:", ["Dashboard", "Customers Setup", "Packages & Areas", "Billing System"])

db = SessionLocal()

if menu == "Dashboard":
    st.title("📊 ISP Billing Dashboard Summary")
    
    # Query database for live metrics
    total_cust = db.query(Customer).count()
    active_cust = db.query(Customer).filter(Customer.status == CustomerStatus.ACTIVE).count()
    inactive_cust = db.query(Customer).filter(Customer.status != CustomerStatus.ACTIVE).count()
    total_complaints = db.query(Complaint).filter(Complaint.status == ComplaintStatus.OPEN).count()
    
    # Visual Cards (Jaise video mein tha)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", total_cust)
    col2.metric("Active Users", active_cust, delta_color="normal")
    col3.metric("Inactive Users", inactive_cust)
    col4.metric("Open Complaints", total_complaints)
    
    st.markdown("---")
    st.subheader("📋 Recent Active Customers")
    customers = db.query(Customer).limit(10).all()
    if customers:
        for c in customers:
            st.write(f"🔗 **{c.customer_code}** - {c.name} | Phone: {c.phone} | Status: `{c.status.value}`")
    else:
        st.info("Abhi tak koi customer add nahi kiya gaya.")

elif menu == "Customers Setup":
    st.title("👤 Add New ISP Customer")
    
    # Fetch packages and areas for selectors
    packages = db.query(Package).all()
    sub_areas = db.query(SubArea).all()
    
    if not packages or not sub_areas:
        st.warning("⚠️ Pehle 'Packages & Areas' menu mein ja kar Company, Package aur Area add karein!")
    else:
        with st.form("customer_form"):
            col1, col2 = st.columns(2)
            with col1:
                c_code = st.text_input("Customer Code (Unique)", "LNX-001")
                c_name = st.text_input("Full Name")
                f_name = st.text_input("Father Name")
                phone = st.text_input("Contact Number")
            with col2:
                pack_options = {p.name: p.id for p in packages}
                selected_pack = st.selectbox("Select Internet Package", list(pack_options.keys()))
                area_options = {sa.name: sa.id for sa in sub_areas}
                selected_area = st.selectbox("Select Sub Area", list(area_options.keys()))
                discount = st.number_input("Monthly Discount (Rs.)", min_value=0, value=0)
                b_type = st.selectbox("Billing Type", ["Monthly-Fixed", "Card-System"])
            
            submit = st.form_submit_button("Save Customer Profile")
            if submit:
                new_cust = Customer(
                    customer_code=c_code, name=c_name, father_name=f_name, phone=phone,
                    package_id=pack_options[selected_pack], sub_area_id=area_options[selected_area],
                    monthly_discount=Decimal(discount), billing_type=BillingType(b_type), status=CustomerStatus.ACTIVE
                )
                db.add(new_cust)
                db.commit()
                st.success(f"🎉 Customer {c_name} successfully add ho gaya!")

elif menu == "Packages & Areas":
    st.title("⚙️ Packages, Companies & Area Setup")
    
    tab1, tab2 = st.tabs(["Add Company & Package", "Add Area & Sub-Area"])
    
    with tab1:
        st.subheader("Add Upstream Company / Plan")
        comp_name = st.text_input("Company Name (e.g., PTCL Wholesale)")
        if st.button("Save Company"):
            if comp_name:
                db.add(Company(name=comp_name))
                db.commit()
                st.success("Company add ho gayi!")
        
        st.markdown("---")
        companies = db.query(Company).all()
        if companies:
            comp_dict = {c.name: c.id for c in companies}
            selected_comp = st.selectbox("Select Company for Package", list(comp_dict.keys()))
            p_code = st.text_input("Package Code (e.g., 10MB-NET)")
            p_name = st.text_input("Package Name (e.g., 10 Mbps Unlimited)")
            p_cost = st.number_input("Purchase Price (Cost)", min_value=0)
            p_sale = st.number_input("Sale Price (Retail Bill)", min_value=0)
            
            if st.button("Save Package Plan"):
                new_pack = Package(company_id=comp_dict[selected_comp], package_code=p_code, name=p_name, purchase_price=p_cost, sale_price=p_sale)
                db.add(new_pack)
                db.commit()
                st.success("Package system mein save ho gaya!")

    with tab2:
        st.subheader("Manage Areas")
        area_name = st.text_input("Main Area Name (e.g., Johar Town)")
        if st.button("Save Main Area"):
            if area_name:
                db.add(Area(name=area_name))
                db.commit()
                st.success("Main Area added!")
                
        st.markdown("---")
        areas = db.query(Area).all()
        if areas:
            area_dict = {a.name: a.id for a in areas}
            selected_m_area = st.selectbox("Select Main Area for Sub-Area", list(area_dict.keys()))
            sub_name = st.text_input("Sub-Area/Block Name (e.g., Block G3)")
            if st.button("Save Sub Area"):
                db.add(SubArea(area_id=area_dict[selected_m_area], name=sub_name))
                db.commit()
                st.success("Sub Area linked successfully!")

elif menu == "Billing System":
    st.title("💵 Invoice Generation & Bill Ledger")
    st.info("Is section se aap monthly invoices bulk mein generate aur manage kar sakte hain.")
    # Invoices and dynamic ledger handling details...
    st.write("Billing management screens load ho rahi hain...")

db.close()