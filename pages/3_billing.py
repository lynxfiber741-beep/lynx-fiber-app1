import streamlit as st
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, ForeignKey, Enum, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import enum

DATABASE_URL = "postgresql://postgres.snbmurjcggthdvxyxyrd:DlLaglY98SkOzDq2@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class InvoiceStatus(enum.Enum):
    UNPAID = "Unpaid"
    PARTIALLY_PAID = "Partially Paid"
    PAID = "Paid"

class PaymentMethod(enum.Enum):
    CASH = "Cash"
    BANK_TRANSFER = "Bank Transfer"
    EASYPAISA = "EasyPaisa"
    JAZZCASH = "JazzCash"

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    customer_code = Column(String, unique=True)
    name = Column(String)
    package_id = Column(Integer, ForeignKey('packages.id'))
    monthly_discount = Column(Numeric)

class Package(Base):
    __tablename__ = 'packages'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    sale_price = Column(Numeric)

class Invoice(Base):
    __tablename__ = 'invoices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String, unique=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    billing_month = Column(String)
    issue_date = Column(Date)
    due_date = Column(Date)
    base_amount = Column(Numeric)
    discount_applied = Column(Numeric)
    total_payable = Column(Numeric)
    status = Column(Enum(InvoiceStatus))

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    amount_paid = Column(Numeric)
    payment_date = Column(Date)
    payment_method = Column(Enum(PaymentMethod))

st.set_page_config(layout="wide")
st.title("💵 Invoicing & Recovery Ledger")

db = SessionLocal()
t1, t2 = st.tabs(["⚡ Bulk Generate Invoices", "💰 Receive Payments / Wasooli"])

# --- TAB 1: GENERATE INVOICES (Jaise video mein single-click generator tha) ---
with t1:
    st.subheader("Monthly Bill Invoice Generator")
    current_month = datetime.utcnow().strftime("%B %Y") # e.g., May 2026
    st.info(f"📅 Current Billing Cycle: **{current_month}**")
    
    col1, col2 = st.columns(2)
    with col1:
        issue_d = st.date_input("Invoice Issue Date", datetime.utcnow().date())
    with col2:
        due_d = st.date_input("Due Date", datetime.utcnow().date() + timedelta(days=10))

    if st.button("🚀 Generate All Pending Invoices"):
        customers = db.query(Customer).all()
        generated_count = 0
        
        for cust in customers:
            # Check agar is mahine ka bill pehle se bana hua hai toh dobara na bane
            exists = db.query(Invoice).filter(
                Invoice.customer_id == cust.id, 
                Invoice.billing_month == current_month
            ).first()
            
            if not exists:
                pack = db.query(Package).filter(Package.id == cust.package_id).first()
                base_amt = pack.sale_price if pack else Decimal(0)
                disc = cust.monthly_discount if cust.monthly_discount else Decimal(0)
                final_bill = base_amt - disc
                
                inv_num = f"INV-{cust.customer_code}-{datetime.utcnow().strftime('%y%m%d%H%M%S')}"
                
                new_inv = Invoice(
                    invoice_number=inv_num, customer_id=cust.id, billing_month=current_month,
                    issue_date=issue_d, due_date=due_d, base_amount=base_amt,
                    discount_applied=disc, total_payable=final_bill, status=InvoiceStatus.UNPAID
                )
                db.add(new_inv)
                generated_count += 1
                
        db.commit()
        if generated_count > 0:
            st.success(f"✅ Success! {generated_count} New Invoices automatically created for {current_month}!")
        else:
            st.warning("Sab customers ke bills pehle se generated hain!")

# --- TAB 2: RECEIVE PAYMENTS (Ledger Update) ---
with t2:
    st.subheader("Record Bill Collections")
    all_unpaid_invoices = db.query(Invoice, Customer).join(Customer, Invoice.customer_id == Customer.id).filter(Invoice.status != InvoiceStatus.PAID).all()
    
    if not all_unpaid_invoices:
        st.info("Kamaal hai! Koi bhi pending bills baki nahi hain.")
    else:
        inv_list = {f"{res.Customer.name} ({res.Invoice.invoice_number}) - Due: Rs.{res.Invoice.total_payable}": res.Invoice.id for res in all_unpaid_invoices}
        selected_inv_str = st.selectbox("Select Pending Invoice / User", list(inv_list.keys()))
        selected_inv_id = inv_list[selected_inv_str]
        
        target_invoice = db.query(Invoice).filter(Invoice.id == selected_inv_id).first()
        
        col3, col4 = st.columns(2)
        with col3:
            amt_rec = st.number_input("Amount Received (PKR)", min_value=1, max_value=int(target_invoice.total_payable), value=int(target_invoice.total_payable))
        with col4:
            pay_meth = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "EasyPaisa", "JazzCash"])
            
        if st.button("💾 Post Payment Ledger"):
            # Update Invoice Status
            target_invoice.status = InvoiceStatus.PAID if Decimal(amt_rec) == target_invoice.total_payable else InvoiceStatus.PARTIALLY_PAID
            
            # Save Payment Transaction Record
            new_pay = Payment(
                invoice_id=target_invoice.id, amount_paid=Decimal(amt_rec),
                payment_date=datetime.utcnow().date(), payment_method=PaymentMethod(pay_meth)
            )
            db.add(new_pay)
            db.commit()
            st.success("💰 Payment posted successfully! Ledger has been synchronized live.")

db.close()