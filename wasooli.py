import enum
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, Date, ForeignKey, Enum, Text
from sqlalchemy.orm import declarative_base, relationship

# ==============================================================================
# ✅ FIXED LIVE CONNECTION STRING (SUPABASE POSTGRESQL POOLER)
# ==============================================================================
DATABASE_URL = "postgresql://postgres.snbmurjcggthdvxyxyrd:DlLaglY98SkOzDq2@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

# Initialize SQLAlchemy Base and Engine
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=True)

# ==============================================================================
# 1. DATABASE ENUMS (Matching the Video's Core Workflow)
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


# ==============================================================================
# 2. DEFINING MASTER & TRANSACTIONAL TABLES
# ==============================================================================

class Company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
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
    cnic = Column(String(20))
    address = Column(Text)
    package_id = Column(Integer, ForeignKey('packages.id'), nullable=False)
    sub_area_id = Column(Integer, ForeignKey('sub_areas.id'), nullable=False)
    monthly_discount = Column(Numeric(10, 2), default=0.00)
    security_deposit = Column(Numeric(10, 2), default=0.00)
    connection_charges = Column(Numeric(10, 2), default=0.00)
    billing_type = Column(Enum(BillingType), default=BillingType.MONTHLY_FIXED)
    status = Column(Enum(CustomerStatus), default=CustomerStatus.ACTIVE)
    registration_date = Column(Date, default=datetime.utcnow().date)
    
    package = relationship("Package", back_populates="customers")
    sub_area = relationship("SubArea", back_populates="customers")
    invoices = relationship("Invoice", back_populates="customer", cascade="all, delete-orphan")
    complaints = relationship("Complaint", back_populates="customer", cascade="all, delete-orphan")

class Invoice(Base):
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete="CASCADE"), nullable=False)
    billing_month = Column(String(30), nullable=False)  # e.g., "October 2026"
    issue_date = Column(Date, default=datetime.utcnow().date)
    due_date = Column(Date, nullable=False)
    base_amount = Column(Numeric(10, 2), nullable=False)  # Preserves rate history
    discount_applied = Column(Numeric(10, 2), default=0.00)
    previous_arrears = Column(Numeric(10, 2), default=0.00)
    total_payable = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.UNPAID)
    
    customer = relationship("Customer", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id', ondelete="CASCADE"), nullable=False)
    amount_paid = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.CASH)
    notes = Column(Text)
    
    invoice = relationship("Invoice", back_populates="payments")

class Complaint(Base):
    __tablename__ = 'complaints'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.OPEN)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    customer = relationship("Customer", back_populates="complaints")

class Expense(Base):
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100), nullable=False)  # e.g., "Salary", "Rent"
    expense_date = Column(Date, default=datetime.utcnow().date)


# ==============================================================================
# 3. DIRECT EXECUTION
# ==============================================================================
if __name__ == "__main__":
    print("🔄 Establishing secure tunnel to Supabase...")
    try:
        # Generates all schemas, types, and constraints directly inside Postgres
        Base.metadata.create_all(engine)
        print("\n✅ PERFECT! All ISP Management tables generated live on your Supabase engine.")
    except Exception as e:
        print("\n❌ Migration halted due to connection or execution error:")
        print(e)