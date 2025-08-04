import streamlit as st 
st.set_page_config(page_title="INSIGHT", layout="wide", page_icon="./oask_short_logo.png", initial_sidebar_state="collapsed" )

from streamlit_navigation_bar import st_navbar
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from pages.google_auth import login, fetch_token, get_user_info
from urllib.parse import urlparse, parse_qs
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
import numpy as np
import random
from pages.menu import menu_with_redirect
import plotly.express as px
import os
import re
from streamlit_cookies_manager import EncryptedCookieManager
import json
import streamlit_authenticator as stauth
import bcrypt
from supabase import create_client, Client
import smtplib
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pytz



# Initialize cookies
if "cookies" not in st.session_state:
    cookies = EncryptedCookieManager(prefix="myapp_", password=st.secrets.COOKIE_SECRET)
    if not cookies.ready():
        st.stop()
    st.session_state["cookies"] = cookies
else:
    cookies = st.session_state["cookies"]



url = st.secrets["SUPABASE_URL"] 
key = st.secrets["SUPABASE_KEY"] 
supabase: Client = create_client(url, key)

def normalize_org_name(name):
    return re.sub(r'\W+', '', name).strip().lower()



# st.html("""
#     <style>
#     @import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');
#     html, body, [class*="css"]  {
#         font-family: 'Poppins', sans-serif;
#     }
#     </style>"""
#     "<h1 style='text-align: center; font-size: 65px; font-weight: 900; font-family: Poppins; margin-bottom: 0px'>INSIGHT</h1>"
# )
logo = st.logo("./oask_light_mode_tagline.png", size="large", link="https://oregonask.org/")

st.set_option("client.showSidebarNavigation", False)

# -------- ASSESSMENTS DICTIONARY --------
ASSESSMENTS = {
    "Environment, Health, and Safety": {"form_url": "...", "sheet_name": "Environment, Health, and Safety (Responses)"},
    "Highly Skilled Personnel": {"form_url": "...", "sheet_name": "Highly Skilled Personnel (Responses)"},
    "Program Management": {"form_url": "...", "sheet_name": "Program Management (Responses)"},
    "Youth Development and Engagement": {"form_url": "...", "sheet_name": "Youth Development and Engagement (Responses)"},
    "Programming and Activities": {"form_url": "...", "sheet_name": "Programming and Activities (Responses)"},
    "Families, Schools, and Communities": {"form_url": "...", "sheet_name": "Families, Schools, and Communities (Responses)"},
}

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* Apply Poppins font to Streamlit buttons */
    button[kind="primary"], button[kind="secondary"] {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)


if "mode" not in st.session_state:
    st.session_state["mode"] = "login"  # or "reset_password" if using query param

# Check for password reset token in query string
query_params = st.query_params
if "token" in query_params:
    st.session_state["mode"] = "reset_password"
    st.session_state["reset_token"] = query_params["token"]

# --- Mode: Forgot Password ---
if st.session_state["mode"] == "forgot_password":
    st.title("Forgot Password")
    email = st.text_input("Enter your email")

    if st.button("Send Reset Email"):
        token = str(uuid4())
        expiration = datetime.now(timezone.utc) + timedelta(minutes=30)

        # Store in Supabase
        supabase.table("password_resets").insert({
            "email": email,
            "token": token,
            "expires_at": expiration.isoformat()
        }).execute()

        reset_link = f"https://getinsights.streamlit.app?token={token}"  # Update this!

        # Send email
        def send_reset_email(to_email, reset_link):
            msg = MIMEMultipart()
            msg["From"] = f"{st.secrets['FROM_NAME']} <{st.secrets['EMAIL_ADDRESS']}>"
            msg["To"] = to_email
            msg["Subject"] = "INSIGHT Password Reset"
            html = f"""
            <p>Click below to reset your password:</p>
            <a href="{reset_link}">{reset_link}</a>
            """
            msg.attach(MIMEText(html, "html"))
            try:
                server = smtplib.SMTP(st.secrets["EMAIL_HOST"], st.secrets["EMAIL_PORT"])
                server.starttls()
                server.login(st.secrets["EMAIL_USERNAME"], st.secrets["EMAIL_PASSWORD"])
                server.sendmail(st.secrets["EMAIL_ADDRESS"], to_email, msg.as_string())
                server.quit()
                return True
            except Exception as e:
                st.error(f"Failed to send email: {e}")
                return False

        if send_reset_email(email, reset_link):
            st.success("Password reset link sent!")
        else:
            st.error("Email failed to send.")

    st.button("Back to Login", on_click=lambda: st.session_state.update(mode="login"))

