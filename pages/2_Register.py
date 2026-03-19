import streamlit as st

st.set_page_config(page_title="Register", layout="wide")

st.title("Registration")
st.write("Choose your role")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales Person")
    if st.button("Register as Sales Person"):
        st.switch_page("pages/3_Sales_Register.py")

with col2:
    st.subheader("Resource Person")
    if st.button("Register as Resource Person"):
        st.switch_page("pages/4_Resource_Register.py")
