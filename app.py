import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Page Config
st.set_page_config(page_title="Family Food Sync", page_icon="🍴")

# --- SIDEBAR: FAMILY SELECTION ---
st.sidebar.title("👨‍👩‍👧‍👦 Family Members")
member = st.sidebar.radio(
    "Select who is recording:",
    ["Rashida", "Danish", "Shamaila", "Shanzey", "Palwasha"]
)

st.title("🍴 Family Food Sync")

# Establish Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Create Tabs
tab1, tab2, tab3 = st.tabs(["📝 Log Meal", "📊 Dashboard", "💡 Recommendations"])

# --- TAB 1: LOG MEAL ---
with tab1:
    st.subheader(f"Recording for: {member}")
    
    with st.form("entry_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.now())
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        food_item = st.text_input("What was eaten?")
        submit_button = st.form_submit_button("Save Entry")

    if submit_button:
        if food_item:
            try:
                # 1. Fetch current data
                existing_data = conn.read(ttl=0)
                
                # 2. Prepare new entry
                new_entry = pd.DataFrame([{
                    "Date": date.strftime("%Y/%m/%d"),
                    "Member": member,
                    "Meal Type": meal_type,
                    "Food": food_item
                }])
                
                # 3. Combine
                updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
                
                # 4. Update the sheet
                conn.update(data=updated_df)
                
                st.success(f"✅ Entry saved! {member} ate {food_item}.")
            except Exception as e:
                # If we get the 'Response 200' error but the data actually saved
                if "200" in str(e):
                    st.success(f"✅ Entry saved! {member} ate {food_item}.")
                else:
                    st.error(f"Save failed: {e}")
        else:
            st.error("Please enter what was eaten.")

# --- TAB 2: DASHBOARD ---
with tab2:
    st.subheader("Recent Activity")
    try:
        data = conn.read(ttl=0)
        if not data.empty:
            st.dataframe(data.sort_index(ascending=False), use_container_width=True)
        else:
            st.info("The sheet is empty. Add your first meal!")
    except:
        st.error("Unable to load data. Please check your connection.")

# --- TAB 3: RECOMMENDATIONS ---
with tab3:
    st.subheader("Personalized Tips")
    try:
        df_rec = conn.read(ttl=0)
        if not df_rec.empty:
            # Filter for the active family member
            user_history = df_rec[df_rec['Member'] == member]
            
            if not user_history.empty:
                last_food = user_history.iloc[-1]['Food']
                st.write(f"Last meal for **{member}**: {last_food}")
                
                # Recommendation logic
                check_food = last_food.lower()
                if any(x in check_food for x in ["mutton", "meat", "chicken", "beef"]):
                    st.warning("💡 High Protein detected! Consider a fiber-rich meal like vegetables or fruits next.")
                else:
                    st.success("💡 Balanced choice! Keep maintaining this variety.")
            else:
                st.info(f"No history found for {member}. Start logging to get tips!")
        else:
            st.info("Log your first meal to see recommendations.")
    except:
        st.write("Complete your first log to activate tips.")

