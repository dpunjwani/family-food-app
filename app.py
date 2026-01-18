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

st.title(f"🍴 Family Food Sync")

# Establish Connection using the secrets we set up
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
                # Read existing data using the URL defined in secrets
                existing_data = conn.read()
                
                # Create new row
                new_entry = pd.DataFrame([{
                    "Date": date.strftime("%Y/%m/%d"),
                    "Member": member,
                    "Meal Type": meal_type,
                    "Food": food_item
                }])
                
                # Combine and Update
                updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
                conn.update(data=updated_df)
                
                st.success(f"✅ Entry saved! {member} ate {food_item}.")
            except Exception as e:
                st.error(f"Error saving to Google Sheets: {e}")
        else:
            st.error("Please enter the food name.")

# --- TAB 2: DASHBOARD ---
with tab2:
    st.subheader("Recent Meals")
    try:
        data = conn.read()
        if not data.empty:
            # Show only the current person's meals or all? Let's show all but highlight
            st.dataframe(data.sort_index(ascending=False), use_container_width=True)
        else:
            st.write("The sheet is empty. Start logging!")
    except Exception as e:
        st.error("Could not load data from Google Sheets. Check your Secrets.")

# --- TAB 3: RECOMMENDATIONS ---
with tab3:
    st.subheader("Health Feedback")
    try:
        df_rec = conn.read()
        if not df_rec.empty:
            # Filter data for the selected family member
            user_data = df_rec[df_rec['Member'] == member]
            
            if not user_data.empty:
                last_food = user_data.iloc[-1]['Food']
                st.write(f"Hey **{member}**, your last recorded meal was: **{last_food}**")
                
                # Recommendation Logic
                food_lower = last_food.lower()
                if any(word in food_lower for word in ["meat", "mutton", "chicken", "beef", "kebab"]):
                    st.info("💡 You had a high-protein meal. Consider adding some fiber/vegetables in your next meal!")
                else:
                    st.info("💡 That looks like a balanced start! Keep it up.")
            else:
                st.write(f"No previous meals found for {member} yet.")
        else:
            st.write("Log a meal to see personalized tips!")
    except:
        st.write("Log some data to get recommendations.")
