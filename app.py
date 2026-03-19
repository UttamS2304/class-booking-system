import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Class Booking System", layout="wide")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Class Booking System")
st.write("Welcome to the class booking platform.")

st.markdown("### Choose an option from the sidebar")
st.info("Go to Login or Register from the left sidebar.")
