import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(page_title="Class Booking System", layout="wide")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------- session init ----------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "user_mobile" not in st.session_state:
    st.session_state.user_mobile = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None


# ---------- helpers ----------
def go_to(page_name: str):
    st.session_state.page = page_name
    st.rerun()


def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_name = None
    st.session_state.user_mobile = None
    st.session_state.user_email = None
    st.session_state.page = "home"
    st.rerun()


def show_home():
    st.title("Class Booking System")
    st.write("Welcome to the class booking platform.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Login")
        st.write("Already registered? Login here.")
        if st.button("Go to Login", use_container_width=True):
            go_to("login")

    with col2:
        st.subheader("Register")
        st.write("New user? Create an account.")
        if st.button("Go to Register", use_container_width=True):
            go_to("register")


def show_register_choice():
    st.title("Registration")
    st.write("Choose your role")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sales Person")
        st.write("Register as a sales person for Creative Kids or Little Genius.")
        if st.button("Register as Sales Person", use_container_width=True):
            go_to("sales_register")

    with col2:
        st.subheader("Resource Person")
        st.write("Register as a resource person and select your subjects.")
        if st.button("Register as Resource Person", use_container_width=True):
            go_to("resource_register")

    st.markdown("---")
    if st.button("Back to Home"):
        go_to("home")


def show_login():
    st.title("Login")
    st.write("Login with your email or mobile number")
    st.markdown("---")

    identifier = st.text_input("Email or Mobile Number")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login", use_container_width=True):
            if not identifier or not password:
                st.error("Please enter identifier and password.")
                return

            try:
                result = (
                    supabase.table("users")
                    .select("*")
                    .or_(f"email.eq.{identifier},mobile_number.eq.{identifier}")
                    .eq("password", password)
                    .execute()
                )

                if result.data and len(result.data) > 0:
                    user = result.data[0]

                    st.session_state.logged_in = True
                    st.session_state.user_role = user["role"]
                    st.session_state.user_name = user["name"]
                    st.session_state.user_mobile = user["mobile_number"]
                    st.session_state.user_email = user["email"]

                    if user["role"] == "sales":
                        go_to("sales_dashboard")
                    elif user["role"] == "resource":
                        go_to("resource_dashboard")
                    elif user["role"] == "admin":
                        go_to("admin_dashboard")
                    else:
                        st.error("Invalid user role.")
                else:
                    st.error("Invalid login credentials.")

            except Exception as e:
                st.error(f"Login failed: {e}")

    with col2:
        if st.button("Back to Home", use_container_width=True):
            go_to("home")


def show_sales_register():
    st.title("Sales Person Registration")
    st.markdown("---")

    with st.form("sales_registration_form"):
        brand = st.selectbox("Select Brand", ["creative_kids", "little_genius"])
        name = st.text_input("Name")
        mobile = st.text_input("Mobile Number")
        email = st.text_input("Email")
        area = st.text_input("Area")
        designation = st.text_input("Designation")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Register", use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Register"):
            go_to("register")
    with col2:
        if st.button("Back to Home"):
            go_to("home")

    if submitted:
        if not name or not mobile or not email or not area or not designation or not password:
            st.error("Please fill all fields.")
            return

        try:
            existing_user = (
                supabase.table("users")
                .select("id")
                .or_(f"email.eq.{email},mobile_number.eq.{mobile}")
                .execute()
            )

            if existing_user.data:
                st.error("User with same email or mobile already exists.")
                return

            user_data = {
                "name": name,
                "mobile_number": mobile,
                "email": email,
                "role": "sales",
                "password": password,
                "created_at": datetime.utcnow().isoformat()
            }

            user_res = supabase.table("users").insert(user_data).execute()

            if not user_res.data:
                st.error("Unable to create user.")
                return

            user_id = user_res.data[0]["id"]

            sales_data = {
                "user_id": user_id,
                "mobile_number": mobile,
                "brand_type": brand,
                "area": area,
                "designation": designation
            }

            supabase.table("sales_profiles").insert(sales_data).execute()
            st.success("Sales person registered successfully.")
            st.info("Now go to Login page and login.")
        except Exception as e:
            st.error(f"Registration failed: {e}")


