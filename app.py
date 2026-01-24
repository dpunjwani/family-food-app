import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="Family Food Sync", layout="wide")

# --- 1. CONNECTION SETUP ---
# This looks for the [connections.gsheets] in your Streamlit Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. DATA LOADING ---
def load_data():
    # ttl=0 ensures we don't show old cached data after saving
    return conn.read(worksheet="Sheet1", ttl=0)

df = load_data()

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("🍴 Family Food App")
page = st.sidebar.selectbox("Go to", ["Data Entry", "Dashboard", "Recommendations"])

# --- PAGE 1: DATA ENTRY ---
if page == "Data Entry":
    st.header("📝 Log New Meal")
    
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date")
            member = st.selectbox("Family Member", ["Rashida", "Danish", "Shamaila", "Shanzey", "Palwasha"])
        with col2:
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
            food = st.text_input("What was eaten?")
        
        submit = st.form_submit_button("Save Entry")
        
        if submit:
            if food:
                # Create a new row
                new_data = pd.DataFrame([{
                    "Date": str(date),
                    "Member": member,
                    "Meal Type": meal_type,
                    "Food": food
                }])
                
                # Combine with existing data
                updated_df = pd.concat([df, new_data], ignore_index=True)
                
                # Push back to Google Sheets
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success(f"Successfully saved: {food} for {member}!")
                st.balloons()
            else:
                st.error("Please enter the food details before saving.")

# --- PAGE 2: DASHBOARD ---
elif page == "Dashboard":
    st.header("📊 Eating Habits Dashboard")
    
    if not df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Entries by Member")
            fig1 = px.pie(df, names="Member", hole=0.3)
            st.plotly_chart(fig1)
            
        with col2:
            st.subheader("Meal Type Distribution")
            fig2 = px.bar(df, x="Meal Type", color="Member", barmode="group")
            st.plotly_chart(fig2)
            
        st.subheader("Recent History")
        st.dataframe(df.tail(10), use_container_width=True)
    else:
        st.warning("No data found in the Google Sheet yet.")

# --- PAGE 3: RECOMMENDATIONS ---
elif page == "Recommendations":
    st.header("💡 Meal Recommendations")
    
    if not df.empty:
        last_meal = df.iloc[-1]
        st.info(f"The last meal logged was **{last_meal['Food']}** by **{last_meal['Member']}**.")
        
        # Simple Logic: Suggest something different from the last meal type
        if last_meal['Meal Type'] == 'Breakfast':
            st.write("### Suggestion for Lunch:")
            st.success("How about a fresh salad or a chicken sandwich?")
        elif last_meal['Meal Type'] == 'Lunch':
            st.write("### Suggestion for Dinner:")
            st.success("Consider a light pasta dish or grilled vegetables.")
        else:
            st.write("### Suggestion for Tomorrow:")
            st.success("How about starting the day with some fruits and oats?")
    else:
        st.warning("Log some meals first to get recommendations!")
