import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Family Food Sync", page_icon="🍴")

# --- SIDEBAR ---
st.sidebar.title("👨‍👩‍👧‍👦 Family Members")
member = st.sidebar.radio("Select who is recording:", ["Rashida", "Danish", "Shamaila", "Shanzey", "Palwasha"])

st.title("🍴 Family Food Sync")

# Connection setup - using the ID from your secrets
conn = st.connection("gsheets", type=GSheetsConnection)

tab1, tab2, tab3 = st.tabs(["📝 Log Meal", "📊 Dashboard", "💡 Recommendations"])

# --- TAB 1: LOG MEAL ---
with tab1:
    st.subheader(f"Recording for: {member}")
    with st.form("entry_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.now())
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        food_item = st.text_input("What was eaten?")
        submit_button = st.form_submit_button("Save Entry")

    if submit_button and food_item:
        try:
            # Prepare new entry
            new_entry = pd.DataFrame([{
                "Date": date.strftime("%Y-%m-%d"),
                "Member": member,
                "Meal Type": meal_type,
                "Food": food_item
            }])
            
            # Using 'create' instead of 'update' to avoid the Response 200 bug
            conn.create(data=new_entry)
            
            st.success(f"✅ Entry saved! {member} ate {food_item}.")
            # Force clear cache so Dashboard updates immediately
            st.cache_data.clear()
        except Exception as e:
            # Silent fix for the Response 200 issue
            if "200" in str(e):
                st.success(f"✅ Entry saved! {member} ate {food_item}.")
                st.cache_data.clear()
            else:
                st.error(f"Error: {e}")

# --- TAB 2: DASHBOARD ---
with tab2:
    st.subheader("Recent Activity")
    try:
        # Fetch fresh data
        df = conn.read(ttl=0)
        if not df.empty:
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
        else:
            st.info("The sheet appears empty. If you just added data, refresh in 5 seconds.")
    except:
        st.error("Cannot load Dashboard. Check if the Sheet ID in Secrets is correct.")

# --- TAB 3: RECOMMENDATIONS ---
with tab3:
    st.subheader("Personalized Tips")
    try:
        df_rec = conn.read(ttl=0)
        user_history = df_rec[df_rec['Member'] == member]
        if not user_history.empty:
            last_meal = user_history.iloc[-1]['Food']
            st.write(f"Your last meal was: **{last_meal}**")
            if any(x in last_meal.lower() for x in ["mutton", "meat", "chicken", "puri", "halwa"]):
                st.warning("💡 That was a rich meal! Consider something lighter like fruit or yogurt next.")
            else:
                st.success("💡 Looking good! Keep up the variety.")
        else:
            st.info("Log a meal to see your tips.")
    except:
        st.write("Tips will appear here after your first log.")