# --- Mode: Reset Password with Token ---
elif st.session_state["mode"] == "reset_password":
    def update_user_password(email, new_password):
        email = email.strip().lower()
        # Hash the new password
        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

        # Update the user record in Supabase
        try:
            res = supabase.table("users").update({"hash": hashed}).eq("email", email).execute()
            if res.data:
                return True
            else:
                return False
        except Exception as e:
            st.error(f"Failed to update password: {e}")
            return False

    st.title("Reset Your Password")
    token = st.session_state["reset_token"]

    res = supabase.table("password_resets").select("*").eq("token", token).execute()
    if res.data:
        record = res.data[0]
        expires_at = datetime.fromisoformat(record["expires_at"])
        
        # Compare timezone-aware datetimes
        if expires_at > datetime.now(timezone.utc):
            new_pw = st.text_input("New Password", type="password")
            confirm_pw = st.text_input("Confirm Password", type="password")
            if st.button("Reset Password"):
                if new_pw != confirm_pw:
                    st.error("Passwords do not match")
                else:
                    if update_user_password(record["email"], new_pw):
                        st.success("Password updated. You can now log in.")
                        st.session_state["mode"] = "login"
                    else:
                        st.error("Error updating password.")

        else:
            st.error("This reset link has expired.")
    else:
        st.error("Invalid reset token.")

# --- Default: Login/Register Flow ---


