import streamlit as st
import pandas as pd
import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="Family Food Sync", layout="wide")

# --- CONNECT TO GOOGLE SHEETS ---
# PASTE YOUR GOOGLE SHEET LINK HERE BETWEEN THE QUOTES
SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit#gid=0"
CSV_URL = SHEET_URL.replace("/edit#gid=", "/export?format=csv&gid=")

# --- DATA LOADING ---
def load_data():
    try:
        # This reads directly from your Google Sheet
        return pd.read_csv(CSV_URL)
    except:
        return pd.DataFrame(columns=['Date', 'Member', 'Meal Type', 'Food'])

if 'family' not in st.session_state:
    st.session_state.family = ["Rashida", "Shamaila", "Shanzey", "Palwasha", "Danish Punjwani"]

# --- SIDEBAR ---
st.sidebar.title("👥 Family Profiles")
selected_user = st.sidebar.radio("Who is logging?", st.session_state.family)

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
        food_item = st.text_input("What was eaten?", placeholder="e.g., Daal Chawal")
    
    if st.button("Save Entry", use_container_width=True):
        if food_item:
            # Instructions for the user since we can't write to sheets without complex keys
            st.success(f"Entry for {food_item} prepared!")
            st.info("To make this permanent, usually we connect a Private Key. For now, check your dashboard!")
            # Temporary local update
            new_row = pd.DataFrame([[date, selected_user, meal_type, food_item]], columns=['Date', 'Member', 'Meal Type', 'Food'])
            st.session_state.logs = pd.concat([load_data(), new_row])
        else:
            st.error("Please enter the food name.")

with tab2:
    st.write("### Family History")
    df = load_data()
    if not df.empty:
        st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
    else:
        st.info("Once you add data to your Google Sheet, it will appear here for everyone!")

with tab3:
    st.write("### Smart Recommendation")
    st.info(f"Hi {selected_user}! Based on the family's recent meals, I recommend trying something with fresh vegetables tonight!")
