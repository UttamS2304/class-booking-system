import streamlit as st

st.set_page_config(page_title="Register", layout="wide")

st.title("Registration")
st.write("Choose the type of registration")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales Person")
    st.write("Register as a sales person for Creative Kids or Little Genius.")
    if st.button("Go to Sales Registration"):
        st.switch_page("pages/3_Sales_Register.py")

with col2:
    st.subheader("Resource Person")
    st.write("Register as a resource person and select your subjects.")
    if st.button("Go to Resource Registration"):
        st.switch_page("pages/4_Resource_Register.py")
