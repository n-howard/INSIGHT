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

# query_params = st.query_params
# query_params = st.query_params
# # if st.query_params.get("code") and "google_token" not in st.session_state:
# #     code = query_params["code"]
# #     token = fetch_token(code)
# #     if token:
# #         st.session_state.google_token = token
# #         st.session_state.user_info = get_user_info(token)
# #     else:
# #         st.error("Login failed.")
# #         st.stop()

# # --- Step 1: Ask to sign in ---

# # if not st.experimental_user.is_logged_in:
# #     if st.button("Log In"):
# #         st.login("auth0")

# # st.json(st.experimental_user)


# # if "google_token" not in st.session_state:
# #     login()
# #     st.stop()
# query_params = st.query_params
# code = query_params.get("code")
# state = query_params.get("state")



# # Extract code and state from URL
# query_params = st.query_params
# code = query_params.get("code")
# state = query_params.get("state") or st.session_state.get("oauth_state")

# if "auth0_token" not in st.session_state:
#     if code and state:
#         token = fetch_token(code)
#         if token:
#             st.session_state["auth0_token"] = token
#             st.session_state["user_info"] = get_user_info(token)
#         else:
#             st.error("Login failed. Please try again.")
#             login()
#             st.stop()
#     else:
#         login()
#         st.stop()




# # else:
# #     st.html("""
# #     <style>
# #     @import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');
# #     html, body, [class*="css"]  {
# #         font-family: 'Poppins', sans-serif;
# #     }
# #     </style>"""
# #     "<h1 style='text-align: center; font-size: 65px; font-weight: 900; font-family: Poppins; margin-bottom: 0px'>INSIGHT</h1>"
# #     )

# user_info = st.session_state.get("user_info", {})
# user_email = user_info.get("email", "").strip().lower()
# user_name = user_info.get("name", "").strip()
# user_info = st.user

# if not st.user.is_logged_in:
#     st.info("Please sign in to continue.")
#     if st.button("Sign In"):
#         st.login("auth0")
#     st.stop()
# if st.user.is_logged_in:
#     home_run()

# st.session_state["user_email"] = st.user.email.strip().lower()
# st.session_state["user_name"] = st.user.name.strip()



# authenticator = stauth.Authenticate(
#     dict(st.secrets['credentials']),
#     st.secrets['cookie']['name'],
#     st.secrets['cookie']['key'],
#     st.secrets['cookie']['expiry_days']
# )
# if st.button("Sign Up"):
#     try:
#         user_email, user_username, user_name = authenticator.register_user(
#             fields={'Form name':'Sign Up for INSIGHT', 'Email':'Email', 'Password': 'Password', 'Repeat Password':'Reenter Password', 'Captcha':'Enter CAPTCHA', 'Register':'Sign Up'}, 
#             merge_username_email=True, password_hint=False)
#         if user_email: 
#             st.success('Account created successfully.')
#     except Exception as e:
#         st.error(e)
# if st.button("Log In"):
#     try:
#         authenticator.login()
#         # if st.button("Forgot Password"):
#         #     try:
#         #         username_of_forgotten_password, \
#         #         email_of_forgotten_password, \
#         #         new_random_password = authenticator.forgot_password()
#         #         if username_of_forgotten_password:
#         #             st.success('A new password will be sent securely.')
#         #             # To securely transfer the new password to the user please see step 8.
#         #         elif username_of_forgotten_password == False:
#         #             st.error('Username not found')
#         #     except Exception as e:
#         #         st.error(e)
#     except Exception as e:
#         st.error(e)

# user_email = st.session_state.get("username")
# user_name = st.session_state.get("name")
# if st.session_state.get('authentication_status') is False:
#     st.error('Username/password is incorrect')
# elif st.session_state.get('authentication_status') is None:
#     st.warning('Please enter your username and password')

