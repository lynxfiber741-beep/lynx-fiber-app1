import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- APP CONFIGURATION ---
st.set_page_config(page_title="LYNX Fiber - Wasooli Dashboard", layout="wide", page_icon="⚡")
st.title("⚡ LYNX Fiber - WasooliPK Style Billing System")
st.markdown("---")

# --- SUPABASE SECURE CONNECTION ---
# Security rule ke mutabiq credentials cloud secrets se load ho rahe hain
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase: Client = init_supabase()
except Exception as e:
    st.error(f"Supabase Connection Error: Secrets config check karein. {e}")

# Live Timing calculations
current_month = datetime.now().strftime("%B")
current_year = datetime.now().strftime("%Y")
today_date = datetime.now().strftime("%Y-%m-%d")


# --- SIDEBAR CONTROLS ---
st.sidebar.header("➕ Wasooli Management")

# Feature 1: Naya Customer Add Karna
with st.sidebar.expander("📝 Naya Customer Add Karein", expanded=False):
    with st.form("add_user_form", clear_on_submit=True):
        new_name = st.text_input("Customer Name")
        new_username = st.text_input("PPPoE / Router ID (Unique)")
        new_phone = st.text_input("Phone Number")
        new_area = st.text_input("Area / Colony (e.g., Jhelum Cantt)")
        new_bill = st.number_input("Monthly Bill (Rs.)", min_value=0, step=100)
        submit_user = st.form_submit_button("Save Customer")
        
        if submit_user:
            if new_name and new_username and new_area and new_bill > 0:
                try:
                    data = {
                        "name": new_name,
                        "username": new_username,
                        "phone": new_phone,
                        "area": new_area,
                        "monthly_bill": new_bill,
                        "status": "Unpaid"
                    }
                    supabase.table("billing_users").insert(data).execute()
                    st.success(f"✔️ {new_name} database mein save ho gaya!")
                    st.rerun()
                except Exception:
                    st.error("❌ Error: Yeh Username pehle se kisi customer ka hai!")
            else:
                st.warning("⚠️ Meherbani karke saari details sahi bharein.")

# Feature 2: Monthly Cycle Reset (Sabh ko Unpaid karna)
st.sidebar.markdown("---")
if st.sidebar.button("🔄 New Month Reset (Sabh ko Unpaid Karein)"):
    try:
        supabase.table("billing_users").update({"status": "Unpaid"}).neq("id", 0).execute()
        st.sidebar.success("Saray users ka status dubara Unpaid ho gaya!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Reset fail: {e}")


# --- FETCH DATA FROM CLOUD DATABASE ---
try:
    users_resp = supabase.table("billing_users").select("*").order("name").execute()
    history_resp = supabase.table("billing_history").select("*").execute()
    
    df_users = pd.DataFrame(users_resp.data)
    df_history = pd.DataFrame(history_resp.data)
except Exception as e:
    st.info("👋 Welcome! Agar app pehli baar chal rahi hai, to database tables setup zaroori hain.")
    df_users = pd.DataFrame()
    df_history = pd.DataFrame()


# --- MAIN DASHBOARD INTERFACE ---
if not df_users.empty:
    # Top Live Counters
    total_users = len(df_users)
    paid_users = len(df_users[df_users['status'] == 'Paid'])
    unpaid_users = len(df_users[df_users['status'] == 'Unpaid'])
    
    if not df_history.empty:
        today_collection = df_history[df_history['pay_date'] == today_date]['amount'].sum()
        monthly_collection = df_history[(df_history['pay_month'] == current_month) & (df_history['pay_year'] == current_year)]['amount'].sum()
    else:
        today_collection = 0
        monthly_collection = 0

    # 📊 Live Metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("👥 Total Users", f"{total_users}")
    m2.metric("✅ Paid Users", f"{paid_users}", delta=f"{paid_users} Collected")
    m3.metric("❌ Unpaid Users", f"{unpaid_users}", delta=f"-{unpaid_users} Remaining", delta_color="inverse")
    m4.metric("💰 Today's Cash", f"Rs. {today_collection:,.0f}")
    m5.metric(f"📅 Revenue ({current_month})", f"Rs. {monthly_collection:,.0f}")
    
    st.markdown("---")

    # 📍 AREA WISE FILTERING
    st.subheader("📍 Area Wise Sorting (Colony Tracker)")
    unique_areas = ["All Areas"] + list(df_users['area'].unique())
    selected_area = st.selectbox("Apna Sector/Area Select Karein:", unique_areas)
    
    filtered_df = df_users if selected_area == "All Areas" else df_users[df_users['area'] == selected_area]

    # Area summary display
    a_total = len(filtered_df)
    a_paid = len(filtered_df[filtered_df['status'] == 'Paid'])
    a_unpaid = len(filtered_df[filtered_df['status'] == 'Unpaid'])
    st.caption(f"📊 Filtering Status -> **Total:** {a_total} | **Paid:** {a_paid} | **Unpaid:** {a_unpaid}")

    # 📋 CUSTOMERS ACTIVE LIST & RECOVERY BUTTONS
    st.markdown("### 📋 Client Active Directory & Quick Pay")
    
    for index, row in filtered_df.iterrows():
        status_label = "🟢 Paid" if row['status'] == 'Paid' else "🔴 Unpaid"
        
        c1, c2, c3, c4, c5 = st.columns([2, 2, 1.5, 1.5, 1.5])
        c1.markdown(f"**{row['name']}** ({row['username']})")
        c2.markdown(f"📍 {row['area']} | 📞 {row['phone'] if row['phone'] else 'N/A'}")
        c3.markdown(f"💵 Bill: **Rs. {float(row['monthly_bill']):.0f}**")
        c4.markdown(f"Status: **{status_label}**")
        
        if row['status'] == 'Unpaid':
            if c5.button("Receive Bill 💵", key=f"pay_{row['id']}"):
                # 1. Update user status to Paid in cloud
                supabase.table("billing_users").update({"status": "Paid", "last_paid_date": today_date}).eq("id", row['id']).execute()
                
                # 2. History table mein automatic ledger record update
                hist_data = {
                    "user_id": int(row['id']),
                    "name": row['name'],
                    "area": row['area'],
                    "amount": float(row['monthly_bill']),
                    "pay_date": today_date,
                    "pay_month": current_month,
                    "pay_year": current_year
                }
                supabase.table("billing_history").insert(hist_data).execute()
                
                st.success(f"💸 {row['name']} ka bill record ho gaya!")
                st.rerun()
        else:
            c5.markdown(f"📆 Paid: `{row['last_paid_date']}`")
            
        st.markdown("<hr style='margin: 0.3em 0px; opacity: 0.2;'>", unsafe_allow_html=True)

    # 📚 SAALANA RECORD LEDGER
    st.markdown("---")
    st.subheader("📚 Business Annual Ledger (Saal ka Mukammal Record)")
    
    if not df_history.empty:
        t1, t2 = st.tabs(["📋 Detailed Log Sheet", "🗓️ Monthly Summary Overview"])
        with t1:
            st.dataframe(df_history[['name', 'area', 'amount', 'pay_date', 'pay_month', 'pay_year']].sort_index(ascending=False), use_container_width=True)
        with t2:
            summary_df = df_history.groupby(['pay_year', 'pay_month'])['amount'].sum().reset_index()
            summary_df.columns = ['Year', 'Month', 'Total Collection (Rs.)']
            st.table(summary_df)
    else:
        st.info("Abhi tak database mein koi billing payment history transaction nahi hui.")
else:
    st.info("👋 Welcome LYNX Fiber! Sidebar khol kar sab se pehle naye customers add karein.")