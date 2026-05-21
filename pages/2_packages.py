import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql://postgres.snbmurjcggthdvxyxyrd:DlLaglY98SkOzDq2@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

class Package(Base):
    __tablename__ = 'packages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    package_code = Column(String, unique=True)
    name = Column(String)
    purchase_price = Column(Numeric)
    sale_price = Column(Numeric)

class Area(Base):
    __tablename__ = 'areas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

class SubArea(Base):
    __tablename__ = 'sub_areas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    area_id = Column(Integer, ForeignKey('areas.id'))
    name = Column(String)

st.set_page_config(layout="wide")
st.title("⚙️ Network Config: Packages & Geographical Areas")

db = SessionLocal()
t1, t2 = st.tabs(["🏢 Manage Companies & Plans", "📍 Area Mapping"])

with t1:
    st.subheader("Add Distribution Company")
    c_name = st.text_input("Upstream Provider Name (e.g., StormFiber)")
    if st.button("Add Company"):
        if c_name:
            db.add(Company(name=c_name))
            db.commit()
            st.success("Company Added!")

    st.markdown("---")
    comps = db.query(Company).all()
    if comps:
        c_dict = {c.name: c.id for c in comps}
        sel_c = st.selectbox("Select Company", list(c_dict.keys()))
        p_code = st.text_input("Plan Code", "10M-UNLIM")
        p_name = st.text_input("Plan Name", "10 Mbps Premium")
        p_cost = st.number_input("Cost Price", min_value=0)
        p_retail = st.number_input("Retail Price", min_value=0)
        if st.button("Save Internet Package"):
            db.add(Package(company_id=c_dict[sel_c], package_code=p_code, name=p_name, purchase_price=p_cost, sale_price=p_retail))
            db.commit()
            st.success("Package Configuration Active!")

with t2:
    st.subheader("Add Franchise Area")
    a_name = st.text_input("Main Hub Name (e.g., Gulberg)")
    if st.button("Add Hub"):
        if a_name:
            db.add(Area(name=a_name))
            db.commit()
            st.success("Main Hub Saved!")

    st.markdown("---")
    areas = db.query(Area).all()
    if areas:
        a_dict = {a.name: a.id for a in areas}
        sel_a = st.selectbox("Select Hub Location", list(a_dict.keys()))
        sub_n = st.text_input("Sector / Block Name (e.g., Block B2)")
        if st.button("Link Sub-Area"):
            db.add(SubArea(area_id=a_dict[sel_a], name=sub_n))
            db.commit()
            st.success("Sub-Area Linked Successfully!")

db.close()