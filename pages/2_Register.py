import streamlit as st

st.title("Register")
st.write("Choose registration type")

col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/3_Sales_Register.py", label="Sales Person Registration")

with col2:
    st.page_link("pages/4_Resource_Register.py", label="Resource Person Registration")
