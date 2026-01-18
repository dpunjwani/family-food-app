import streamlit as st
import pandas as pd
import datetime
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Family Food Sync", layout="wide")

# --- FILE PATHS ---
LOG_FILE = "food_logs.csv"
PROFILE_FILE = "family_profiles.csv"

# --- DATA LOADING ---
def load_profiles():
    # Cleaned names in your preferred order
    default_order = ["Rashida", "Shamaila", "Shanzey", "Palwasha", "Danish Punjwani"]
    if os.path.exists(PROFILE_FILE):
        saved_profiles = pd.read_csv(PROFILE_FILE)['Name'].tolist()
        # Ensure the default names exist in the list
        for name in default_order:
            if name not in saved_profiles:
                saved_profiles.append(name)
        return saved_profiles
    return default_order

if 'family' not in st.session_state:
    st.session_state.family = load_profiles()

if 'logs' not in st.session_state:
    if os.path.exists(LOG_FILE):
        st.session_state.logs = pd.read_csv(LOG_FILE)
    else:
        st.session_state.logs = pd.DataFrame(columns=['Date', 'Member', 'Meal Type', 'Food'])

# --- SIDEBAR: Profile Selection ---
st.sidebar.title("👥 Family Profiles")

# Simple list for selection
selected_user = st.sidebar.radio("Who is logging?", st.session_state.family)

st.sidebar.divider()

# Add/Remove Section
with st.sidebar.expander("Manage List"):
    new_member = st.text_input("Add Name:")
    if st.button("Add"):
        if new_member and new_member not in st.session_state.family:
            st.session_state.family.append(new_member)
            pd.DataFrame(st.session_state.family, columns=['Name']).to_csv(PROFILE_FILE, index=False)
            st.rerun()

    member_to_remove = st.selectbox("Remove Name:", [""] + st.session_state.family)
    if st.button("Remove"):
        if member_to_remove:
            st.session_state.family.remove(member_to_remove)
            pd.DataFrame(st.session_state.family, columns=['Name']).to_csv(PROFILE_FILE, index=False)
            st.rerun()

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
        food_item = st.text_input("What was eaten?", placeholder="e.g., Daal Chawal, Pasta")
    
    if st.button("Save Entry", use_container_width=True):
        if food_item:
            new_entry = pd.DataFrame([[date, selected_user, meal_type, food_item]], 
                                    columns=['Date', 'Member', 'Meal Type', 'Food'])
            st.session_state.logs = pd.concat([st.session_state.logs, new_entry], ignore_index=True)
            st.session_state.logs.to_csv(LOG_FILE, index=False)
            st.success(f"Successfully logged for {selected_user}!")
        else:
            st.error("Please enter the food name.")

with tab2:
    if not st.session_state.logs.empty:
        st.write("### Recent History")
        st.dataframe(st.session_state.logs.sort_values(by="Date", ascending=False), use_container_width=True)
    else:
        st.info("No meals logged yet.")

with tab3:
    st.write("### Smart Recommendation")
    # Logic based on selected user
    user_data = st.session_state.logs[st.session_state.logs['Member'] == selected_user]
    if not user_data.empty:
        last_food = user_data.iloc[-1]['Food'].lower()
        if "chicken" in last_food or "meat" in last_food:
            st.info(f"Since {selected_user} recently had meat, maybe try a lighter vegetable dish today?")
        else:
            st.info(f"How about a high-protein meal for {selected_user} today?")
    else:
        st.write("Start logging to get personalized suggestions!")