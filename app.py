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

    # -------------------- TAB 1: BOOK CLASS --------------------
    with tab1:
        st.subheader("Book a Class")

        with st.form("booking_form"):
            session_type = st.selectbox(
                "Session Type",
                ["live_class", "product_training", "avrd", "workshop"]
            )

            school_name = st.text_input("School Name")
            school_grade = st.text_input("School Grade")

            subject = ""
            class_standard = ""

            if session_type in ["live_class", "product_training"]:
                subject = st.text_input("Subject")

            if session_type == "live_class":
                class_standard = st.text_input("Class / Standard")

            preferred_date = st.date_input("Preferred Date")
            preferred_time = st.text_input("Preferred Time Slot")
            curriculum = st.text_input("Curriculum")
            book_title = st.text_input("Book Title")
            area = st.text_input("Area / Location")

            submitted = st.form_submit_button("Submit Booking", use_container_width=True)

        if submitted:
            try:
                # sales person brand dynamically nikalna
                brand_res = (
                    supabase.table("sales_profiles")
                    .select("brand_type")
                    .eq("mobile_number", st.session_state.user_mobile)
                    .execute()
                )

                brand_type = "creative_kids"
                if brand_res.data and len(brand_res.data) > 0:
                    brand_type = brand_res.data[0]["brand_type"]

                # duration according to session type
                if session_type == "live_class":
                    duration_minutes = 45
                elif session_type == "product_training":
                    duration_minutes = 45
                elif session_type == "avrd":
                    duration_minutes = 60
                elif session_type == "workshop":
                    duration_minutes = 120
                else:
                    duration_minutes = 45

                booking_data = {
                    "sales_person_number": st.session_state.user_mobile,
                    "resource_person_number": None,
                    "brand_type": brand_type,
                    "session_type": session_type,
                    "duration_minutes": duration_minutes,
                    "school_name": school_name,
                    "school_grade": school_grade,
                    "subject": subject if subject else None,
                    "class_standard": class_standard if class_standard else None,
                    "preferred_date": str(preferred_date),
                    "preferred_time_slot": preferred_time,
                    "curriculum": curriculum,
                    "book_title": book_title,
                    "area_location": area,
                    "status": "pending"
                }

                supabase.table("bookings").insert(booking_data).execute()
                st.success("Class booking request submitted successfully.")

            except Exception as e:
                st.error(f"Booking failed: {e}")

    # -------------------- TAB 2: CLASS STATUS --------------------
    with tab2:
        st.subheader("Class Status")

        try:
            status_res = (
                supabase.table("bookings")
                .select("*")
                .eq("sales_person_number", st.session_state.user_mobile)
                .order("created_at", desc=True)
                .execute()
            )

            if status_res.data:
                for booking in status_res.data:
                    st.markdown("---")
                    st.write(f"**Session Type:** {booking.get('session_type', '')}")
                    st.write(f"**School Name:** {booking.get('school_name', '')}")
                    st.write(f"**Date:** {booking.get('preferred_date', '')}")
                    st.write(f"**Time Slot:** {booking.get('preferred_time_slot', '')}")
                    st.write(f"**Status:** {booking.get('status', '')}")
            else:
                st.info("No class status found.")

        except Exception as e:
            st.error(f"Could not load class status: {e}")

    # -------------------- TAB 3: ALL CLASSES --------------------
    with tab3:
        st.subheader("All Classes")

        try:
            all_res = (
                supabase.table("bookings")
                .select("*")
                .eq("sales_person_number", st.session_state.user_mobile)
                .order("preferred_date", desc=True)
                .execute()
            )

            if all_res.data:
                for booking in all_res.data:
                    st.markdown("---")
                    st.write(f"**Session Type:** {booking.get('session_type', '')}")
                    st.write(f"**School Name:** {booking.get('school_name', '')}")
                    st.write(f"**School Grade:** {booking.get('school_grade', '')}")
                    st.write(f"**Subject:** {booking.get('subject', '')}")
                    st.write(f"**Class / Standard:** {booking.get('class_standard', '')}")
                    st.write(f"**Preferred Date:** {booking.get('preferred_date', '')}")
                    st.write(f"**Preferred Time Slot:** {booking.get('preferred_time_slot', '')}")
                    st.write(f"**Curriculum:** {booking.get('curriculum', '')}")
                    st.write(f"**Book Title:** {booking.get('book_title', '')}")
                    st.write(f"**Area / Location:** {booking.get('area_location', '')}")
                    st.write(f"**Status:** {booking.get('status', '')}")
            else:
                st.info("No classes found.")

        except Exception as e:
            st.error(f"Could not load classes: {e}")

    # -------------------- TAB 4: ADD FEEDBACK --------------------
    with tab4:
        st.subheader("Add Feedback")

        try:
            feedback_booking_res = (
                supabase.table("bookings")
                .select("*")
                .eq("sales_person_number", st.session_state.user_mobile)
                .in_("status", ["completed", "feedback_pending", "closed"])
                .order("preferred_date", desc=True)
                .execute()
            )

            if feedback_booking_res.data:
                booking_options = {
                    f"{b.get('school_name', '')} | {b.get('session_type', '')} | {b.get('preferred_date', '')}": b["id"]
                    for b in feedback_booking_res.data
                }

                selected_booking_label = st.selectbox(
                    "Select Booking",
                    list(booking_options.keys())
                )

                feedback_text = st.text_area("Enter Feedback")

                if st.button("Submit Feedback", use_container_width=True):
                    selected_booking_id = booking_options[selected_booking_label]

                    if not feedback_text.strip():
                        st.error("Please enter feedback.")
                    else:
                        try:
                            feedback_data = {
                                "booking_id": selected_booking_id,
                                "sales_person_number": st.session_state.user_mobile,
                                "feedback_text": feedback_text
                            }

                            supabase.table("feedback_sales").insert(feedback_data).execute()
                            st.success("Feedback submitted successfully.")

                        except Exception as e:
                            st.error(f"Feedback submission failed: {e}")
            else:
                st.info("No completed classes available for feedback.")

        except Exception as e:
            st.error(f"Could not load feedback section: {e}")

    st.markdown("---")
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

    # -------------------- TAB 1: UPCOMING CLASSES --------------------
    with tab1:
        st.subheader("Upcoming Classes")

        try:
            upcoming_res = (
                supabase.table("bookings")
                .select("*")
                .eq("resource_person_number", st.session_state.user_mobile)
                .in_("status", ["approved", "rp_assigned", "zoom_sent"])
                .order("preferred_date", desc=False)
                .execute()
            )

            if upcoming_res.data:
                for booking in upcoming_res.data:
                    st.markdown("---")
                    st.write(f"**Session Type:** {booking.get('session_type', '')}")
                    st.write(f"**School Name:** {booking.get('school_name', '')}")
                    st.write(f"**School Grade:** {booking.get('school_grade', '')}")
                    st.write(f"**Subject:** {booking.get('subject', '')}")
                    st.write(f"**Class / Standard:** {booking.get('class_standard', '')}")
                    st.write(f"**Preferred Date:** {booking.get('preferred_date', '')}")
                    st.write(f"**Preferred Time Slot:** {booking.get('preferred_time_slot', '')}")
                    st.write(f"**Curriculum:** {booking.get('curriculum', '')}")
                    st.write(f"**Book Title:** {booking.get('book_title', '')}")
                    st.write(f"**Area / Location:** {booking.get('area_location', '')}")
                    st.write(f"**Status:** {booking.get('status', '')}")

                    if booking.get("zoom_link"):
                        st.write(f"**Zoom Link:** {booking.get('zoom_link')}")
            else:
                st.info("No upcoming classes found.")

        except Exception as e:
            st.error(f"Could not load upcoming classes: {e}")

    # -------------------- TAB 2: COMPLETED CLASSES --------------------
    with tab2:
        st.subheader("Completed Classes with Sales Feedback")

        try:
            completed_res = (
                supabase.table("bookings")
                .select("*")
                .eq("resource_person_number", st.session_state.user_mobile)
                .in_("status", ["completed", "feedback_pending", "closed"])
                .order("preferred_date", desc=True)
                .execute()
            )

            if completed_res.data:
                for booking in completed_res.data:
                    st.markdown("---")
                    st.write(f"**Session Type:** {booking.get('session_type', '')}")
                    st.write(f"**School Name:** {booking.get('school_name', '')}")
                    st.write(f"**Preferred Date:** {booking.get('preferred_date', '')}")
                    st.write(f"**Preferred Time Slot:** {booking.get('preferred_time_slot', '')}")
                    st.write(f"**Status:** {booking.get('status', '')}")

                    try:
                        sales_feedback_res = (
                            supabase.table("feedback_sales")
                            .select("*")
                            .eq("booking_id", booking["id"])
                            .execute()
                        )

                        if sales_feedback_res.data:
                            for fb in sales_feedback_res.data:
                                st.write(f"**Sales Feedback:** {fb.get('feedback_text', '')}")
                        else:
                            st.write("**Sales Feedback:** Not submitted yet")
                    except Exception as inner_e:
                        st.write(f"**Sales Feedback:** Could not load ({inner_e})")
            else:
                st.info("No completed classes found.")

        except Exception as e:
            st.error(f"Could not load completed classes: {e}")

    # -------------------- TAB 3: AVAILABILITY --------------------
    with tab3:
        st.subheader("Mark Availability / Unavailability")

        with st.form("availability_form"):
            availability_date = st.date_input("Date")
            start_time = st.time_input("Start Time")
            end_time = st.time_input("End Time")
            availability_type = st.selectbox("Type", ["available", "unavailable"])
            notes = st.text_area("Notes")

            availability_submitted = st.form_submit_button("Save Availability", use_container_width=True)

        if availability_submitted:
            try:
                availability_data = {
                    "resource_person_number": st.session_state.user_mobile,
                    "date": str(availability_date),
                    "start_time": str(start_time),
                    "end_time": str(end_time),
                    "type": availability_type,
                    "notes": notes
                }

                supabase.table("resource_availability").insert(availability_data).execute()
                st.success("Availability saved successfully.")
            except Exception as e:
                st.error(f"Could not save availability: {e}")

        st.markdown("### Your Availability Records")

        try:
            availability_res = (
                supabase.table("resource_availability")
                .select("*")
                .eq("resource_person_number", st.session_state.user_mobile)
                .order("date", desc=True)
                .execute()
            )

            if availability_res.data:
                for item in availability_res.data:
                    st.markdown("---")
                    st.write(f"**Date:** {item.get('date', '')}")
                    st.write(f"**Start Time:** {item.get('start_time', '')}")
                    st.write(f"**End Time:** {item.get('end_time', '')}")
                    st.write(f"**Type:** {item.get('type', '')}")
                    st.write(f"**Notes:** {item.get('notes', '')}")
            else:
                st.info("No availability records found.")

        except Exception as e:
            st.error(f"Could not load availability records: {e}")

    # -------------------- TAB 4: ADD REMARK / FEEDBACK --------------------
    with tab4:
        st.subheader("Add Remark / Feedback for Conducted Class")

        try:
            remark_booking_res = (
                supabase.table("bookings")
                .select("*")
                .eq("resource_person_number", st.session_state.user_mobile)
                .in_("status", ["completed", "feedback_pending", "closed"])
                .order("preferred_date", desc=True)
                .execute()
            )

            if remark_booking_res.data:
                booking_options = {
                    f"{b.get('school_name', '')} | {b.get('session_type', '')} | {b.get('preferred_date', '')}": b["id"]
                    for b in remark_booking_res.data
                }

                selected_booking_label = st.selectbox(
                    "Select Booking",
                    list(booking_options.keys())
                )

                feedback_text = st.text_area("Feedback")
                remark_text = st.text_area("Remark")

                if st.button("Submit Remark / Feedback", use_container_width=True):
                    selected_booking_id = booking_options[selected_booking_label]

                    if not feedback_text.strip() and not remark_text.strip():
                        st.error("Please enter feedback or remark.")
                    else:
                        try:
                            feedback_data = {
                                "booking_id": selected_booking_id,
                                "resource_person_number": st.session_state.user_mobile,
                                "feedback_text": feedback_text,
                                "remark_text": remark_text
                            }

                            supabase.table("feedback_resource").insert(feedback_data).execute()
                            st.success("Remark / feedback submitted successfully.")

                        except Exception as e:
                            st.error(f"Submission failed: {e}")
            else:
                st.info("No completed classes available for remarks.")

        except Exception as e:
            st.error(f"Could not load remark section: {e}")

    st.markdown("---")
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

    # -------------------- TAB 1: ALL BOOKINGS --------------------
    with tab1:
        st.subheader("All Class Bookings")

        try:
            bookings_res = (
                supabase.table("bookings")
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )

            if bookings_res.data:
                for booking in bookings_res.data:
                    st.markdown("---")
                    st.write(f"**Booking ID:** {booking.get('id', '')}")
                    st.write(f"**Sales Person Number:** {booking.get('sales_person_number', '')}")
                    st.write(f"**Resource Person Number:** {booking.get('resource_person_number', '')}")
                    st.write(f"**Brand Type:** {booking.get('brand_type', '')}")
                    st.write(f"**Session Type:** {booking.get('session_type', '')}")
                    st.write(f"**School Name:** {booking.get('school_name', '')}")
                    st.write(f"**School Grade:** {booking.get('school_grade', '')}")
                    st.write(f"**Subject:** {booking.get('subject', '')}")
                    st.write(f"**Class / Standard:** {booking.get('class_standard', '')}")
                    st.write(f"**Preferred Date:** {booking.get('preferred_date', '')}")
                    st.write(f"**Preferred Time Slot:** {booking.get('preferred_time_slot', '')}")
                    st.write(f"**Curriculum:** {booking.get('curriculum', '')}")
                    st.write(f"**Book Title:** {booking.get('book_title', '')}")
                    st.write(f"**Area / Location:** {booking.get('area_location', '')}")
                    st.write(f"**Status:** {booking.get('status', '')}")
                    if booking.get("zoom_link"):
                        st.write(f"**Zoom Link:** {booking.get('zoom_link')}")
            else:
                st.info("No bookings found.")

        except Exception as e:
            st.error(f"Could not load bookings: {e}")

    # -------------------- TAB 2: SALES PERSONS MANAGE --------------------
    with tab2:
        st.subheader("Sales Persons Manage")

        try:
            sales_users_res = (
                supabase.table("users")
                .select("*")
                .eq("role", "sales")
                .order("created_at", desc=True)
                .execute()
            )

            if sales_users_res.data:
                for user in sales_users_res.data:
                    st.markdown("---")
                    st.write(f"**Name:** {user.get('name', '')}")
                    st.write(f"**Mobile:** {user.get('mobile_number', '')}")
                    st.write(f"**Email:** {user.get('email', '')}")

                    try:
                        sales_profile_res = (
                            supabase.table("sales_profiles")
                            .select("*")
                            .eq("mobile_number", user.get("mobile_number"))
                            .execute()
                        )

                        if sales_profile_res.data:
                            profile = sales_profile_res.data[0]
                            st.write(f"**Brand Type:** {profile.get('brand_type', '')}")
                            st.write(f"**Area:** {profile.get('area', '')}")
                            st.write(f"**Designation:** {profile.get('designation', '')}")
                    except Exception:
                        pass
            else:
                st.info("No sales persons found.")

        except Exception as e:
            st.error(f"Could not load sales persons: {e}")

    # -------------------- TAB 3: CLASS STATUS / APPROVE / REJECT / ASSIGN --------------------
    with tab3:
        st.subheader("Class Status")

        try:
            pending_res = (
                supabase.table("bookings")
                .select("*")
                .in_("status", ["pending", "approved"])
                .order("created_at", desc=True)
                .execute()
            )

            if pending_res.data:
                resource_res = (
                    supabase.table("resource_profiles")
                    .select("*")
                    .execute()
                )

                resource_options = {}
                if resource_res.data:
                    for rp in resource_res.data:
                        label = (
                            f"{rp.get('mobile_number', '')} | "
                            f"{rp.get('subject_1', '')}, "
                            f"{rp.get('subject_2', '')}, "
                            f"{rp.get('subject_3', '')}"
                        )
                        resource_options[label] = rp.get("mobile_number")

                for booking in pending_res.data:
                    st.markdown("---")
                    st.write(f"**Booking ID:** {booking.get('id', '')}")
                    st.write(f"**Session Type:** {booking.get('session_type', '')}")
                    st.write(f"**School Name:** {booking.get('school_name', '')}")
                    st.write(f"**Subject:** {booking.get('subject', '')}")
                    st.write(f"**Preferred Date:** {booking.get('preferred_date', '')}")
                    st.write(f"**Preferred Time Slot:** {booking.get('preferred_time_slot', '')}")
                    st.write(f"**Current Status:** {booking.get('status', '')}")

                    current_session_type = booking.get("session_type", "")
                    booking_id = booking.get("id")

                    if resource_options:
                        selected_rp_label = st.selectbox(
                            f"Assign Resource Person for booking {booking_id}",
                            options=list(resource_options.keys()),
                            key=f"rp_select_{booking_id}"
                        )
                    else:
                        selected_rp_label = None
                        st.warning("No resource persons found.")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button("Approve", key=f"approve_{booking_id}", use_container_width=True):
                            try:
                                update_data = {
                                    "status": "approved"
                                }

                                # Live class / Product training -> assign from selected RP
                                # AVRD / Workshop -> manual RP allocation bhi yahi selectbox se
                                if selected_rp_label:
                                    update_data["resource_person_number"] = resource_options[selected_rp_label]
                                    update_data["status"] = "rp_assigned"

                                supabase.table("bookings").update(update_data).eq("id", booking_id).execute()
                                st.success(f"Booking {booking_id} approved successfully.")
                                st.rerun()

                            except Exception as e:
                                st.error(f"Approve failed: {e}")

                    with col2:
                        if st.button("Reject", key=f"reject_{booking_id}", use_container_width=True):
                            try:
                                supabase.table("bookings").update({
                                    "status": "rejected"
                                }).eq("id", booking_id).execute()

                                st.success(f"Booking {booking_id} rejected successfully.")
                                st.rerun()

                            except Exception as e:
                                st.error(f"Reject failed: {e}")

                    with col3:
                        if st.button("Assign RP Only", key=f"assign_{booking_id}", use_container_width=True):
                            try:
                                if not selected_rp_label:
                                    st.error("Please select a resource person.")
                                else:
                                    assigned_number = resource_options[selected_rp_label]

                                    supabase.table("bookings").update({
                                        "resource_person_number": assigned_number,
                                        "status": "rp_assigned"
                                    }).eq("id", booking_id).execute()

                                    st.success(f"RP assigned successfully for booking {booking_id}.")
                                    st.rerun()

                            except Exception as e:
                                st.error(f"RP assignment failed: {e}")
            else:
                st.info("No pending or approved bookings found.")

        except Exception as e:
            st.error(f"Could not load class status section: {e}")

    # -------------------- TAB 4: RESOURCE PERSON MANAGE --------------------
    with tab4:
        st.subheader("Resource Person Manage")

        try:
            rp_users_res = (
                supabase.table("users")
                .select("*")
                .eq("role", "resource")
                .order("created_at", desc=True)
                .execute()
            )

            if rp_users_res.data:
                for user in rp_users_res.data:
                    st.markdown("---")
                    st.write(f"**Name:** {user.get('name', '')}")
                    st.write(f"**Mobile:** {user.get('mobile_number', '')}")
                    st.write(f"**Email:** {user.get('email', '')}")

                    try:
                        rp_profile_res = (
                            supabase.table("resource_profiles")
                            .select("*")
                            .eq("mobile_number", user.get("mobile_number"))
                            .execute()
                        )

                        if rp_profile_res.data:
                            profile = rp_profile_res.data[0]
                            st.write(f"**Subject 1:** {profile.get('subject_1', '')}")
                            st.write(f"**Subject 2:** {profile.get('subject_2', '')}")
                            st.write(f"**Subject 3:** {profile.get('subject_3', '')}")
                    except Exception:
                        pass
            else:
                st.info("No resource persons found.")

        except Exception as e:
            st.error(f"Could not load resource persons: {e}")

    # -------------------- TAB 5: FEEDBACK --------------------
    with tab5:
        st.subheader("Feedback")

        st.markdown("### Sales Feedback")
        try:
            sales_feedback_res = (
                supabase.table("feedback_sales")
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )

            if sales_feedback_res.data:
                for fb in sales_feedback_res.data:
                    st.markdown("---")
                    st.write(f"**Booking ID:** {fb.get('booking_id', '')}")
                    st.write(f"**Sales Person Number:** {fb.get('sales_person_number', '')}")
                    st.write(f"**Feedback:** {fb.get('feedback_text', '')}")
                    st.write(f"**Created At:** {fb.get('created_at', '')}")
            else:
                st.info("No sales feedback found.")

        except Exception as e:
            st.error(f"Could not load sales feedback: {e}")

        st.markdown("### Resource Feedback")
        try:
            resource_feedback_res = (
                supabase.table("feedback_resource")
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )

            if resource_feedback_res.data:
                for fb in resource_feedback_res.data:
                    st.markdown("---")
                    st.write(f"**Booking ID:** {fb.get('booking_id', '')}")
                    st.write(f"**Resource Person Number:** {fb.get('resource_person_number', '')}")
                    st.write(f"**Feedback:** {fb.get('feedback_text', '')}")
                    st.write(f"**Remark:** {fb.get('remark_text', '')}")
                    st.write(f"**Created At:** {fb.get('created_at', '')}")
            else:
                st.info("No resource feedback found.")

        except Exception as e:
            st.error(f"Could not load resource feedback: {e}")

    # -------------------- TAB 6: REPORTS --------------------
    with tab6:
        st.subheader("Reports")

        try:
            all_bookings = supabase.table("bookings").select("*").execute()
            sales_feedback = supabase.table("feedback_sales").select("*").execute()
            resource_feedback = supabase.table("feedback_resource").select("*").execute()

            total_bookings = len(all_bookings.data) if all_bookings.data else 0
            pending_count = len([b for b in all_bookings.data if b.get("status") == "pending"]) if all_bookings.data else 0
            approved_count = len([b for b in all_bookings.data if b.get("status") in ["approved", "rp_assigned", "zoom_sent"]]) if all_bookings.data else 0
            completed_count = len([b for b in all_bookings.data if b.get("status") in ["completed", "feedback_pending", "closed"]]) if all_bookings.data else 0
            rejected_count = len([b for b in all_bookings.data if b.get("status") == "rejected"]) if all_bookings.data else 0

            sales_feedback_count = len(sales_feedback.data) if sales_feedback.data else 0
            resource_feedback_count = len(resource_feedback.data) if resource_feedback.data else 0

            st.metric("Total Bookings", total_bookings)
            st.metric("Pending Bookings", pending_count)
            st.metric("Approved / Assigned", approved_count)
            st.metric("Completed Bookings", completed_count)
            st.metric("Rejected Bookings", rejected_count)
            st.metric("Sales Feedback Count", sales_feedback_count)
            st.metric("Resource Feedback Count", resource_feedback_count)

        except Exception as e:
            st.error(f"Could not load reports: {e}")

    st.markdown("---")
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
