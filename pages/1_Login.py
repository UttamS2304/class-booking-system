import streamlit as st

st.set_page_config(page_title="Login", layout="wide")

st.title("Login")
st.write("Login with your email or mobile number")

identifier = st.text_input("Email or Mobile Number")
password = st.text_input("Password", type="password")

if st.button("Login"):
    st.info("Login logic will be connected next.")