else:

    def add_autofill_detection():
        components.html("""
        <script>
        function checkAutofill() {
            const inputs = parent.document.querySelectorAll('input[type="text"], input[type="password"]');
            inputs.forEach(input => {
                if (input.value && input.value !== '') {
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
        }
        
        // Check for autofill after a short delay
        setTimeout(checkAutofill, 100);
        setTimeout(checkAutofill, 500);
        setTimeout(checkAutofill, 1000);
        </script>
        """, height=0)
    # --- UI ---
    st.title("Welcome to INSIGHT")
    col1, col2 = st.columns(2)

    # LOGIN FORM
    with col1:
        with st.form("log_in"):
            st.write("### Log In")
            add_autofill_detection()
            log_org_input = st.text_input("Your organization name", key="log_org")
            log_email = st.text_input("Your email", key="log_email").strip().lower()
            log_password = st.text_input("Your password", type="password", key="log_pass")
            log_submitted = st.form_submit_button("Log In")
        st.button("Forgot Password?", on_click=lambda: st.session_state.update(mode="forgot_password"))

    # SIGNUP FORM
    with col2:
        with st.form("sign_up"):
            st.write("### Sign Up")
            add_autofill_detection()
            sign_org_input = st.text_input("Your organization name", key="sign_org")
            sign_role_input = st.text_input("Your role or title")
            sign_first_name = st.text_input("Your first name")
            sign_last_name = st.text_input("Your last name")
            sign_email = st.text_input("Your email", key="sign_email").strip().lower()
            sign_password = st.text_input("Your password", type="password", key="sign_pass")
            submitted = st.form_submit_button("Sign Up")

    # --- Shared Setup for Google Sheets ---
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    service_account_info = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)
    user_sheet = client.open("All Contacts (Arlo + Salesforce)_6.17.25").worksheet("Sheet1")
    user_records = user_sheet.get_all_records()

 

    # --- Login Logic ---
    if log_submitted:
        match = supabase.table("users").select("*").eq("email", log_email).execute()
        match = match.data
        user_match = next((u for u in user_records if u["Email"].strip().lower() == log_email), None)
        
        user_in = bool(user_match)

        if not user_in or not match:
            st.error("Email not found. Please sign up.")
        else:
            
            stored_hash = match[0]["hash"]
            if bcrypt.checkpw(log_password.encode(), stored_hash.encode()):
                if log_org_input != "":
                    user_org = user_match.get("Organization", "").strip().lower()
                    st.success("Login successful!")
                    st.session_state["user_email"] = log_email
                    st.session_state["org_input"] = log_org_input
                    cookies["user_email"] = log_email
                    cookies["org_input"] = log_org_input
                    oregonask_access = user_match.get("OregonASK Access", "").strip().lower() == "true"
                    # if bool(oregonask_access) == False:
                    #     if user_org == "" or not user_org == log_org_input.strip().lower():
                    #         admin_approved = False   
                    #     else:
                    #         admin_approved = user_match.get("Admin Approved", "").strip().lower() == "true"
                    user_org = user_match.get("Organization", "")
                    normalized_user_org = normalize_org_name(user_org)
                    normalized_input_org = normalize_org_name(log_org_input)

                    if not oregonask_access:
                        if normalized_user_org == "" or normalized_user_org != normalized_input_org:
                            admin_approved = False
                        else:
                            admin_approved = user_match.get("Admin Approved", "").strip().lower() == "true"
                            st.session_state["org_input"] = user_org
                            cookies["org_input"] = user_org

                    else:
                        admin_approved = user_match.get("Admin Approved", "").strip().lower() == "true"
                    oregonask_access = user_match.get("OregonASK Access", "").strip().lower() == "true"
                    st.session_state["is_admin"] = admin_approved
                    cookies["admin_input"] = str(admin_approved)

                    st.session_state["access"] = oregonask_access
                    cookies["access_level"] = str(oregonask_access)
                    cookies.save()
                    st.switch_page("pages/home.py")
                else:
                    st.error("Please enter an organization.")
            else:
                st.error("Incorrect password.")
    def convert_to_pacific(timestamp):
        utc_time = datetime.fromisoformat(timestamp)
        pacific = pytz.timezone("US/Pacific")
        pacific_time = utc_time.astimezone(pacific)
        return pacific_time.strftime("%Y-%m-%d %I:%M %p PT")
    # --- Signup Logic ---
    if submitted:
        match = supabase.table("users").select("*").eq("email", sign_email).execute()


        user_match = next((u for u in user_records if u["Email"].strip().lower() == sign_email), None)
        match = match.data

        user_in = bool(user_match)

        # timestamp = str(match[0]["created_at"])
        if not match and not user_in:
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(sign_password.encode(), salt).decode()
            supabase.table("users").insert({"email": sign_email, "hash": hashed_pw}).execute()
            if sign_org_input != "" and sign_first_name != "" and sign_last_name!= "" and sign_email != "" and sign_role_input!="":
                try:
                    match = supabase.table("users").select("*").eq("email", sign_email).execute()
                    user_match = next((u for u in user_records if u["Email"].strip().lower() == sign_email), None)
                    match = match.data
                    timestamp_str = str(match[0]["created_at"])
                    timestamp = convert_to_pacific(timestamp_str)
                    existing_orgs = [
                        normalize_org_name(r["Organization"]) 
                        for r in user_records 
                        if r.get("Organization", "").strip() != ""
                    ]
                    creating_new_org = normalize_org_name(sign_org_input) not in existing_orgs

                    # creating_new_org = sign_org_input.strip().lower() not in [
                    #     r["Organization"].strip().lower() for r in user_records if "Organization" in r
                    # ]
                    admin_approved = "True" if creating_new_org else "False"

                    user_sheet.append_row([
                        "INSIGHT", sign_first_name, sign_last_name, sign_role_input,
                        sign_org_input, sign_email, "", "", admin_approved, "FALSE", timestamp
                    ])
                    st.success("Account created! Please log in.")
                except Exception as e:
                    st.error(f"Failed to write to Google Sheet: {e}")
            else:
                st.error("Please fill in all sign up fields.")
        elif match and not user_in:
            if sign_org_input != "" and sign_first_name != "" and sign_last_name!= "" and sign_email != "" and sign_role_input!="":
                try:
                    timestamp_str = str(match[0]["created_at"])
                    timestamp = convert_to_pacific(timestamp_str)
                    # creating_new_org = sign_org_input.strip().lower() not in [
                    #     r["Organization"].strip().lower() for r in user_records if "Organization" in r
                    # ]
                    existing_orgs = [
                        normalize_org_name(r["Organization"]) 
                        for r in user_records 
                        if r.get("Organization", "").strip() != ""
                    ]
                    creating_new_org = normalize_org_name(sign_org_input) not in existing_orgs
                    admin_approved = "True" if creating_new_org else "False"

                    user_sheet.append_row([
                        "INSIGHT", sign_first_name, sign_last_name, sign_role_input,
                        sign_org_input, sign_email, "", "", admin_approved, "FALSE", timestamp
                    ])
                    st.success("Account created! Please log in.")
                except Exception as e:
                    st.error(f"Failed to write to Google Sheet: {e}")
            else:
                st.error("Please fill in all sign up fields.")
        elif not match and user_in:
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(sign_password.encode(), salt).decode()
            supabase.table("users").insert({"email": sign_email, "hash": hashed_pw}).execute()
        else:
            st.warning("User already exists. Please log in.")

   