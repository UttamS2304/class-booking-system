import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

st.set_page_config(
    page_title="Class Booking System",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def hide_streamlit_chrome():
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        [data-testid="stToolbar"] {
            display: none !important;
        }

        [data-testid="stDecoration"] {
            display: none !important;
        }

        [data-testid="stStatusWidget"] {
            display: none !important;
        }

        [data-testid="stHeader"] {
            display: none !important;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        div.stButton > button {
            border-radius: 10px;
            height: 44px;
            font-weight: 600;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        textarea {
            border-radius: 10px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


hide_streamlit_chrome()

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
def render_footer():
    st.markdown(
        """
        <hr style="margin-top: 2rem; margin-bottom: 1rem;">
        <div style="text-align: center; color: #6b7280; font-size: 14px; padding-bottom: 10px;">
            Designed by Uttam for Cordova Publication Pvt Ltd
        </div>
        """,
        unsafe_allow_html=True
    )


def render_info_card(content: str):
    st.markdown(
        f"""
        <div style="
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 14px 16px;
            margin-bottom: 12px;
            color: #111827;
        ">
            {content}
        </div>
        """,
        unsafe_allow_html=True
    )


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


def get_brand_display_name(brand_type):
    if brand_type == "creative_kids":
        return "Creative Kids"
    elif brand_type == "little_genius":
        return "Little Genius"
    return "Cordova"


def get_session_display_name(session_type):
    session_map = {
        "live_class": "Live Class",
        "product_training": "Product Training",
        "avrd": "AVRD Session",
        "mini_workshop": "Mini Workshop",
        "workshop": "Workshop"
    }
    return session_map.get(session_type, session_type)


def get_duration_minutes(session_type):
    if session_type in ["live_class", "product_training"]:
        return 45
    elif session_type in ["avrd", "mini_workshop"]:
        return 60
    elif session_type == "workshop":
        return 120
    return 45


def get_resource_profile_for_user(user):
    try:
        profile_res = (
            supabase.table("resource_profiles")
            .select("*")
            .eq("user_id", user.get("id"))
            .execute()
        )
        if profile_res.data:
            return profile_res.data[0]
    except Exception:
        pass

    try:
        profile_res = (
            supabase.table("resource_profiles")
            .select("*")
            .eq("mobile_number", user.get("mobile_number"))
            .execute()
        )
        if profile_res.data:
            return profile_res.data[0]
    except Exception:
        pass

    return None


def send_email(to_email, subject, body):
    sender_email = st.secrets["SENDER_EMAIL"]
    sender_password = st.secrets["SENDER_PASSWORD"]

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, to_email, msg.as_string())
    server.quit()


def build_sales_confirmation_email(booking, sales_person_name):
    brand_name = get_brand_display_name(booking.get("brand_type"))
    session_type = get_session_display_name(booking.get("session_type", ""))
    school_name = booking.get("school_name", "")
    grade = booking.get("school_grade", "")
    subject = booking.get("subject", "") or ""
    class_standard = booking.get("class_standard", "") or ""
    topic = booking.get("topic", "") or ""
    date = booking.get("preferred_date", "")
    time_slot = booking.get("preferred_time_slot", "")
    curriculum = booking.get("curriculum", "")
    book_title = booking.get("book_title", "")
    area = booking.get("area_location", "")

    subject_line = f"Your Session is Booked - {brand_name}"

    body = f"""Dear {sales_person_name},

Greetings from {brand_name}!

We are pleased to inform you that your session has been successfully booked. Please find the details below:

Session Details:

Session Type: {session_type}
School Name: {school_name}
Grade: {grade}
Subject: {subject}
Class / Standard: {class_standard}
Topic: {topic}
Date: {date}
Time Slot: {time_slot}
Curriculum: {curriculum}
Book Title: {book_title}
Area: {area}

Kindly review the details and ensure all arrangements are in place from your end.

For any changes or support, please feel free to reach out.

Best regards,
Admin
{brand_name}
"""
    return subject_line, body


def build_resource_assignment_email(booking, resource_person_name):
    brand_name = get_brand_display_name(booking.get("brand_type"))
    session_type = get_session_display_name(booking.get("session_type", ""))
    school_name = booking.get("school_name", "")
    grade = booking.get("school_grade", "")
    subject = booking.get("subject", "") or ""
    class_standard = booking.get("class_standard", "") or ""
    topic = booking.get("topic", "") or ""
    date = booking.get("preferred_date", "")
    time_slot = booking.get("preferred_time_slot", "")
    curriculum = booking.get("curriculum", "")
    book_title = booking.get("book_title", "")
    area = booking.get("area_location", "")

    subject_line = f"New Session Assigned - {brand_name}"

    body = f"""Dear {resource_person_name},

Greetings from {brand_name}!

You have been assigned a session. Please find the details below:

Assigned Session Details:

Session Type: {session_type}
School Name: {school_name}
Grade: {grade}
Subject: {subject}
Class / Standard: {class_standard}
Topic: {topic}
Date: {date}
Time Slot: {time_slot}
Curriculum: {curriculum}
Book Title: {book_title}
Area: {area}

Kindly prepare accordingly and ensure timely availability for the session.

In case of any queries or conflicts, please inform us at the earliest.

Best regards,
Admin
{brand_name}
"""
    return subject_line, body


def build_zoom_link_email(booking, recipient_name, zoom_link):
    brand_name = get_brand_display_name(booking.get("brand_type"))
    session_type = get_session_display_name(booking.get("session_type", ""))
    subject_line = f"Zoom Link for Your Session - {brand_name}"

    body = f"""Dear {recipient_name},

Greetings from {brand_name}!

Please find below the Zoom link for your upcoming session:

Session Type: {session_type}
School Name: {booking.get("school_name", "")}
Topic: {booking.get("topic", "") or ""}
Date: {booking.get("preferred_date", "")}
Time Slot: {booking.get("preferred_time_slot", "")}

Zoom Link:
{zoom_link}

Please be available on time.

Best regards,
Admin
{brand_name}
"""
    return subject_line, body


def show_home():
    st.markdown(
        """
        <style>
        .home-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 0.4rem;
        }

        .home-subtitle {
            font-size: 1rem;
            color: #cbd5e1;
            margin-bottom: 1.8rem;
        }

        .home-card {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 18px;
            padding: 1.4rem 1.2rem;
            min-height: 145px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.20);
            margin-bottom: 0.8rem;
        }

        .home-card-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.55rem;
        }

        .home-card-text {
            font-size: 0.98rem;
            color: #e5e7eb;
            line-height: 1.5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="home-title">Class Booking System</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="home-subtitle">Welcome to the class booking platform.</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            """
            <div class="home-card">
                <div class="home-card-title">Login</div>
                <div class="home-card-text">
                    Already registered? Login here to access your dashboard and manage class bookings.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Go to Login", use_container_width=True, key="home_login"):
            go_to("login")

    with col2:
        st.markdown(
            """
            <div class="home-card">
                <div class="home-card-title">Register</div>
                <div class="home-card-text">
                    New user? Create an account to start using the class booking system.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Go to Register", use_container_width=True, key="home_register"):
            go_to("register")

    render_footer()


def show_register_choice():
    st.title("Registration")
    st.write("Choose your role to continue.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sales Person")
        st.write("Register as a sales person for Creative Kids or Little Genius.")
        if st.button("Register as Sales Person", use_container_width=True, key="register_sales"):
            go_to("sales_register")

    with col2:
        st.subheader("Resource Person")
        st.write("Register as a resource person and select your subjects.")
        if st.button("Register as Resource Person", use_container_width=True, key="register_resource"):
            go_to("resource_register")

    st.markdown("---")
    if st.button("Back to Home", use_container_width=True, key="register_back_home"):
        go_to("home")

    render_footer()


def show_login():
    st.title("Login")
    st.write("Login using your email address or mobile number.")
    st.markdown("---")

    identifier = st.text_input("Email or Mobile Number")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login", use_container_width=True, key="login_button"):
            if not identifier.strip() or not password.strip():
                st.error("Please enter your email/mobile number and password.")
                st.stop()

            try:
                result = (
                    supabase.table("users")
                    .select("*")
                    .or_(f"email.eq.{identifier.strip()},mobile_number.eq.{identifier.strip()}")
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
        if st.button("Back to Home", use_container_width=True, key="login_back_home"):
            go_to("home")

    render_footer()


def show_sales_register():
    st.title("Sales Person Registration")
    st.write("Please complete the form below to register as a sales person.")
    st.markdown("---")

    brand_options = {
        "Creative Kids": "creative_kids",
        "Little Genius": "little_genius"
    }

    with st.form("sales_registration_form"):
        selected_brand_label = st.selectbox(
            "Select Brand",
            list(brand_options.keys())
        )
        brand = brand_options[selected_brand_label]

        name = st.text_input("Full Name")
        mobile = st.text_input("Mobile Number")
        email = st.text_input("Email Address")
        area = st.text_input("Area")
        designation = st.text_input("Designation")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Register", use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Register", use_container_width=True, key="sales_reg_back_register"):
            go_to("register")
    with col2:
        if st.button("Back to Home", use_container_width=True, key="sales_reg_back_home"):
            go_to("home")

    if submitted:
        if not name.strip() or not mobile.strip() or not email.strip() or not area.strip() or not designation.strip() or not password.strip():
            st.error("Please fill all fields.")
            st.stop()

        try:
            existing_user = (
                supabase.table("users")
                .select("id")
                .or_(f"email.eq.{email.strip()},mobile_number.eq.{mobile.strip()}")
                .execute()
            )

            if existing_user.data:
                st.error("A user with the same email or mobile number already exists.")
                st.stop()

            user_data = {
                "name": name.strip(),
                "mobile_number": mobile.strip(),
                "email": email.strip(),
                "role": "sales",
                "password": password,
                "created_at": datetime.utcnow().isoformat()
            }

            user_res = supabase.table("users").insert(user_data).execute()

            if not user_res.data:
                st.error("Unable to create user.")
                st.stop()

            user_id = user_res.data[0]["id"]

            sales_data = {
                "user_id": user_id,
                "name": name.strip(),
                "mobile_number": mobile.strip(),
                "brand_type": brand,
                "area": area.strip(),
                "designation": designation.strip()
            }

            supabase.table("sales_profiles").insert(sales_data).execute()
            st.success("Sales person registered successfully.")
            st.info("You can now login using your email or mobile number.")

        except Exception as e:
            st.error(f"Registration failed: {e}")

    render_footer()


def show_resource_register():
    st.title("Resource Person Registration")
    st.write("Please complete the form below to register as a resource person.")
    st.markdown("---")

    subject_options = [
        "Mathematics",
        "Hindi",
        "English",
        "Hindi Vyakaran",
        "English Grammar",
        "Science",
        "Social Science",
        "Computer",
        "General Knowledge",
        "Pre Primary",
        "Pre Primary Hindi",
        "Environment Science"
    ]

    with st.form("resource_registration_form"):
        name = st.text_input("Full Name")
        mobile = st.text_input("Mobile Number")
        email = st.text_input("Email Address")

        subject_1 = st.selectbox("Subject 1 *", ["Select Subject"] + subject_options)

        subject_2_options = ["None"] + [s for s in subject_options if s != subject_1]
        subject_2 = st.selectbox("Subject 2 (Optional)", subject_2_options)

        subject_3_options = ["None"] + [
            s for s in subject_options if s not in [subject_1, subject_2]
        ]
        subject_3 = st.selectbox("Subject 3 (Optional)", subject_3_options)

        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Register", use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Register", use_container_width=True, key="resource_reg_back_register"):
            go_to("register")
    with col2:
        if st.button("Back to Home", use_container_width=True, key="resource_reg_back_home"):
            go_to("home")

    if submitted:
        if not name.strip() or not mobile.strip() or not email.strip() or not password.strip():
            st.error("Please fill all required fields.")
            st.stop()

        if subject_1 == "Select Subject":
            st.error("Subject 1 is required.")
            st.stop()

        try:
            existing_user = (
                supabase.table("users")
                .select("id")
                .or_(f"email.eq.{email.strip()},mobile_number.eq.{mobile.strip()}")
                .execute()
            )

            if existing_user.data:
                st.error("A user with the same email or mobile number already exists.")
                st.stop()

            user_data = {
                "name": name.strip(),
                "mobile_number": mobile.strip(),
                "email": email.strip(),
                "role": "resource",
                "password": password,
                "created_at": datetime.utcnow().isoformat()
            }

            user_res = supabase.table("users").insert(user_data).execute()

            if not user_res.data:
                st.error("Unable to create user.")
                st.stop()

            user_id = user_res.data[0]["id"]

            resource_data = {
                "user_id": user_id,
                "name": name.strip(),
                "mobile_number": mobile.strip(),
                "subject_1": subject_1,
                "subject_2": None if subject_2 == "None" else subject_2,
                "subject_3": None if subject_3 == "None" else subject_3
            }

            supabase.table("resource_profiles").insert(resource_data).execute()
            st.success("Resource person registered successfully.")
            st.info("You can now login using your email or mobile number.")

        except Exception as e:
            st.error(f"Registration failed: {e}")

    render_footer()


def get_time_slots(session_type):
    if session_type in ["live_class", "product_training"]:
        return [
            "09:45 AM - 10:30 AM",
            "10:30 AM - 11:15 AM",
            "11:15 AM - 12:00 PM",
            "12:00 PM - 12:45 PM",
            "12:45 PM - 01:30 PM",
            "01:30 PM - 02:15 PM",
            "02:15 AM - 03:00 PM",
            "03:00 PM - 03:45 PM"
        ]
    elif session_type in ["avrd", "mini_workshop"]:
        return [
            "09:45 AM - 10:45 AM",
            "10:45 AM - 11:45 AM",
            "11:45 AM - 12:45 PM",
            "12:45 PM - 01:45 PM",
            "01:45 PM - 02:45 PM",
            "02:45 PM - 03:45 PM"
        ]
    elif session_type == "workshop":
        return [
            "09:45 AM - 11:45 AM",
            "11:45 AM - 01:45 PM",
            "01:45 PM - 03:45 PM"
        ]
    return []


def is_rp_slot_conflicting(resource_person_number, preferred_date, preferred_time_slot):
    try:
        res = (
            supabase.table("bookings")
            .select("*")
            .eq("resource_person_number", resource_person_number)
            .eq("preferred_date", str(preferred_date))
            .in_("status", ["approved", "rp_assigned", "zoom_sent", "completed", "feedback_pending", "closed"])
            .execute()
        )

        if not res.data:
            return False

        for booking in res.data:
            if booking.get("preferred_time_slot") == preferred_time_slot:
                return True

        return False

    except Exception:
        return True


def is_rp_unavailable(resource_person_number, preferred_date):
    try:
        availability_res = (
            supabase.table("resource_availability")
            .select("*")
            .eq("resource_person_number", resource_person_number)
            .eq("date", str(preferred_date))
            .execute()
        )

        if not availability_res.data:
            return False

        for av in availability_res.data:
            if av.get("type") == "unavailable":
                return True

        return False

    except Exception:
        return True


def get_available_rps_for_booking(booking):
    try:
        preferred_date = str(booking.get("preferred_date"))
        preferred_time_slot = booking.get("preferred_time_slot")

        rp_res = supabase.table("resource_profiles").select("*").execute()
        if not rp_res.data:
            return {}

        available_rps = {}

        for rp in rp_res.data:
            rp_number = rp.get("mobile_number")
            subject_1 = rp.get("subject_1")
            subject_2 = rp.get("subject_2")
            subject_3 = rp.get("subject_3")

            if is_rp_unavailable(rp_number, preferred_date):
                continue

            if is_rp_slot_conflicting(rp_number, preferred_date, preferred_time_slot):
                continue

            label = f"{rp_number} | {subject_1 or '-'} | {subject_2 or '-'} | {subject_3 or '-'}"
            available_rps[label] = rp_number

        return available_rps

    except Exception:
        return {}


def auto_assign_rp_for_subject_booking(booking):
    try:
        booking_subject = booking.get("subject")
        preferred_date = str(booking.get("preferred_date"))
        preferred_time_slot = booking.get("preferred_time_slot")

        rp_res = supabase.table("resource_profiles").select("*").execute()
        if not rp_res.data:
            return None

        primary_matches = []
        secondary_matches = []

        for rp in rp_res.data:
            rp_number = rp.get("mobile_number")
            subject_1 = rp.get("subject_1")
            subject_2 = rp.get("subject_2")
            subject_3 = rp.get("subject_3")

            if is_rp_unavailable(rp_number, preferred_date):
                continue

            if is_rp_slot_conflicting(rp_number, preferred_date, preferred_time_slot):
                continue

            if booking_subject == subject_1:
                primary_matches.append(rp_number)
            elif booking_subject in [subject_2, subject_3]:
                secondary_matches.append(rp_number)

        if primary_matches:
            return primary_matches[0]

        if secondary_matches:
            return secondary_matches[0]

        return None

    except Exception:
        return None


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

    session_display_map = {
        "live_class": "Live Class",
        "product_training": "Product Training",
        "avrd": "AVRD Session",
        "mini_workshop": "Mini Workshop",
        "workshop": "Workshop"
    }

    status_display_map = {
        "pending": "Pending",
        "approved": "Approved",
        "rp_assigned": "Resource Assigned",
        "zoom_sent": "Zoom Link Sent",
        "completed": "Completed",
        "feedback_pending": "Feedback Pending",
        "closed": "Closed",
        "rejected": "Rejected"
    }

    with tab1:
        st.subheader("Book a Class")

        subject_options = [
            "Mathematics",
            "Hindi",
            "English",
            "Hindi Vyakaran",
            "English Grammar",
            "Science",
            "Social Science",
            "Computer",
            "General Knowledge",
            "Pre Primary",
            "Pre Primary Hindi",
            "Environment Science"
        ]

        session_options = {
            "Live Class (45 mins) [Temporarily Closed]": "live_class",
            "Product Training (45 mins)": "product_training",
            "AVRD Session (1 hour)": "avrd",
            "Mini Workshop (1 hour)": "mini_workshop",
            "Workshop (2 hours)": "workshop"
        }

        min_booking_date = datetime.today().date() + timedelta(days=1)

        selected_session_label = st.selectbox(
            "Select Session Type",
            list(session_options.keys()),
            key="sales_session_type"
        )
        session_type = session_options[selected_session_label]

        if session_type == "live_class":
            render_info_card(
                "<strong>Notice:</strong> We are not conducting Live Classes right now. "
                "Please choose another session type."
            )

        time_slot_options = get_time_slots(session_type)

        with st.form("booking_form"):
            school_name = st.text_input("Name of School")
            school_grade = st.text_input("School Grade")

            subject = ""
            class_standard = ""
            topic = ""

            if session_type in ["product_training"]:
                subject = st.selectbox("Subject", ["Select Subject"] + subject_options)

            if session_type == "live_class":
                class_standard = st.text_input("Class / Standard")

            if session_type in ["product_training", "mini_workshop", "workshop"]:
                topic = st.text_input("Topic of the Session *")

            preferred_date = st.date_input(
                "Preferred Date",
                min_value=min_booking_date
            )

            preferred_time = st.selectbox(
                "Preferred Time Slot",
                ["Select Time Slot"] + time_slot_options
            )

            curriculum = st.text_input("Curriculum")
            book_title = st.text_input("Title of Book(s) Used")
            area = st.text_input("Area / Location")

            submitted = st.form_submit_button("Submit Booking", use_container_width=True)

        if submitted:
            if session_type == "live_class":
                st.error("We are not conducting Live Classes right now.")
                st.stop()

            if not school_name.strip():
                st.error("Please enter school name.")
                st.stop()

            if not school_grade.strip():
                st.error("Please enter school grade.")
                st.stop()

            if session_type in ["product_training"] and subject == "Select Subject":
                st.error("Please select a subject.")
                st.stop()

            if session_type in ["product_training", "mini_workshop", "workshop"] and not topic.strip():
                st.error("Please enter topic.")
                st.stop()

            if preferred_date <= datetime.today().date():
                st.error("Booking can only be made at least one day in advance.")
                st.stop()

            if preferred_time == "Select Time Slot":
                st.error("Please select a preferred time slot.")
                st.stop()

            if not curriculum.strip():
                st.error("Please enter curriculum.")
                st.stop()

            if not book_title.strip():
                st.error("Please enter book title.")
                st.stop()

            if not area.strip():
                st.error("Please enter area / location.")
                st.stop()

            try:
                brand_res = (
                    supabase.table("sales_profiles")
                    .select("brand_type")
                    .eq("mobile_number", st.session_state.user_mobile)
                    .execute()
                )

                brand_type = "creative_kids"
                if brand_res.data and len(brand_res.data) > 0:
                    brand_type = brand_res.data[0]["brand_type"]

                booking_data = {
                    "sales_person_number": st.session_state.user_mobile,
                    "resource_person_number": None,
                    "brand_type": brand_type,
                    "session_type": session_type,
                    "duration_minutes": get_duration_minutes(session_type),
                    "school_name": school_name.strip(),
                    "school_grade": school_grade.strip(),
                    "subject": subject if session_type in ["product_training"] else None,
                    "class_standard": class_standard.strip() if session_type == "live_class" else None,
                    "topic": topic.strip() if topic else None,
                    "preferred_date": str(preferred_date),
                    "preferred_time_slot": preferred_time,
                    "curriculum": curriculum.strip(),
                    "book_title": book_title.strip(),
                    "area_location": area.strip(),
                    "status": "pending"
                }

                supabase.table("bookings").insert(booking_data).execute()
                st.success("Class booking request submitted successfully.")
                st.rerun()

            except Exception as e:
                st.error(f"Booking failed: {e}")

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
                table_data = []

                for booking in status_res.data:
                    table_data.append({
                        "Session Type": session_display_map.get(
                            booking.get("session_type"),
                            booking.get("session_type", "")
                        ),
                        "School Name": booking.get("school_name", ""),
                        "Preferred Date": booking.get("preferred_date", ""),
                        "Preferred Time Slot": booking.get("preferred_time_slot", ""),
                        "Status": status_display_map.get(
                            booking.get("status"),
                            booking.get("status", "")
                        )
                    })

                st.dataframe(table_data, use_container_width=True, hide_index=True)
            else:
                st.info("No class status found.")

        except Exception as e:
            st.error(f"Could not load class status: {e}")

    with tab3:
        st.subheader("All Booked Classes")

        try:
            all_res = (
                supabase.table("bookings")
                .select("*")
                .eq("sales_person_number", st.session_state.user_mobile)
                .order("preferred_date", desc=True)
                .execute()
            )

            if all_res.data:
                table_data = []

                for booking in all_res.data:
                    table_data.append({
                        "Session Type": session_display_map.get(
                            booking.get("session_type"),
                            booking.get("session_type", "")
                        ),
                        "School Name": booking.get("school_name", ""),
                        "School Grade": booking.get("school_grade", ""),
                        "Subject": booking.get("subject", ""),
                        "Class / Standard": booking.get("class_standard", ""),
                        "Topic": booking.get("topic", ""),
                        "Preferred Date": booking.get("preferred_date", ""),
                        "Preferred Time Slot": booking.get("preferred_time_slot", ""),
                        "Curriculum": booking.get("curriculum", ""),
                        "Book Title": booking.get("book_title", ""),
                        "Area / Location": booking.get("area_location", ""),
                        "Status": status_display_map.get(
                            booking.get("status"),
                            booking.get("status", "")
                        )
                    })

                st.dataframe(table_data, use_container_width=True, hide_index=True)
            else:
                st.info("No classes found.")

        except Exception as e:
            st.error(f"Could not load classes: {e}")

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
                    f"{b.get('school_name', '')} | {b.get('preferred_date', '')} | {b.get('preferred_time_slot', '')}": b["id"]
                    for b in feedback_booking_res.data
                }

                selected_booking_label = st.selectbox(
                    "Select Booking",
                    list(booking_options.keys())
                )

                rating_options = {
                    "⭐ 1": 1,
                    "⭐⭐ 2": 2,
                    "⭐⭐⭐ 3": 3,
                    "⭐⭐⭐⭐ 4": 4,
                    "⭐⭐⭐⭐⭐ 5": 5
                }

                selected_rating_label = st.selectbox(
                    "Rating of the Session",
                    list(rating_options.keys())
                )
                session_rating = rating_options[selected_rating_label]

                feedback_text = st.text_area("Comments (Optional)")

                if st.button("Submit Feedback", use_container_width=True, key="sales_feedback_submit"):
                    selected_booking_id = booking_options[selected_booking_label]

                    try:
                        existing_feedback_res = (
                            supabase.table("feedback_sales")
                            .select("*")
                            .eq("booking_id", selected_booking_id)
                            .eq("sales_person_number", st.session_state.user_mobile)
                            .execute()
                        )

                        if existing_feedback_res.data:
                            st.error("Feedback for this booking has already been submitted.")
                            st.stop()

                        feedback_data = {
                            "booking_id": selected_booking_id,
                            "sales_person_number": st.session_state.user_mobile,
                            "session_rating": session_rating,
                            "feedback_text": feedback_text.strip() if feedback_text.strip() else None
                        }

                        supabase.table("feedback_sales").insert(feedback_data).execute()
                        st.success("Feedback submitted successfully.")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Feedback submission failed: {e}")
            else:
                st.info("No completed classes available for feedback.")

        except Exception as e:
            st.error(f"Could not load feedback section: {e}")

    st.markdown("---")
    if st.button("Logout", use_container_width=True, key="sales_logout"):
        logout()

    render_footer()


def show_resource_dashboard():
    st.title("Resource Dashboard")
    st.write(f"Welcome, {st.session_state.user_name}")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Upcoming Classes",
        "Completed Classes",
        "Availability",
        "Add Remark / Feedback"
    ])

    session_display_map = {
        "live_class": "Live Class",
        "product_training": "Product Training",
        "avrd": "AVRD Session",
        "mini_workshop": "Mini Workshop",
        "workshop": "Workshop"
    }

    status_display_map = {
        "pending": "Pending",
        "approved": "Approved",
        "rp_assigned": "Resource Assigned",
        "zoom_sent": "Zoom Link Sent",
        "completed": "Completed",
        "feedback_pending": "Feedback Pending",
        "closed": "Closed",
        "rejected": "Rejected"
    }

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
                table_data = []
                for booking in upcoming_res.data:
                    table_data.append({
                        "Session Type": session_display_map.get(
                            booking.get("session_type"),
                            booking.get("session_type", "")
                        ),
                        "School Name": booking.get("school_name", ""),
                        "School Grade": booking.get("school_grade", ""),
                        "Subject": booking.get("subject", ""),
                        "Class / Standard": booking.get("class_standard", ""),
                        "Topic": booking.get("topic", ""),
                        "Preferred Date": booking.get("preferred_date", ""),
                        "Preferred Time Slot": booking.get("preferred_time_slot", ""),
                        "Curriculum": booking.get("curriculum", ""),
                        "Book Title": booking.get("book_title", ""),
                        "Area / Location": booking.get("area_location", ""),
                        "Status": status_display_map.get(
                            booking.get("status"),
                            booking.get("status", "")
                        ),
                        "Zoom Link": booking.get("zoom_link", "")
                    })

                st.dataframe(table_data, use_container_width=True, hide_index=True)
            else:
                st.info("No upcoming classes found.")

        except Exception as e:
            st.error(f"Could not load upcoming classes: {e}")

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
                table_data = []

                for booking in completed_res.data:
                    sales_rating = ""
                    sales_feedback = ""

                    try:
                        sales_feedback_res = (
                            supabase.table("feedback_sales")
                            .select("*")
                            .eq("booking_id", booking["id"])
                            .execute()
                        )

                        if sales_feedback_res.data:
                            sales_fb = sales_feedback_res.data[0]
                            sales_rating = sales_fb.get("session_rating", "")
                            sales_feedback = sales_fb.get("feedback_text", "")
                    except Exception:
                        pass

                    table_data.append({
                        "Session Type": session_display_map.get(
                            booking.get("session_type"),
                            booking.get("session_type", "")
                        ),
                        "School Name": booking.get("school_name", ""),
                        "Topic": booking.get("topic", ""),
                        "Preferred Date": booking.get("preferred_date", ""),
                        "Preferred Time Slot": booking.get("preferred_time_slot", ""),
                        "Status": status_display_map.get(
                            booking.get("status"),
                            booking.get("status", "")
                        ),
                        "Sales Rating": sales_rating,
                        "Sales Feedback": sales_feedback
                    })

                st.dataframe(table_data, use_container_width=True, hide_index=True)
            else:
                st.info("No completed classes found.")

        except Exception as e:
            st.error(f"Could not load completed classes: {e}")

    with tab3:
        st.subheader("Availability Management")

        with st.form("availability_form"):
            availability_date = st.date_input("Date")
            start_time = st.time_input("Start Time")
            end_time = st.time_input("End Time")
            availability_type = st.selectbox(
                "Availability Type",
                ["available", "unavailable"]
            )
            notes = st.text_area("Notes (Optional)")

            availability_submitted = st.form_submit_button(
                "Save Availability",
                use_container_width=True
            )

        if availability_submitted:
            try:
                availability_data = {
                    "resource_person_number": st.session_state.user_mobile,
                    "date": str(availability_date),
                    "start_time": str(start_time),
                    "end_time": str(end_time),
                    "type": availability_type,
                    "notes": notes.strip() if notes.strip() else None
                }

                supabase.table("resource_availability").insert(availability_data).execute()
                st.success("Availability saved successfully.")
                st.rerun()

            except Exception as e:
                st.error(f"Could not save availability: {e}")

        st.markdown("### Availability Records")

        try:
            availability_res = (
                supabase.table("resource_availability")
                .select("*")
                .eq("resource_person_number", st.session_state.user_mobile)
                .order("date", desc=True)
                .execute()
            )

            if availability_res.data:
                availability_table = []
                for item in availability_res.data:
                    availability_table.append({
                        "Date": item.get("date", ""),
                        "Start Time": item.get("start_time", ""),
                        "End Time": item.get("end_time", ""),
                        "Type": item.get("type", ""),
                        "Notes": item.get("notes", "")
                    })

                st.dataframe(availability_table, use_container_width=True, hide_index=True)
            else:
                st.info("No availability records found.")

        except Exception as e:
            st.error(f"Could not load availability records: {e}")

    with tab4:
        st.subheader("Add Remark / Feedback")

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
                    f"{b.get('school_name', '')} | {b.get('preferred_date', '')} | {b.get('preferred_time_slot', '')}": b["id"]
                    for b in remark_booking_res.data
                }

                selected_booking_label = st.selectbox(
                    "Select Booking",
                    list(booking_options.keys())
                )

                rating_options = {
                    "⭐ 1": 1,
                    "⭐⭐ 2": 2,
                    "⭐⭐⭐ 3": 3,
                    "⭐⭐⭐⭐ 4": 4,
                    "⭐⭐⭐⭐⭐ 5": 5
                }

                selected_rating_label = st.selectbox(
                    "Rating of the Session",
                    list(rating_options.keys())
                )
                session_rating = rating_options[selected_rating_label]

                feedback_text = st.text_area("Feedback (Optional)")
                remark_text = st.text_area("Remark (Optional)")

                if st.button("Submit Remark / Feedback", use_container_width=True, key="resource_feedback_submit"):
                    selected_booking_id = booking_options[selected_booking_label]

                    try:
                        existing_feedback_res = (
                            supabase.table("feedback_resource")
                            .select("*")
                            .eq("booking_id", selected_booking_id)
                            .eq("resource_person_number", st.session_state.user_mobile)
                            .execute()
                        )

                        if existing_feedback_res.data:
                            st.error("Feedback for this booking has already been submitted.")
                            st.stop()

                        feedback_data = {
                            "booking_id": selected_booking_id,
                            "resource_person_number": st.session_state.user_mobile,
                            "session_rating": session_rating,
                            "feedback_text": feedback_text.strip() if feedback_text.strip() else None,
                            "remark_text": remark_text.strip() if remark_text.strip() else None
                        }

                        supabase.table("feedback_resource").insert(feedback_data).execute()
                        st.success("Remark / feedback submitted successfully.")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Submission failed: {e}")
            else:
                st.info("No completed classes available for remarks.")

        except Exception as e:
            st.error(f"Could not load remark section: {e}")

    st.markdown("---")
    if st.button("Logout", use_container_width=True, key="resource_logout"):
        logout()

    render_footer()


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

    session_display_map = {
        "live_class": "Live Class",
        "product_training": "Product Training",
        "avrd": "AVRD Session",
        "mini_workshop": "Mini Workshop",
        "workshop": "Workshop"
    }

    status_display_map = {
        "pending": "Pending",
        "approved": "Approved",
        "rp_assigned": "Resource Assigned",
        "zoom_sent": "Zoom Link Sent",
        "completed": "Completed",
        "feedback_pending": "Feedback Pending",
        "closed": "Closed",
        "rejected": "Rejected"
    }

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
                table_data = []
                for booking in bookings_res.data:
                    table_data.append({
                        "Booking ID": booking.get("id", ""),
                        "Sales Person": booking.get("sales_person_number", ""),
                        "Resource Person": booking.get("resource_person_number", ""),
                        "Brand": get_brand_display_name(booking.get("brand_type", "")),
                        "Session Type": session_display_map.get(
                            booking.get("session_type"),
                            booking.get("session_type", "")
                        ),
                        "School Name": booking.get("school_name", ""),
                        "Topic": booking.get("topic", ""),
                        "Preferred Date": booking.get("preferred_date", ""),
                        "Preferred Time Slot": booking.get("preferred_time_slot", ""),
                        "Status": status_display_map.get(
                            booking.get("status"),
                            booking.get("status", "")
                        ),
                        "Zoom Link": booking.get("zoom_link", "")
                    })

                st.dataframe(table_data, use_container_width=True, hide_index=True)

                st.markdown("### Booking Actions")

                booking_map = {
                    f"{get_brand_display_name(b.get('brand_type', ''))} | {b.get('school_name', '')} | {b.get('preferred_date', '')} | {b.get('preferred_time_slot', '')}": b
                    for b in bookings_res.data
                }

                selected_booking_label = st.selectbox(
                    "Select Booking",
                    list(booking_map.keys()),
                    key="admin_tab1_selected_booking"
                )

                selected_booking = booking_map[selected_booking_label]
                booking_id = selected_booking.get("id")
                current_status = selected_booking.get("status", "")

                st.write(
                    f"**Current Status:** {status_display_map.get(current_status, current_status)}"
                )

                zoom_link_value = st.text_input(
                    "Zoom Link",
                    value=selected_booking.get("zoom_link", "") if selected_booking.get("zoom_link") else "",
                    key="admin_tab1_zoom_link"
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Send Zoom Link", use_container_width=True, key="admin_send_zoom"):
                        try:
                            if not zoom_link_value.strip():
                                st.error("Please enter Zoom link.")
                                st.stop()

                            supabase.table("bookings").update({
                                "zoom_link": zoom_link_value.strip(),
                                "status": "zoom_sent"
                            }).eq("id", booking_id).execute()

                            sales_user_res = (
                                supabase.table("users")
                                .select("*")
                                .eq("mobile_number", selected_booking["sales_person_number"])
                                .execute()
                            )

                            if sales_user_res.data:
                                sales_user = sales_user_res.data[0]
                                subject_line, body = build_zoom_link_email(
                                    selected_booking,
                                    sales_user.get("name", "Sales Person"),
                                    zoom_link_value.strip()
                                )
                                send_email(sales_user["email"], subject_line, body)

                            if selected_booking.get("resource_person_number"):
                                rp_user_res = (
                                    supabase.table("users")
                                    .select("*")
                                    .eq("mobile_number", selected_booking["resource_person_number"])
                                    .execute()
                                )

                                if rp_user_res.data:
                                    rp_user = rp_user_res.data[0]
                                    subject_line, body = build_zoom_link_email(
                                        selected_booking,
                                        rp_user.get("name", "Resource Person"),
                                        zoom_link_value.strip()
                                    )
                                    send_email(rp_user["email"], subject_line, body)

                            st.success("Zoom link sent successfully.")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Zoom mail failed: {e}")

                with col2:
                    if st.button("Mark as Completed", use_container_width=True, key="admin_mark_completed"):
                        try:
                            if current_status not in ["approved", "rp_assigned", "zoom_sent"]:
                                st.error("Only approved, assigned, or zoom-sent classes can be marked as completed.")
                                st.stop()

                            supabase.table("bookings").update({
                                "status": "completed"
                            }).eq("id", booking_id).execute()

                            st.success("Class marked as completed successfully.")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Could not mark class as completed: {e}")

            else:
                st.info("No bookings found.")

        except Exception as e:
            st.error(f"Could not load bookings: {e}")

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
                sales_table = []

                for user in sales_users_res.data:
                    brand_type = ""
                    area = ""
                    designation = ""

                    try:
                        sales_profile_res = (
                            supabase.table("sales_profiles")
                            .select("*")
                            .eq("mobile_number", user.get("mobile_number"))
                            .execute()
                        )

                        if sales_profile_res.data:
                            profile = sales_profile_res.data[0]
                            brand_type = get_brand_display_name(profile.get("brand_type", ""))
                            area = profile.get("area", "")
                            designation = profile.get("designation", "")
                    except Exception:
                        pass

                    sales_table.append({
                        "Name": user.get("name", ""),
                        "Mobile": user.get("mobile_number", ""),
                        "Email": user.get("email", ""),
                        "Brand": brand_type,
                        "Area": area,
                        "Designation": designation
                    })

                st.dataframe(sales_table, use_container_width=True, hide_index=True)
            else:
                st.info("No sales persons found.")

        except Exception as e:
            st.error(f"Could not load sales persons: {e}")

    with tab3:
        st.subheader("Class Status Management")

        try:
            pending_res = (
                supabase.table("bookings")
                .select("*")
                .in_("status", ["pending", "approved"])
                .order("created_at", desc=True)
                .execute()
            )

            if pending_res.data:
                table_data = []
                for booking in pending_res.data:
                    table_data.append({
                        "Booking ID": booking.get("id", ""),
                        "Session Type": session_display_map.get(
                            booking.get("session_type"),
                            booking.get("session_type", "")
                        ),
                        "School Name": booking.get("school_name", ""),
                        "Subject": booking.get("subject", ""),
                        "Topic": booking.get("topic", ""),
                        "Preferred Date": booking.get("preferred_date", ""),
                        "Preferred Time Slot": booking.get("preferred_time_slot", ""),
                        "Current Status": status_display_map.get(
                            booking.get("status"),
                            booking.get("status", "")
                        )
                    })

                st.dataframe(table_data, use_container_width=True, hide_index=True)

                st.markdown("### Update Booking Status")

                booking_map = {
                    f"{b.get('school_name', '')} | {b.get('preferred_date', '')} | {b.get('preferred_time_slot', '')}": b
                    for b in pending_res.data
                }

                selected_booking_label = st.selectbox(
                    "Select Booking to Manage",
                    list(booking_map.keys()),
                    key="admin_tab3_selected_booking"
                )

                selected_booking = booking_map[selected_booking_label]
                booking_id = selected_booking.get("id")
                session_type = selected_booking.get("session_type", "")

                selected_rp_label = None
                available_rp_options = {}

                if session_type in ["avrd", "mini_workshop", "workshop"]:
                    available_rp_options = get_available_rps_for_booking(selected_booking)

                    if available_rp_options:
                        selected_rp_label = st.selectbox(
                            "Select Available Resource Person",
                            list(available_rp_options.keys()),
                            key="admin_tab3_selected_rp"
                        )
                    else:
                        st.warning("No resource person is available for this date and time slot.")

                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("Approve", use_container_width=True, key="admin_approve_booking"):
                        try:
                            if session_type in ["live_class"]:
                                st.error("Live Class is currently disabled.")
                                st.stop()

                            if session_type in ["product_training"]:
                                assigned_number = auto_assign_rp_for_subject_booking(selected_booking)

                                if not assigned_number:
                                    st.error("No eligible resource person is available for this subject, date, and time slot.")
                                    st.stop()

                                supabase.table("bookings").update({
                                    "status": "rp_assigned",
                                    "resource_person_number": assigned_number
                                }).eq("id", booking_id).execute()

                                updated_booking_res = (
                                    supabase.table("bookings")
                                    .select("*")
                                    .eq("id", booking_id)
                                    .execute()
                                )

                                if updated_booking_res.data:
                                    updated_booking = updated_booking_res.data[0]

                                    sales_user_res = (
                                        supabase.table("users")
                                        .select("*")
                                        .eq("mobile_number", updated_booking["sales_person_number"])
                                        .execute()
                                    )

                                    if sales_user_res.data:
                                        sales_user = sales_user_res.data[0]
                                        sales_subject, sales_body = build_sales_confirmation_email(
                                            updated_booking,
                                            sales_user.get("name", "Sales Person")
                                        )
                                        send_email(sales_user["email"], sales_subject, sales_body)

                                    rp_user_res = (
                                        supabase.table("users")
                                        .select("*")
                                        .eq("mobile_number", assigned_number)
                                        .execute()
                                    )

                                    if rp_user_res.data:
                                        rp_user = rp_user_res.data[0]
                                        rp_subject, rp_body = build_resource_assignment_email(
                                            updated_booking,
                                            rp_user.get("name", "Resource Person")
                                        )
                                        send_email(rp_user["email"], rp_subject, rp_body)

                                st.success("Booking approved and resource person assigned automatically.")
                                st.rerun()

                            else:
                                supabase.table("bookings").update({
                                    "status": "approved"
                                }).eq("id", booking_id).execute()

                                st.success("Booking approved successfully. Please assign a resource person manually.")
                                st.rerun()

                        except Exception as e:
                            st.error(f"Approve failed: {e}")

                with col2:
                    if st.button("Reject", use_container_width=True, key="admin_reject_booking"):
                        try:
                            supabase.table("bookings").update({
                                "status": "rejected"
                            }).eq("id", booking_id).execute()

                            st.success("Booking rejected successfully.")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Reject failed: {e}")

                with col3:
                    if session_type in ["avrd", "mini_workshop", "workshop"]:
                        if st.button("Assign RP Only", use_container_width=True, key="admin_assign_rp_only"):
                            try:
                                if not selected_rp_label:
                                    st.error("Please select a resource person.")
                                    st.stop()

                                assigned_number = available_rp_options[selected_rp_label]

                                supabase.table("bookings").update({
                                    "resource_person_number": assigned_number,
                                    "status": "rp_assigned"
                                }).eq("id", booking_id).execute()

                                updated_booking_res = (
                                    supabase.table("bookings")
                                    .select("*")
                                    .eq("id", booking_id)
                                    .execute()
                                )

                                if updated_booking_res.data:
                                    updated_booking = updated_booking_res.data[0]

                                    rp_user_res = (
                                        supabase.table("users")
                                        .select("*")
                                        .eq("mobile_number", assigned_number)
                                        .execute()
                                    )

                                    if rp_user_res.data:
                                        rp_user = rp_user_res.data[0]
                                        rp_subject, rp_body = build_resource_assignment_email(
                                            updated_booking,
                                            rp_user.get("name", "Resource Person")
                                        )
                                        send_email(rp_user["email"], rp_subject, rp_body)

                                st.success("Resource person assigned successfully.")
                                st.rerun()

                            except Exception as e:
                                st.error(f"RP assignment failed: {e}")
                    else:
                        st.info("Resource person is auto-assigned on approval.")

            else:
                st.info("No pending or approved bookings found.")

        except Exception as e:
            st.error(f"Could not load class status section: {e}")

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
                resource_table = []

                for user in rp_users_res.data:
                    subject_1 = ""
                    subject_2 = ""
                    subject_3 = ""

                    try:
                        profile = get_resource_profile_for_user(user)
                        if profile:
                            subject_1 = profile.get("subject_1", "")
                            subject_2 = profile.get("subject_2", "")
                            subject_3 = profile.get("subject_3", "")
                    except Exception:
                        pass

                    resource_table.append({
                        "Name": user.get("name", ""),
                        "Mobile": user.get("mobile_number", ""),
                        "Email": user.get("email", ""),
                        "Subject 1": subject_1,
                        "Subject 2": subject_2,
                        "Subject 3": subject_3
                    })

                st.dataframe(resource_table, use_container_width=True, hide_index=True)
            else:
                st.info("No resource persons found.")

        except Exception as e:
            st.error(f"Could not load resource persons: {e}")

    with tab5:
        st.subheader("Feedback Overview")

        st.markdown("### Sales Person Feedback")
        try:
            sales_feedback_res = (
                supabase.table("feedback_sales")
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )

            if sales_feedback_res.data:
                sales_table = []
                for fb in sales_feedback_res.data:
                    sales_table.append({
                        "Booking ID": fb.get("booking_id", ""),
                        "Sales Person Number": fb.get("sales_person_number", ""),
                        "Session Rating": fb.get("session_rating", ""),
                        "Comments": fb.get("feedback_text", ""),
                        "Created At": fb.get("created_at", "")
                    })

                st.dataframe(sales_table, use_container_width=True, hide_index=True)
            else:
                st.info("No sales feedback found.")

        except Exception as e:
            st.error(f"Could not load sales feedback: {e}")

        st.markdown("### Resource Person Feedback")
        try:
            resource_feedback_res = (
                supabase.table("feedback_resource")
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )

            if resource_feedback_res.data:
                resource_table = []
                for fb in resource_feedback_res.data:
                    resource_table.append({
                        "Booking ID": fb.get("booking_id", ""),
                        "Resource Person Number": fb.get("resource_person_number", ""),
                        "Session Rating": fb.get("session_rating", ""),
                        "Feedback": fb.get("feedback_text", ""),
                        "Remark": fb.get("remark_text", ""),
                        "Created At": fb.get("created_at", "")
                    })

                st.dataframe(resource_table, use_container_width=True, hide_index=True)
            else:
                st.info("No resource feedback found.")

        except Exception as e:
            st.error(f"Could not load resource feedback: {e}")

    with tab6:
        st.subheader("Reports")

        try:
            all_bookings_res = supabase.table("bookings").select("*").execute()
            sales_feedback_res = supabase.table("feedback_sales").select("*").execute()
            resource_feedback_res = supabase.table("feedback_resource").select("*").execute()

            all_bookings = all_bookings_res.data if all_bookings_res.data else []
            sales_feedback = sales_feedback_res.data if sales_feedback_res.data else []
            resource_feedback = resource_feedback_res.data if resource_feedback_res.data else []

            total_bookings = len(all_bookings)
            pending_count = len([b for b in all_bookings if b.get("status") == "pending"])
            approved_count = len([b for b in all_bookings if b.get("status") in ["approved", "rp_assigned", "zoom_sent"]])
            completed_count = len([b for b in all_bookings if b.get("status") in ["completed", "feedback_pending", "closed"]])
            rejected_count = len([b for b in all_bookings if b.get("status") == "rejected"])

            sales_feedback_count = len(sales_feedback)
            resource_feedback_count = len(resource_feedback)

            sales_ratings = [fb.get("session_rating") for fb in sales_feedback if fb.get("session_rating") is not None]
            resource_ratings = [fb.get("session_rating") for fb in resource_feedback if fb.get("session_rating") is not None]

            avg_sales_rating = round(sum(sales_ratings) / len(sales_ratings), 2) if sales_ratings else 0
            avg_resource_rating = round(sum(resource_ratings) / len(resource_ratings), 2) if resource_ratings else 0

            st.markdown("### Overall Summary")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Bookings", total_bookings)
                st.metric("Pending Bookings", pending_count)
                st.metric("Approved / Assigned", approved_count)

            with col2:
                st.metric("Completed Bookings", completed_count)
                st.metric("Rejected Bookings", rejected_count)
                st.metric("Sales Feedback Count", sales_feedback_count)

            with col3:
                st.metric("Resource Feedback Count", resource_feedback_count)
                st.metric("Average Sales Rating", avg_sales_rating)
                st.metric("Average Resource Rating", avg_resource_rating)

            st.markdown("### Daily Class Report")

            if all_bookings:
                daily_summary = {}

                sales_feedback_map = {}
                for fb in sales_feedback:
                    booking_id = fb.get("booking_id")
                    if booking_id:
                        sales_feedback_map[booking_id] = fb.get("session_rating")

                resource_feedback_map = {}
                for fb in resource_feedback:
                    booking_id = fb.get("booking_id")
                    if booking_id:
                        resource_feedback_map[booking_id] = fb.get("session_rating")

                for booking in all_bookings:
                    booking_date = booking.get("preferred_date", "Unknown Date")

                    if booking_date not in daily_summary:
                        daily_summary[booking_date] = {
                            "Date": booking_date,
                            "Total Classes": 0,
                            "Pending": 0,
                            "Approved / Assigned": 0,
                            "Completed": 0,
                            "Rejected": 0,
                            "Sales Ratings": [],
                            "Resource Ratings": []
                        }

                    daily_summary[booking_date]["Total Classes"] += 1

                    status = booking.get("status", "")
                    if status == "pending":
                        daily_summary[booking_date]["Pending"] += 1
                    elif status in ["approved", "rp_assigned", "zoom_sent"]:
                        daily_summary[booking_date]["Approved / Assigned"] += 1
                    elif status in ["completed", "feedback_pending", "closed"]:
                        daily_summary[booking_date]["Completed"] += 1
                    elif status == "rejected":
                        daily_summary[booking_date]["Rejected"] += 1

                    booking_id = booking.get("id")

                    if booking_id in sales_feedback_map and sales_feedback_map[booking_id] is not None:
                        daily_summary[booking_date]["Sales Ratings"].append(sales_feedback_map[booking_id])

                    if booking_id in resource_feedback_map and resource_feedback_map[booking_id] is not None:
                        daily_summary[booking_date]["Resource Ratings"].append(resource_feedback_map[booking_id])

                report_rows = []
                for _, data in daily_summary.items():
                    avg_sales = round(sum(data["Sales Ratings"]) / len(data["Sales Ratings"]), 2) if data["Sales Ratings"] else 0
                    avg_resource = round(sum(data["Resource Ratings"]) / len(data["Resource Ratings"]), 2) if data["Resource Ratings"] else 0

                    report_rows.append({
                        "Date": data["Date"],
                        "Total Classes": data["Total Classes"],
                        "Pending": data["Pending"],
                        "Approved / Assigned": data["Approved / Assigned"],
                        "Completed": data["Completed"],
                        "Rejected": data["Rejected"],
                        "Average Sales Rating": avg_sales,
                        "Average Resource Rating": avg_resource
                    })

                report_rows = sorted(report_rows, key=lambda x: x["Date"], reverse=True)

                report_df = pd.DataFrame(report_rows)
                st.dataframe(report_df, use_container_width=True, hide_index=True)

                csv_data = report_df.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="Download Daily Report CSV",
                    data=csv_data,
                    file_name="daily_class_report.csv",
                    mime="text/csv"
                )
            else:
                st.info("No booking data available for reports.")

        except Exception as e:
            st.error(f"Could not load reports: {e}")

    st.markdown("---")
    if st.button("Logout", use_container_width=True, key="admin_logout"):
        logout()

    render_footer()


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
