import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="Family Food Sync", layout="wide")

# --- GOOGLE SHEET SETUP ---
# Your specific link integrated
SHEET_URL = "https://docs.google.com/spreadsheets/d/1E26HheF-2lr22MMkWQSB5CG8qlJ1D0r2OVyJptrpcbQ/edit?usp=sharing"

# Create connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Load data from the sheet
try:
    df = conn.read(spreadsheet=SHEET_URL, ttl="0")
    df = df.dropna(how="all")
except Exception:
    df = pd.DataFrame(columns=['Date', 'Member', 'Meal Type', 'Food'])

# --- SIDEBAR: PROFILES ---
st.sidebar.title("👥 Family Profiles")
family_list = ["Rashida", "Shamaila", "Shanzey", "Palwasha", "Danish Punjwani"]
selected_user = st.sidebar.radio("Who is logging?", family_list)

# --- MAIN UI ---
st.title("🍽️ Family Food Sync")
st.subheader(f"Recording for: {selected_user}")

tab1, tab2, tab3 = st.tabs(["📝 Log Meal", "📊 Dashboard", "💡 Recommendations"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date", datetime.date.today())
        meal_type = st.selectbox("Meal Type", ["Lunch", "Dinner"])
    with col2:
        food_item = st.text_input("What was eaten?", placeholder="e.g., Daal Chawal, Biryani")
    
    if st.button("Save Entry", use_container_width=True):
        if food_item:
            # Create the new row
            new_row = pd.DataFrame([{
                "Date": str(date),
                "Member": selected_user,
                "Meal Type": meal_type,
                "Food": food_item
            }])
            
            # Combine current sheet data with the new entry
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            # Write back to Google Sheets
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            st.success(f"Entry saved! {selected_user} ate {food_item}.")
            st.balloons()
            st.info("Refresh the page in a moment to see it in the Dashboard.")
        else:
            st.error("Please enter a food item before saving.")

with tab2:
    st.write("### Family Eating History")
    if not df.empty:
        # Show latest meals at the top
        st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
    else:
        st.info("The history is empty. Start logging meals to see them here!")

with tab3:
    st.write("### Smart Recommendation")
    user_data = df[df['Member'] == selected_user]
    
    if not user_data.empty:
        last_meal = user_data.iloc[-1]['Food']
        st.write(f"The last meal recorded for **{selected_user}** was **{last_meal}**.")
        
        # Simple Logic
        if "chicken" in last_food.lower() or "meat" in last_food.lower():
            st.success("💡 Recommendation: How about a light vegetarian dish like Sabzi or Daal today?")
        else:
            st.success("💡 Recommendation: Maybe try some protein like Grilled Fish or Chicken Karahi today!")
    else:
        st.write("Log at least one meal to get personalized suggestions!")
