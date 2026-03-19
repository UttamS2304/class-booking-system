import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Class Booking System", layout="wide")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# UI
st.title("Class Booking System")
st.write("Welcome to the class booking platform.")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Login")
    st.write("Already registered? Login here.")
    if st.button("Go to Login"):
        st.switch_page("pages/1_Login.py")

with col2:
    st.subheader("Register")
    st.write("New user? Create an account.")
    if st.button("Go to Register"):
        st.switch_page("pages/2_Register.py")
