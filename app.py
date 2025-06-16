import streamlit as st 
st.set_page_config(page_title="INSIGHT", layout="wide", page_icon="./oask_short_logo.png", initial_sidebar_state="collapsed")
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from urllib.parse import urlparse, parse_qs, urlencode
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
from pages.google_auth import login, fetch_token, get_user_info
from pages.menu import menu_with_redirect


st.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }
    </style>"""
    "<h1 style='text-align: center; font-size: 65px; font-weight: 900; font-family: Poppins; margin-bottom: 0px'>INSIGHT</h1>"
)
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

query_params = st.query_params
if "code" in query_params and "google_token" not in st.session_state:
    code = query_params["code"]
    token = fetch_token(code)
    if token:
        st.session_state.google_token = token
        st.session_state.user_info = get_user_info(token)
    else:
        st.error("Login failed.")
        st.stop()

# --- Step 1: Ask to sign in ---
if "google_token" not in st.session_state:
    login()
    st.stop()

# --- Step 2: Ask for org info if not present ---
if "org_input" not in st.session_state:
    st.subheader("Enter Your Organization Information")
    org_input = st.text_input("Please enter your organization name.")
    site_input = st.text_input("If your organization has multiple sites, please enter your site name.")
    admin_input = st.text_input("If you are a program administrator, please enter your admin number.")

    if st.button("Continue") and org_input:
        st.session_state["org_input"] = org_input.strip()
        st.session_state["site_input"] = site_input.strip()
        st.session_state["admin_input"] = admin_input.strip()
        st.success("Organization information saved!")
        st.switch_page("pages/home.py")

# --- Step 3: Already signed in and org saved ---
else:
    st.markdown(f"Please enter your organization name. **{st.session_state['org_input']}**")
    st.markdown(f"If your organization has multiple sites, please enter your site name. **{st.session_state['site_input']}**")
    st.markdown(f"If you are a program administrator, please enter your admin number. **{st.session_state['admin_input']}**")
    st.page_link("pages/home.py", label="Go to Dashboard")
