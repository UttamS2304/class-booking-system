import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Class Booking System", layout="wide")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Class Booking System")
st.write("Welcome to the class booking platform.")

col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/1_Login.py", label="Login")

with col2:
    st.page_link("pages/2_Register.py", label="Register")