# log_on()
# st.warning("We couldn't find your email in the system. Please enter your information to create an account.")
# --- Initialize state ---
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
                    if bool(oregonask_access) == False:
                        if user_org == "" or not user_org == log_org_input.strip().lower():
                            admin_approved = False   
                        else:
                            admin_approved = user_match.get("Admin Approved", "").strip().lower() == "true"
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

    # --- Signup Logic ---
    if submitted:
        match = supabase.table("users").select("*").eq("email", sign_email).execute()


        user_match = next((u for u in user_records if u["Email"].strip().lower() == sign_email), None)
        match = match.data

        user_in = bool(user_match)


        if not match and not user_in:
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(sign_password.encode(), salt).decode()
            supabase.table("users").insert({"email": sign_email, "hash": hashed_pw}).execute()
            if sign_org_input != "" and sign_first_name != "" and sign_last_name!= "" and sign_email != "" and sign_role_input!="":
                try:
                    creating_new_org = sign_org_input.strip().lower() not in [
                        r["Organization"].strip().lower() for r in user_records if "Organization" in r
                    ]
                    admin_approved = "True" if creating_new_org else "False"

                    user_sheet.append_row([
                        "INSIGHT", sign_first_name, sign_last_name, sign_role_input,
                        sign_org_input, sign_email, "", "", admin_approved, "FALSE"
                    ])
                    st.success("Account created! Please log in.")
                except Exception as e:
                    st.error(f"Failed to write to Google Sheet: {e}")
            else:
                st.error("Please fill in all sign up fields.")
        elif match and not user_in:
            if sign_org_input != "" and sign_first_name != "" and sign_last_name!= "" and sign_email != "" and sign_role_input!="":
                try:
                    creating_new_org = sign_org_input.strip().lower() not in [
                        r["Organization"].strip().lower() for r in user_records if "Organization" in r
                    ]
                    admin_approved = "True" if creating_new_org else "False"

                    user_sheet.append_row([
                        "INSIGHT", sign_first_name, sign_last_name, sign_role_input,
                        sign_org_input, sign_email, "", "", admin_approved, "FALSE"
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

    # st.title("Welcome to INSIGHT")
    # col1, col2 = st.columns(2)
    # with col1:
    #     with st.form("log_in"):
    #         st.write("### Log In")
    #         curr_org_input = st.text_input("Your organization name", key = "log_org")
    #         user_email = st.text_input("Your email", key="log_email").strip().lower()
    #         password = st.text_input("Your password", type="password", key="log_pass")
    #         password_to_verify = password.encode('utf-8')
    #         log_submitted = st.form_submit_button("Log In")
    #     st.button("Forgot Password?", on_click=lambda: st.session_state.update(mode="forgot_password"))
    # with col2:
    #     with st.form("sign_up"):
    #         st.write("### Sign Up")
    #         curr_org_input = st.text_input("Your organization name", key = "sign_org")
    #         role_input = st.text_input("Your role or title (e.g., Program Manager, Principal, Staff, etc.)")
    #         first_name = st.text_input("Your first name")
    #         last_name = st.text_input("Your last name")
    #         user_email = st.text_input("Your email", key="sign_email").strip().lower()
    #         password = st.text_input("Your password", type="password", key="sign_pass")
    #         password_to_verify = password.encode('utf-8')
    #         name_input = first_name + " " + last_name
    #         user_name = name_input
    #         submitted = st.form_submit_button("Sign Up")


    # # def sign(user_email, password_to_verify, curr_org_input, first_name, last_name, role_input):
    # # if st.button("Sign In"):
    # if submitted or log_submitted:
    #     # def log_on():
    #     scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    #     # Convert secrets section to JSON string and parse it
    #     service_account_info = dict(st.secrets["gcp_service_account"])
    #     creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    #     client = gspread.authorize(creds)

    #     # # After successful Google login
    #     # user_info = st.session_state.get("user_info", {})
    #     # user_email = st.session_state.get("user_email")
    #     # user_name = st.session_state.get("user_name")

    #     # Load authorized users
    #     user_sheet = client.open("All Contacts (Arlo + Salesforce)_6.17.25").worksheet("Sheet1")
    #     user_records = user_sheet.get_all_records()


    #     if curr_org_input == "":
    #         st.error("Please enter an organization.")
    #         st.switch_page("app.py")
    #     # Match user by email
    #     user_match = next((u for u in user_records if u["Email"].strip().lower() == user_email), None)

    #     st.session_state["user_email"] = user_email
    #     email = st.session_state.get("user_email")
    #     cookies["user_email"] = email
    #     # user_hash_match = next((u for u in hash_records if u["Email"].strip().lower() == user_email), None)

    #     user_hash_match = supabase.table("users").select("*").eq("email", user_email).execute()
        
    #     if not user_hash_match.data:
    #         salt = bcrypt.gensalt()
    #         hashed_password = bcrypt.hashpw(password_to_verify, salt)
    #         # hash_sheet.append_row([user_email,hashed_password.decode('utf-8')])
    #         try:
    #             res = supabase.table("users").insert({
    #                 "email": user_email,
    #                 "hash": hashed_password.decode('utf-8')
    #             }).execute()
    #             st.success("Registration successful")
    #             user_hash_in = True
    #             cookies["org_input"] = curr_org_input
    #             st.session_state["org_input"] = curr_org_input
    #         except Exception as e:
    #             st.error(f"Registration failed: {e}")


    #     # else:
    #     #     # user_hash = user_hash_match.get("Hash", "")
    #     #     res = supabase.table("users").select("*").eq("Email", email).execute()
        
    #     else:
    #         res = supabase.table("users").select("*").eq("email", user_email).execute()
    #         stored_hash = res.data[0]["hash"]
    #         if bcrypt.checkpw(password_to_verify, stored_hash.encode()):
    #             st.success("Login successful")
    #             user_hash_in = True
    #             cookies["org_input"] = curr_org_input
    #             st.session_state["org_input"] = curr_org_input
    #         else:
    #             st.error("You entered an incorrect password. Please try again.")

    #             st.switch_page("app.py")
    #         # if bcrypt.checkpw(password_to_verify, user_hash.encode('utf-8')):
    #         #     user_hash_in = True
    #         #     if user_match:
    #         #         cookies["curr_org_input"] = curr_org_input
    #         #         st.session_state["curr_org_input"] = curr_org_input

    #         # else:
    #         #     st.error("You entered an incorrect password. Please try again.")

    #         #     st.switch_page("app.py")
                
    #     # user_hash_match = next((u for u in hash_records if u["Email"].strip().lower() == user_email), None)       
    #     # user_hash = user_hash_match.get("Hash", "")
    #     # user_hash_in = bool(bcrypt.checkpw(password_to_verify, user_hash.encode('utf-8')))
    #     user_hash_in = True
        
    #     user_email = cookies.get("user_email")
    #     user_match = next((u for u in user_records if u["Email"].strip().lower() == user_email.strip().lower()), None)

    #     user_in = bool(user_match)

    #     curr_org_input = cookies.get("org_input")

    #     if not user_in:
    #         st.session_state["name_input"] = name_input.strip()
    #         st.session_state["role"] = role_input.strip()
    #         creating_new_org = curr_org_input.strip().lower() not in [r["Organization"].strip().lower() for r in user_records if "Organization" in r]

    #         admin_approved = "True" if creating_new_org else "False"

    #         oregonask_access = "False"

    #         user_sheet.append_row(["INSIGHT", first_name, last_name, role_input, curr_org_input, user_email, "", "", admin_approved, "FALSE"])

    #         st.session_state["is_admin"] = admin_approved == "True"
    #         cookies["admin_input"] = admin_approved


    #     user_sheet = client.open("All Contacts (Arlo + Salesforce)_6.17.25").worksheet("Sheet1")
    #     user_records = user_sheet.get_all_records()
    #     user_email = cookies.get("user_email")
    #     user_match = next((u for u in user_records if u["Email"].strip().lower() == user_email.strip().lower()), None)

    #     user_in = bool(user_match)

    #     curr_org_input = cookies.get("org_input")

    #     try:
    #         user_org = user_match.get("Organization", "").strip().lower()
    #     except:
    #         user_org = curr_org_input

        


    #     # user_in = bool(user_match)

    #     # org_in = bool(user_org)

    #     # if user_org=="":
    #     #     org_in = False
    #     # else:
    #     #     org_in = True

    #     # if not user_in:
    #     #     st.session_state["name_input"] = name_input.strip()
    #     #     st.session_state["role"] = role_input.strip()
    #     #     creating_new_org = curr_org_input.strip().lower() not in [r["Organization"].strip().lower() for r in user_records if "Organization" in r]

    #     #     admin_approved = "True" if creating_new_org else "False"

    #     #     oregonask_access = "False"

    #     #     user_sheet.append_row(["INSIGHT", first_name, last_name, role_input, curr_org_input, user_email, "", "", admin_approved, "FALSE"])

    #     #     st.session_state["is_admin"] = admin_approved == "True"
    #     #     cookies["admin_input"] = admin_approved
    #     # if user_org=="":
    #     #     org_in = False
    #     # else:
    #     #     org_in = True
    # # --- If user not found: allow account creation ---
    # # if not user_in:
    # #     st.warning("We couldn't find your email in the system. Please enter your information to create an account.")
    # #     first_name = st.text_input("Your first name")
    # #     last_name = st.text_input("Your last name")
    # #     user_email = st.text_input("Your email")
    # #     role_input = st.text_input("Your role or title (e.g., Program Manager, Principal, Staff, etc.)")
    # #     curr_org_input = st.text_input("Your organization name")
    # #     name_input = first_name + " " + last_name
    # #     if st.button("Create Account") and role_input:
    # #         st.session_state["name_input"] = name_input.strip()
    # #         st.session_state["role"] = role_input.strip()

    # #         creating_new_org = curr_org_input.lower() not in [r["Organization"].strip().lower() for r in user_records if "Organization" in r]

    # #         admin_approved = "True" if creating_new_org else "False"

    # #         oregonask_access = "False"

    # #         user_sheet.append_row(["INSIGHT", first_name, last_name, role_input, curr_org_input, user_email, "", "", admin_approved, "FALSE"])

    # #         st.session_state["is_admin"] = admin_approved == "True"
    # #         cookies["admin_input"] = admin_approved
    # #         cookies.save()



    # #         st.success("Account created successfully!")
    # #         user_in = True
    # #         st.rerun()
    # #         # Force initialize once


    #     if user_in and user_hash_in: #and org_in:

    #         # --- If user is found ---
    #         role = user_match["Title"]
    #         st.session_state["role"] = role
    #         # st.session_state["name"] = user_match.get("Name", user_name)
    #         st.session_state["name"] = user_match.get("Name", "")
    #         st.info(f"Welcome, **{st.session_state['name']}**! Your title: **{role}**")

    #         # --- Define admin roles by substrings ---
    #         # admin_keywords = ["director", "president", "principal", "ceo", "admin", "manager", "coordinator", "leader", "owner", "superintendent", "directora", "chief", "mayor", "chair", "founder", "oregonask intern"]

    #         # Simple role check
    #         def is_admin_role(role):
    #             return any(keyword in role.lower() for keyword in admin_keywords)

    #         # Flag admin access
    #         # st.session_state["is_admin"] = is_admin_role(st.session_state.get("role", ""))

    #         # Pull the user's row by email
    #         user_match = next((u for u in user_records if u["Email"].strip().lower() == user_email), None)

    #         admin_approved = user_match.get("Admin Approved", "").strip().lower() == "true"
    #         st.session_state["is_admin"] = admin_approved
    #         cookies["admin_input"] = str(admin_approved)
    #         oregonask_access = user_match.get("OregonASK Access", "").strip().lower() == "true"
    #         st.session_state["access"] = oregonask_access
    #         cookies["access_level"] = str(oregonask_access)



    #         if st.session_state["is_admin"]:
    #             st.success("You have admin-level access.")
    #         else:
    #             st.info("You have standard access.")
    #         # user_org = user_match.get("Organization", "").strip().lower()
    #         user_org = curr_org_input
    #         site_input = ""

    #         st.session_state["org_input"] = user_org
    #         st.session_state["site_input"] = site_input

    #         cookies["org_input"] = user_org
    #         cookies["site_input"] = site_input

    #         cookies.save()

    #         st.success(f"Signed in automatically to: {user_org}")

    #         st.switch_page("pages/home.py")

    #     # if user_in and user_hash_in and not org_in:
    #     #     creating_new_org = curr_org_input.strip().lower() not in [r["Organization"].strip().lower() for r in user_records if "Organization" in r]
    #     #     admin_approved = "True" if creating_new_org else "False"

    #     #     st.session_state["is_admin"] = admin_approved
    #     #     cookies["admin_input"] = str(admin_approved)

    #     #     oregonask_access = False
    #     #     st.session_state["access"] = oregonask_access
    #     #     cookies["access_level"] = str(oregonask_access)

    #     #     user_org = curr_org_input
    #     #     site_input = ""

    #     #     st.session_state["org_input"] = user_org
    #     #     st.session_state["site_input"] = site_input

    #     #     cookies["org_input"] = user_org
    #     #     cookies["site_input"] = site_input


    #     #     cookies.save()

    #     #     st.switch_page("pages/home.py")
    # # if 'show_login' not in st.session_state:
    # # st.session_state.show_login = False
    # # if 'show_sign' not in st.session_state:
    # # st.session_state.show_sign = False

    # # def toggle_login():
    # # st.session_state.show_login = not st.session_state.show_login



    # # def toggle_sign():
    # # st.session_state.show_sign = not st.session_state.show_sign


    # # st.title("Welcome to INSIGHT")
    # # st.write("### Log In or Sign Up")
    # # col1, col2 = st.columns(2)
    # # with col1:
    # #     st.button("Log In", use_container_width=True, on_click=toggle_login)
    # #     if st.session_state.show_login:
    # #         st.session_state.show_sign = False
    # #         user_email = st.text_input("Your email").strip().lower()
    # #         password = st.text_input("Your password", type="password")
    # #         password_to_verify = password.encode('utf-8')
    # #         curr_org_input = st.text_input("Your organization name")
    # #         if st.button("Sign In"):
    # #             # def log_on():
    # #             scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # #             # Convert secrets section to JSON string and parse it
    # #             service_account_info = dict(st.secrets["gcp_service_account"])
    # #             creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    # #             client = gspread.authorize(creds)

    # #             # # After successful Google login
    # #             # user_info = st.session_state.get("user_info", {})
    # #             # user_email = st.session_state.get("user_email")
    # #             # user_name = st.session_state.get("user_name")

    # #             # Load authorized users
    # #             user_sheet = client.open("All Contacts (Arlo + Salesforce)_6.17.25").worksheet("Sheet1")
    # #             user_records = user_sheet.get_all_records()

    # #             hash_sheet = client.open("Log In Information").worksheet("Sheet1")
    # #             hash_records = hash_sheet.get_all_records()

    # #             # Match user by email
    # #             user_match = next((u for u in user_records if u["Email"].strip().lower() == user_email), None)

    # #             user_hash_match = next((u for u in hash_records if u["Email"].strip().lower() == user_email), None)

            
    # #             if not user_hash_match:
    # #                 salt = bcrypt.gensalt()
    # #                 hashed_password = bcrypt.hashpw(password_to_verify, salt)
    # #                 hash_sheet.append_row([user_email,hashed_password.decode('utf-8')])
    # #                 user_hash_in = True
    # #             else:
    # #                 user_hash = user_hash_match.get("Hash", "")
    # #                 if bcrypt.checkpw(password_to_verify, user_hash.encode('utf-8')):
    # #                     user_hash_in = True
    # #                     if user_match:
    # #                         cookies["org_input"] = curr_org_input
    # #                         st.session_state["org_input"] = curr_org_input

    # #                 else:
    # #                     st.error("You entered an incorrect password. Please try again.")

    # #                     st.switch_page("app.py")
                    
    # #             user_hash = user_hash_match.get("Hash", "")
    # #             user_hash_in = bool(bcrypt.checkpw(password_to_verify, user_hash.encode('utf-8')))

                    
    # #             user_org = user_match.get("Organization", "").strip().lower() == curr_org_input.strip().lower()

    # #             user_in = bool(user_match)

    # #             org_in = bool(user_org)

    # #             if not user_in:
    # #                 st.session_state["name_input"] = name_input.strip()
    # #                 st.session_state["role"] = role_input.strip()
    # #                 creating_new_org = curr_org_input.lower() not in [r["Organization"].strip().lower() for r in user_records if "Organization" in r]

    # #                 admin_approved = "True" if creating_new_org else "False"

    # #                 oregonask_access = "False"

    # #                 user_sheet.append_row(["INSIGHT", first_name, last_name, role_input, curr_org_input, user_email, "", "", admin_approved, "FALSE"])

    # #                 st.session_state["is_admin"] = admin_approved == "True"
    # #                 cookies["admin_input"] = admin_approved
    # #                 cookies.save()
    # #                 user_org = user_match.get("Organization", "").strip().lower()
    # #         # --- If user not found: allow account creation ---
    # #         # if not user_in:
    # #         #     st.warning("We couldn't find your email in the system. Please enter your information to create an account.")
    # #         #     first_name = st.text_input("Your first name")
    # #         #     last_name = st.text_input("Your last name")
    # #         #     user_email = st.text_input("Your email")
    # #         #     role_input = st.text_input("Your role or title (e.g., Program Manager, Principal, Staff, etc.)")
    # #         #     curr_org_input = st.text_input("Your organization name")
    # #         #     name_input = first_name + " " + last_name
    # #         #     if st.button("Create Account") and role_input:
    # #         #         st.session_state["name_input"] = name_input.strip()
    # #         #         st.session_state["role"] = role_input.strip()

    # #         #         creating_new_org = curr_org_input.lower() not in [r["Organization"].strip().lower() for r in user_records if "Organization" in r]

    # #         #         admin_approved = "True" if creating_new_org else "False"

    # #         #         oregonask_access = "False"

    # #         #         user_sheet.append_row(["INSIGHT", first_name, last_name, role_input, curr_org_input, user_email, "", "", admin_approved, "FALSE"])

    # #         #         st.session_state["is_admin"] = admin_approved == "True"
    # #         #         cookies["admin_input"] = admin_approved
    # #         #         cookies.save()



    # #         #         st.success("Account created successfully!")
    # #         #         user_in = True
    # #         #         st.rerun()
    # #         #         # Force initialize once

    # #             if user_in and user_hash_in and org_in:
    # #                 org_input = None

    # #                 # --- If user is found ---
    # #                 role = user_match["Title"]
    # #                 st.session_state["role"] = role
    # #                 # st.session_state["name"] = user_match.get("Name", user_name)
    # #                 st.session_state["name"] = user_match.get("Name", "")
    # #                 st.info(f"Welcome, **{st.session_state['name']}**! Your title: **{role}**")

    # #                 # --- Define admin roles by substrings ---
    # #                 # admin_keywords = ["director", "president", "principal", "ceo", "admin", "manager", "coordinator", "leader", "owner", "superintendent", "directora", "chief", "mayor", "chair", "founder", "oregonask intern"]

    # #                 # Simple role check
    # #                 def is_admin_role(role):
    # #                     return any(keyword in role.lower() for keyword in admin_keywords)

    # #                 # Flag admin access
    # #                 # st.session_state["is_admin"] = is_admin_role(st.session_state.get("role", ""))

    # #                 # Pull the user's row by email
    # #                 user_match = next((u for u in user_records if u["Email"].strip().lower() == user_email), None)

    # #                 admin_approved = user_match.get("Admin Approved", "").strip().lower() == "true"
    # #                 st.session_state["is_admin"] = admin_approved
    # #                 cookies["admin_input"] = str(admin_approved)
    # #                 oregonask_access = user_match.get("OregonASK Access", "").strip().lower() == "true"
    # #                 st.session_state["access"] = oregonask_access
    # #                 cookies["access_level"] = str(oregonask_access)



    # #                 if st.session_state["is_admin"]:
    # #                     st.success("You have admin-level access.")
    # #                 else:
    # #                     st.info("You have standard access.")
    # #                 # user_org = user_match.get("Organization", "").strip().lower()
    # #                 user_org = curr_org_input
    # #                 site_input = ""

    # #                 st.session_state["org_input"] = user_org
    # #                 st.session_state["site_input"] = site_input

    # #                 cookies["org_input"] = user_org
    # #                 cookies["site_input"] = site_input

    # #                 cookies.save()

    # #                 st.success(f"Signed in automatically to: {user_org}")

    # #                 st.switch_page("pages/home.py")

    # #             elif not org_in:
    # #                 creating_new_org = curr_org_input.lower() not in [r["Organization"].strip().lower() for r in user_records if "Organization" in r]
    # #                 admin_approved = "True" if creating_new_org else "False"

    # #                 st.session_state["is_admin"] = admin_approved
    # #                 cookies["admin_input"] = str(admin_approved)

    # #                 oregonask_access = False
    # #                 st.session_state["access"] = oregonask_access
    # #                 cookies["access_level"] = str(oregonask_access)

    # #                 user_org = curr_org_input
    # #                 site_input = ""

    # #                 st.session_state["org_input"] = user_org
    # #                 st.session_state["site_input"] = site_input

    # #                 cookies["org_input"] = user_org
    # #                 cookies["site_input"] = site_input

    # #                 cookies.save()
    # # with col2:
    # #     st.button("Sign Up", use_container_width=True, on_click=toggle_sign)
    # #     if st.session_state.show_sign:
    # #         st.session_state.show_login = False
    # #         first_name = st.text_input("Your first name")
    # #         last_name = st.text_input("Your last name")
    # #         user_email = st.text_input("Your email").strip().lower()
    # #         password = st.text_input("A password", type="password")
    # #         password_to_verify = password.encode('utf-8')
    # #         role_input = st.text_input("Your role or title (e.g., Program Manager, Principal, Staff, etc.)")
    # #         curr_org_input = st.text_input("Your organization name")
    # #         name_input = first_name + " " + last_name
    # #         user_name = name_input
    # #         if st.button("Sign In"):
    # #             # def log_on():
    # #             scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # #             # Convert secrets section to JSON string and parse it
    # #             service_account_info = dict(st.secrets["gcp_service_account"])
    # #             creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    # #             client = gspread.authorize(creds)

    # #             # # After successful Google login
    # #             # user_info = st.session_state.get("user_info", {})
    # #             # user_email = st.session_state.get("user_email")
    # #             # user_name = st.session_state.get("user_name")

    # #             # Load authorized users
    # #             user_sheet = client.open("All Contacts (Arlo + Salesforce)_6.17.25").worksheet("Sheet1")
    # #             user_records = user_sheet.get_all_records()

    # #             hash_sheet = client.open("Log In Information").worksheet("Sheet1")
    # #             hash_records = hash_sheet.get_all_records()

    # #             # Match user by email
    # #             user_match = next((u for u in user_records if u["Email"].strip().lower() == user_email), None)

    # #             user_hash_match = next((u for u in hash_records if u["Email"].strip().lower() == user_email), None)

            
    # #             if not user_hash_match:
    # #                 salt = bcrypt.gensalt()
    # #                 hashed_password = bcrypt.hashpw(password_to_verify, salt)
    # #                 hash_sheet.append_row([user_email,hashed_password.decode('utf-8')])
    # #                 user_hash_in = True
    # #             else:
    # #                 user_hash = user_hash_match.get("Hash", "")
    # #                 if bcrypt.checkpw(password_to_verify, user_hash.encode('utf-8')):
    # #                     user_hash_in = True
    # #                     if user_match:
    # #                         cookies["org_input"] = curr_org_input
    # #                         st.session_state["org_input"] = curr_org_input

    # #                 else:
    # #                     st.error("You entered an incorrect password. Please try again.")

    # #                     st.switch_page("app.py")
                    
    # #             user_hash = user_hash_match.get("Hash", "")
    # #             user_hash_in = bool(bcrypt.checkpw(password_to_verify, user_hash.encode('utf-8')))

                    
    # #             user_org = user_match.get("Organization", "").strip().lower() == curr_org_input.strip().lower()

    # #             user_in = bool(user_match)

    # #             org_in = bool(user_org)

    # #             if not user_in:
    # #                 st.session_state["name_input"] = name_input.strip()
    # #                 st.session_state["role"] = role_input.strip()
    # #                 creating_new_org = curr_org_input.lower() not in [r["Organization"].strip().lower() for r in user_records if "Organization" in r]

    # #                 admin_approved = "True" if creating_new_org else "False"

    # #                 oregonask_access = "False"

    # #                 user_sheet.append_row(["INSIGHT", first_name, last_name, role_input, curr_org_input, user_email, "", "", admin_approved, "FALSE"])

    # #                 st.session_state["is_admin"] = admin_approved == "True"
    # #                 cookies["admin_input"] = admin_approved
    # #                 cookies.save()
    # #                 user_org = user_match.get("Organization", "").strip().lower()
    # #         # --- If user not found: allow account creation ---
    #     # if not user_in:
    #     #     st.warning("We couldn't find your email in the system. Please enter your information to create an account.")
    #     #     first_name = st.text_input("Your first name")
    #     #     last_name = st.text_input("Your last name")
    #     #     user_email = st.text_input("Your email")
    #     #     role_input = st.text_input("Your role or title (e.g., Program Manager, Principal, Staff, etc.)")
    #     #     curr_org_input = st.text_input("Your organization name")
    #     #     name_input = first_name + " " + last_name
    #     #     if st.button("Create Account") and role_input:
    #     #         st.session_state["name_input"] = name_input.strip()
    #     #         st.session_state["role"] = role_input.strip()

    #     #         creating_new_org = curr_org_input.lower() not in [r["Organization"].strip().lower() for r in user_records if "Organization" in r]

    #     #         admin_approved = "True" if creating_new_org else "False"

    #     #         oregonask_access = "False"

    #     #         user_sheet.append_row(["INSIGHT", first_name, last_name, role_input, curr_org_input, user_email, "", "", admin_approved, "FALSE"])

    #     #         st.session_state["is_admin"] = admin_approved == "True"
    #     #         cookies["admin_input"] = admin_approved
    #     #         cookies.save()



    #     #         st.success("Account created successfully!")
    #     #         user_in = True
    #     #         st.rerun()
    #     #         # Force initialize once

    #         # if user_in and user_hash_in and org_in:
    #         #     org_input = None

    #         #     # --- If user is found ---
    #         #     role = user_match["Title"]
    #         #     st.session_state["role"] = role
    #         #     # st.session_state["name"] = user_match.get("Name", user_name)
    #         #     st.session_state["name"] = user_match.get("Name", "")
    #         #     st.info(f"Welcome, **{st.session_state['name']}**! Your title: **{role}**")

    #         #     # --- Define admin roles by substrings ---
    #         #     # admin_keywords = ["director", "president", "principal", "ceo", "admin", "manager", "coordinator", "leader", "owner", "superintendent", "directora", "chief", "mayor", "chair", "founder", "oregonask intern"]

    #         #     # Simple role check
    #         #     def is_admin_role(role):
    #         #         return any(keyword in role.lower() for keyword in admin_keywords)

    #         #     # Flag admin access
    #         #     # st.session_state["is_admin"] = is_admin_role(st.session_state.get("role", ""))

    #         #     # Pull the user's row by email
    #         #     user_match = next((u for u in user_records if u["Email"].strip().lower() == user_email), None)

    #         #     admin_approved = user_match.get("Admin Approved", "").strip().lower() == "true"
    #         #     st.session_state["is_admin"] = admin_approved
    #         #     cookies["admin_input"] = str(admin_approved)
    #         #     oregonask_access = user_match.get("OregonASK Access", "").strip().lower() == "true"
    #         #     st.session_state["access"] = oregonask_access
    #         #     cookies["access_level"] = str(oregonask_access)



    #         #     if st.session_state["is_admin"]:
    #         #         st.success("You have admin-level access.")
    #         #     else:
    #         #         st.info("You have standard access.")
    #         #     # user_org = user_match.get("Organization", "").strip().lower()
    #         #     user_org = curr_org_input
    #         #     site_input = ""

    #         #     st.session_state["org_input"] = user_org
    #         #     st.session_state["site_input"] = site_input

    #         #     cookies["org_input"] = user_org
    #         #     cookies["site_input"] = site_input

    #         #     cookies.save()

    #         #     st.success(f"Signed in automatically to: {user_org}")

    #         #     st.switch_page("pages/home.py")

    #         # elif not org_in:
    #         #     creating_new_org = curr_org_input.lower() not in [r["Organization"].strip().lower() for r in user_records if "Organization" in r]
    #         #     admin_approved = "True" if creating_new_org else "False"

    #         #     st.session_state["is_admin"] = admin_approved
    #         #     cookies["admin_input"] = str(admin_approved)

    #         #     oregonask_access = False
    #         #     st.session_state["access"] = oregonask_access
    #         #     cookies["access_level"] = str(oregonask_access)

    #         #     user_org = curr_org_input
    #         #     site_input = ""

    #         #     st.session_state["org_input"] = user_org
    #         #     st.session_state["site_input"] = site_input

    #         #     cookies["org_input"] = user_org
    #         #     cookies["site_input"] = site_input

    #         #     cookies.save()
    #         #     # if user_match and user_org!="":
    #         #     #         # Automatically log in
    #         #     #         user_org = user_match.get("Organization", "").strip()
                        
    #         #     #         site_input = ""

    #         #     #         st.session_state["org_input"] = user_org
    #         #     #         st.session_state["site_input"] = site_input

    #         #     #         cookies["org_input"] = user_org
    #         #     #         cookies["site_input"] = site_input

    #         #     #         cookies.save()

    #         #     #         st.success(f"Signed in automatically to: {user_org}")
    #         #     #         # home()
    #         #     #         st.switch_page("pages/home.py")
    #         #     #         # st.session_state["org_input"] = user_org
    #         #     #         # st.session_state["site_input"] = ""
    #         #     #         # cookies["org_input"] = user_org
    #         #     #         # cookies["site_input"] = ""
    #         #     #         # cookies.save()
    #         #     #         # st.session_state["auto_login_trigger"] = True
    #         #     # elif user_org="":
    #         #     #         admin_approved = False
    #         #     #         st.session_state["is_admin"] = admin_approved
    #         #     #         cookies["admin_input"] = str(admin_approved)

    #         #     #         site_input = ""

    #         #     #         st.session_state["org_input"] = curr_org_input
    #         #     #         st.session_state["site_input"] = site_input

    #         #     #         cookies["org_input"] = curr_org_input
    #         #     #         cookies["site_input"] = site_input

    #         # #     @st.cache_data(ttl=3600, show_spinner=False)
    #         # #     def get_org_names():
    #         # #         sheet = client.open("All Programs Statewide_6.17.25").worksheet("All Programs Statewide")
    #         # #         records = sheet.get_all_records(head=9)
    #         # #         org_names = list({row["Account Name"].strip() for row in records if row.get("Account Name")})
    #         # #         return org_names

    #         # #     # Now outside the function: enrich with current user's org if missing
    #         # #     org_names = get_org_names()
    #         # #     if user_match:
    #         # #         user_org = user_match.get("Organization", "").strip()
    #         # #         if user_org and user_org.lower() not in [org.strip().lower() for org in org_names]:
    #         # #             org_names.append(user_org)

    #         # #     org_names = sorted(org_names)
    #         # #     org_names.insert(0, "Search for your organization name...")
    #         # #     org_names.append("Other")



    #         # #     # # Load orgs from cache
    #         # #     # org_names = get_org_names()


    #         # #     def search_orgs(query: str):
    #         # #         return [org for org in org_names if query.lower() in org.lower()]

    #         # #     org_search = st.selectbox(
    #         # #         "Search for your organization",
    #         # #         options=org_names,
    #         # #     )


    #         # #     if org_search == "Other":
    #         # #         custom_org = st.text_input("Please enter your organization name:")
    #         # #         address = st.text_input("Please enter your site's address:")
    #         # #         org_input = custom_org.strip()
    #         # #     elif org_search != "Search for your organization name...":
    #         # #         user_org = user_match.get("Organization", "").strip().lower()
    #         # #         selected_org = org_search.strip().lower()
    #         # #         normalized_orgs = [org.strip().lower() for org in org_names]
    #         # #         org_input = org_search
    #         # #         # else:
    #         # #         #     st.warning("The organization you selected does not match the organization in our system. Please try again.")
    #         # #         #     org_input = False
    #         # #     else:
    #         # #         st.info("Please select the name of the organization you work for.")

    #         # #     # --- Site input (optional) ---
    #         # #     site_input = st.text_input("If your organization has multiple sites, please enter your site name (optional):")

    #         # #     # # --- Continue button ---
    #         # #     # if st.button("Continue"):
    #         # #     #     if not org_input:
    #         # #     #         st.warning("Please select a valid organization before continuing.")
    #         # #     #     else:
    #         # #     #         # Save inputs
    #         # #     #         st.session_state["org_input"] = org_input.strip()
    #         # #     #         st.session_state["site_input"] = site_input.strip() if site_input else ""
    #         # #     #         st.session_state["admin_input"] = "false"
    #         # #     #         st.session_state["access_level"] = str(st.session_state["access"])

    #         # #     #         # Save cookies
    #         # #     #         cookies["org_input"] = st.session_state["org_input"]
    #         # #     #         cookies["site_input"] = st.session_state["site_input"]
    #         # #     #         cookies["admin_input"] = st.session_state["admin_input"]
    #         # #     #         cookies["access_level"] = st.session_state["access_level"]
    #         # #     #         cookies.save()


    #         # #     #         # Write to sheet only if 'Other'
    #         # #     #         if org_search == "Other":
    #         # #     #             def append_clean_row(sheet, values):
    #         # #     #                 col_a = sheet.col_values(1)
    #         # #     #                 next_empty_row = len(col_a) + 1
    #         # #     #                 sheet.update(f"A{next_empty_row}", [values], value_input_option='USER_ENTERED')

    #         # #     #             append_clean_row(
    #         # #     #                 sheet,
    #         # #     #                 ["Active", "", "INSIGHT", custom_org, st.session_state["site_input"], address]
    #         # #     #             )
    #         # #     #             st.cache_data.clear()

    #         # #     #         # Immediately redirect to home.py
    #         # #     #         st.switch_page("pages/home.py")
    #         # #     #         st.experimental_rerun()
    #         # #     if st.session_state.get("redirect_to_home"):
    #         # #         del st.session_state["redirect_to_home"]
    #         # #         st.switch_page("pages/home.py")

    #         # #     if st.button("Continue"):
    #         # #         if not org_input:
    #         #             st.warning("Please select a valid organization before continuing.")
    #         #         else:
    #         #             st.session_state["org_input"] = org_input.strip()
    #         #             st.session_state["site_input"] = site_input.strip() if site_input else ""
    #         #             st.session_state["admin_input"] = "false"
    #         #             st.session_state["access_level"] = str(st.session_state["access"])

    #         #             cookies["org_input"] = st.session_state["org_input"]
    #         #             cookies["site_input"] = st.session_state["site_input"]
    #         #             cookies["admin_input"] = st.session_state["admin_input"]
    #         #             cookies["access_level"] = st.session_state["access_level"]
    #         #             cookies.save()

    #         #             if org_search == "Other":
    #         #                 def append_clean_row(sheet, values):
    #         #                     col_a = sheet.col_values(1)
    #         #                     next_empty_row = len(col_a) + 1
    #         #                     sheet.update(f"A{next_empty_row}", [values], value_input_option='USER_ENTERED')

    #         #                 append_clean_row(
    #         #                     sheet,
    #         #                     ["Active", "", "INSIGHT", custom_org, st.session_state["site_input"], address]
    #         #                 )
    #         #                 st.cache_data.clear()
    #         #             # home()
    #         #             # Trigger redirect cleanly
    #         #             st.session_state["redirect_to_home"] = True
    #         #             st.rerun()
    #         #         # if st.session_state.get("auto_login_trigger"):
    #         #         #     del st.session_state["auto_login_trigger"]
    #         #         #     st.success(f"Signed in automatically to: {st.session_state['org_input']}")
    #         #         #     st.switch_page("pages/home.py")
    #         # # authenticator = stauth.Authenticate(
    #         # #     dict(st.secrets['credentials']),
    #         # #     st.secrets['cookie']['name'],
    #         # #     st.secrets['cookie']['key'],
    #         # #     st.secrets['cookie']['expiry_days']
    #         # # )
    #         # # if st.button("Sign Up"):
    #         # #     try:
    #         # #         user_email, user_username, user_name = authenticator.register_user(
    #         # #             fields={'Form name':'Sign Up for INSIGHT', 'Email':'Email', 'Password': 'Password', 'Repeat Password':'Reenter Password', 'Captcha':'Enter CAPTCHA', 'Register':'Sign Up'}, 
    #         # #             merge_username_email=True, password_hint=False)
    #         # #         if user_email: 
    #         # #             st.success('Account created successfully.')
    #         # #     except Exception as e:
    #         # #         st.error(e)
    #         # # if st.button("Log In"):
    #         # #     try:
    #         # #         authenticator.login()
    #         # #         user_email = st.session_state.get("username")
    #         # #         user_name = st.session_state.get("name")
    #         # #         if st.session_state.get('authentication_status') == True:
    #         # #             log_on()
    #         # #         elif st.session_state.get('authentication_status') is False:
    #         # #             st.error('Username/password is incorrect')
    #         # #         elif st.session_state.get('authentication_status') is None:
    #         # #             st.warning('Please enter your username and password')
    #         # #         # if st.button("Forgot Password"):
    #         # #         #     try:
    #         # #         #         username_of_forgotten_password, \
    #         # #         #         email_of_forgotten_password, \
    #         # #         #         new_random_password = authenticator.forgot_password()
    #         # #         #         if username_of_forgotten_password:
    #         # #         #             st.success('A new password will be sent securely.')
    #         # #         #             # To securely transfer the new password to the user please see step 8.
    #         # #         #         elif username_of_forgotten_password == False:
    #         # #         #             st.error('Username not found')
    #         # #         #     except Exception as e:
    #         # #         #         st.error(e)
    #         # #     except Exception as e:
    #         # #         st.error(e)





