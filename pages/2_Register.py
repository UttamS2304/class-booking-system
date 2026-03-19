import streamlit as st

st.set_page_config(page_title="Register", layout="wide")

st.title("Registration")
st.write("Choose your role")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales Person")
    st.page_link("pages/3_Sales_Register.py", label="Register as Sales Person")

with col2:
    st.subheader("Resource Person")
    st.page_link("pages/4_Resource_Register.py", label="Register as Resource Person")
