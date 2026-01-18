import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Family Food Sync", page_icon="🍴")

# --- SIDEBAR ---
st.sidebar.title("👨‍👩‍👧‍👦 Family Members")
member = st.sidebar.radio("Select who is recording:", ["Rashida", "Danish", "Shamaila", "Shanzey", "Palwasha"])

st.title("🍴 Family Food Sync")
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
            # ttl=0 forces a fresh read
            existing_data = conn.read(ttl=0)
            new_entry = pd.DataFrame([{"Date": date.strftime("%Y/%m/%d"), "Member": member, "Meal Type": meal_type, "Food": food_item}])
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
            
            # Save to Google
            conn.update(data=updated_df)
            st.success(f"✅ Entry saved! {member} ate {food_item}.")
            st.cache_data.clear() # Clear memory to show new data in Dashboard
        except Exception as e:
            st.error(f"Connection Error: {e}")

# --- TAB 2: DASHBOARD ---
with tab2:
    st.subheader("Recent Activity")
    try:
        # ttl=0 ensures we see the newest logs immediately
        data = conn.read(ttl=0)
        if not data.empty:
            st.dataframe(data.sort_index(ascending=False), use_container_width=True)
        else:
            st.info("The sheet is empty.")
    except Exception as e:
        st.error("Cannot connect to the sheet. Ensure Drive API is enabled.")

# --- TAB 3: RECOMMENDATIONS ---
with tab3:
    st.subheader("Personalized Tips")
    try:
        df_rec = conn.read(ttl=0)
        user_history = df_rec[df_rec['Member'] == member]
        if not user_history.empty:
            last_food = user_history.iloc[-1]['Food']
            st.write(f"Last meal for **{member}**: {last_food}")
            if any(x in last_food.lower() for x in ["mutton", "meat", "chicken"]):
                st.warning("💡 High protein detected. Try some fruit or salad next!")
            else:
                st.success("💡 Looking balanced! Keep it up.")
        else:
            st.info("No logs found for you yet.")
    except:
        st.write("Complete a log to see tips.")