def show_resource_register():
    st.title("Resource Person Registration")
    st.markdown("---")

    # Placeholder subjects; baad me final list replace kar dena
    subject_options = [
        "Math",
        "Science",
        "English",
        "EVS",
        "GK",
        "Hindi",
        "Computer"
    ]

    with st.form("resource_registration_form"):
        name = st.text_input("Name")
        mobile = st.text_input("Mobile Number")
        email = st.text_input("Email")
        subject_1 = st.selectbox("Subject 1", subject_options)
        subject_2 = st.selectbox("Subject 2", subject_options, index=1 if len(subject_options) > 1 else 0)
        subject_3 = st.selectbox("Subject 3", subject_options, index=2 if len(subject_options) > 2 else 0)
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Register", use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Register"):
            go_to("register")
    with col2:
        if st.button("Back to Home"):
            go_to("home")

    if submitted:
        if not name or not mobile or not email or not password:
            st.error("Please fill all required fields.")
            return

        try:
            existing_user = (
                supabase.table("users")
                .select("id")
                .or_(f"email.eq.{email},mobile_number.eq.{mobile}")
                .execute()
            )

            if existing_user.data:
                st.error("User with same email or mobile already exists.")
                return

            user_data = {
                "name": name,
                "mobile_number": mobile,
                "email": email,
                "role": "resource",
                "password": password,
                "created_at": datetime.utcnow().isoformat()
            }

            user_res = supabase.table("users").insert(user_data).execute()

            if not user_res.data:
                st.error("Unable to create user.")
                return

            user_id = user_res.data[0]["id"]

            resource_data = {
                "user_id": user_id,
                "mobile_number": mobile,
                "subject_1": subject_1,
                "subject_2": subject_2,
                "subject_3": subject_3
            }

            supabase.table("resource_profiles").insert(resource_data).execute()
            st.success("Resource person registered successfully.")
            st.info("Now go to Login page and login.")
        except Exception as e:
            st.error(f"Registration failed: {e}")


def show_sales_dashboard():
    st.title("Sales Dashboard")
    st.write(f"Welcome, {st.session_state.user_name}")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Book Class",
        "Class Status",
        "All Classes",
        "Add Feedback"
    ])

   with tab1:
    st.subheader("Book a Class")

    with st.form("booking_form"):

        session_type = st.selectbox(
            "Session Type",
            ["live_class", "product_training", "avrd", "workshop"]
        )

        school_name = st.text_input("School Name")
        school_grade = st.text_input("School Grade")

        subject = None
        class_standard = None

        # Conditional fields
        if session_type in ["live_class", "product_training"]:
            subject = st.text_input("Subject")

        if session_type == "live_class":
            class_standard = st.text_input("Class / Standard")

        preferred_date = st.date_input("Preferred Date")

        preferred_time = st.text_input("Preferred Time Slot")

        curriculum = st.text_input("Curriculum")
        book_title = st.text_input("Book Title")
        area = st.text_input("Area / Location")

        submitted = st.form_submit_button("Submit Booking")

    if submitted:
        try:
            booking_data = {
                "sales_person_number": st.session_state.user_mobile,
                "resource_person_number": None,
                "brand_type": "creative_kids",  # abhi hardcoded, baad me dynamic karenge
                "session_type": session_type,
                "duration_minutes": 45,
                "school_name": school_name,
                "school_grade": school_grade,
                "subject": subject,
                "class_standard": class_standard,
                "preferred_date": str(preferred_date),
                "preferred_time_slot": preferred_time,
                "curriculum": curriculum,
                "book_title": book_title,
                "area_location": area,
                "status": "pending"
            }

            supabase.table("bookings").insert(booking_data).execute()

            st.success("Class booking request submitted ✅")

        except Exception as e:
            st.error(f"Error: {e}")

    with tab2:
        st.info("Class status yahan dikhengi.")

    with tab3:
        st.info("All previous classes yahan dikhengi.")

    with tab4:
        st.info("Feedback form yahan aayega.")

    if st.button("Logout"):
        logout()


def show_resource_dashboard():
    st.title("Resource Dashboard")
    st.write(f"Welcome, {st.session_state.user_name}")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Upcoming Classes",
        "Completed Classes",
        "Availability",
        "Add Remark"
    ])

    with tab1:
        st.info("Upcoming classes yahan dikhengi.")

    with tab2:
        st.info("Completed classes aur sales feedback yahan dikhengi.")

    with tab3:
        st.info("Availability marking yahan hoga.")

    with tab4:
        st.info("Remark / feedback yahan hoga.")

    if st.button("Logout"):
        logout()


def show_admin_dashboard():
    st.title("Admin Dashboard")
    st.write(f"Welcome, {st.session_state.user_name}")
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "All Class Bookings",
        "Sales Persons Manage",
        "Class Status",
        "Resource Person Manage",
        "Feedback",
        "Reports"
    ])

    with tab1:
        st.info("All class bookings yahan dikhengi.")

    with tab2:
        st.info("Sales persons manage yahan hoga.")

    with tab3:
        st.info("Approve / reject classes yahan hoga.")

    with tab4:
        st.info("Resource persons manage yahan hoga.")

    with tab5:
        st.info("Feedback yahan dikhengi.")

    with tab6:
        st.info("Reports yahan dikhengi.")

    if st.button("Logout"):
        logout()


# ---------- router ----------
page = st.session_state.page

if page == "home":
    show_home()
elif page == "login":
    show_login()
elif page == "register":
    show_register_choice()
elif page == "sales_register":
    show_sales_register()
elif page == "resource_register":
    show_resource_register()
elif page == "sales_dashboard":
    show_sales_dashboard()
elif page == "resource_dashboard":
    show_resource_dashboard()
elif page == "admin_dashboard":
    show_admin_dashboard()
else:
    show_home()
