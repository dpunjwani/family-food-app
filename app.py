import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Page Config
st.set_page_config(page_title="Family Food Sync", page_icon="🍴")
st.title("🍴 Family Food Sync")

# Establish Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Create Tabs
tab1, tab2, tab3 = st.tabs(["📝 Log Meal", "📊 Dashboard", "💡 Recommendations"])

# --- TAB 1: LOG MEAL ---
with tab1:
    st.subheader(f"Recording for: Rashida")
    
    with st.form("entry_form"):
        date = st.date_input("Date", datetime.now())
        member = "Rashida"  # Fixed for your specific use
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        food_item = st.text_input("What was eaten?")
        
        submit_button = st.form_submit_button("Save Entry")

    if submit_button:
        if food_item:
            # Fetch existing data
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
            
            st.success(f"Entry saved! {member} ate {food_item}.")
            st.info("Refresh the page in a moment to see it in the Dashboard.")
        else:
            st.error("Please enter the food name.")

# --- TAB 2: DASHBOARD ---
with tab2:
    st.subheader("Recent Meals")
    data = conn.read()
    if not data.empty:
        st.dataframe(data.sort_index(ascending=False))
    else:
        st.write("No data found yet.")

# --- TAB 3: RECOMMENDATIONS (THE FIX IS HERE) ---
with tab3:
    st.subheader("What should you eat next?")
    df_rec = conn.read()
    
    if not df_rec.empty:
        # We define last_food here so line 80 doesn't crash
        last_food = df_rec.iloc[-1]['Food']
        
        st.write(f"Since your last meal was **{last_food}**...")
        
        # Line 80: The logic check
        if "chicken" in last_food.lower() or "meat" in last_food.lower() or "mutton" in last_food.lower():
            st.success("💡 Suggestion: You've had some heavy protein! Maybe try something light like a Salad or Daal Chawal for the next meal.")
        else:
            st.success("💡 Suggestion: Looking good! How about some grilled chicken or fish for some lean protein?")
    else:
        st.write("Log a meal first to get recommendations!")
