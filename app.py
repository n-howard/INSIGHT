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
from streamlit_cookies_manager import EncryptedCookieManager
import json



# Initialize cookies
if "cookies" not in st.session_state:
    cookies = EncryptedCookieManager(prefix="myapp_", password=st.secrets.COOKIE_SECRET)
    if not cookies.ready():
        st.stop()
    st.session_state["cookies"] = cookies
else:
    cookies = st.session_state["cookies"]

if "page_redirect" in st.session_state:
    target = st.session_state["page_redirect"]
    del st.session_state["page_redirect"]
    st.switch_page(target)




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

query_params = st.query_params
query_params = st.query_params
# if st.query_params.get("code") and "google_token" not in st.session_state:
#     code = query_params["code"]
#     token = fetch_token(code)
#     if token:
#         st.session_state.google_token = token
#         st.session_state.user_info = get_user_info(token)
#     else:
#         st.error("Login failed.")
#         st.stop()

# --- Step 1: Ask to sign in ---

# if not st.experimental_user.is_logged_in:
#     if st.button("Log In"):
#         st.login("auth0")

# st.json(st.experimental_user)


# if "google_token" not in st.session_state:
#     login()
#     st.stop()
query_params = st.query_params
code = query_params.get("code")
state = query_params.get("state")



if "auth0_token" not in st.session_state:
    if code:
        if state:
            st.session_state["oauth_state"] = state
        token = fetch_token(code)
        if token:
            st.session_state["auth0_token"] = token
            st.session_state["user_info"] = get_user_info(token)
        else:
            st.error("Login failed. Please try again.")
            login()
            st.stop()
    else:
        login()
        st.stop()


# else:
#     st.html("""
#     <style>
#     @import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');
#     html, body, [class*="css"]  {
#         font-family: 'Poppins', sans-serif;
#     }
#     </style>"""
#     "<h1 style='text-align: center; font-size: 65px; font-weight: 900; font-family: Poppins; margin-bottom: 0px'>INSIGHT</h1>"
#     )

user_info = st.session_state.get("user_info", {})
user_email = user_info.get("email", "").strip().lower()
user_name = user_info.get("name", "").strip()


scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# Convert secrets section to JSON string and parse it
service_account_info = dict(st.secrets["gcp_service_account"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)

# After successful Google login
user_info = st.session_state.get("user_info", {})
user_email = user_info.get("email", "").strip().lower()
user_name = user_info.get("name", "").strip()

# Load authorized users
user_sheet = client.open("All Contacts (Arlo + Salesforce)_6.17.25").worksheet("Sheet1")
user_records = user_sheet.get_all_records()

# Match user by email
user_match = next((u for u in user_records if u["Email"].strip().lower() == user_email), None)



user_in = bool(user_match)
# --- If user not found: allow account creation ---
if not user_in:
    st.warning("We couldn't find your email in the system. Please enter your information to create an account.")
    first_name = st.text_input("Your first name")
    last_name = st.text_input("Your last name")
    role_input = st.text_input("Your role or title (e.g., Program Manager, Principal, Staff, etc.)")
    curr_org_input = st.text_input("Your organization name")
    name_input = first_name + " " + last_name
    if st.button("Create Account") and role_input:
        st.session_state["name_input"] = name_input.strip()
        st.session_state["role"] = role_input.strip()

        creating_new_org = curr_org_input.lower() not in [r["Organization"].strip().lower() for r in user_records if "Organization" in r]

        admin_approved = "True" if creating_new_org else "False"

        oregonask_access = "False"

        user_sheet.append_row(["INSIGHT", first_name, last_name, role_input, curr_org_input, user_email, "", "", admin_approved, "FALSE"])

        st.session_state["is_admin"] = admin_approved == "True"
        cookies["admin_input"] = admin_approved
        cookies.save()



        st.success("Account created successfully!")
        user_in = True
        st.rerun()
        # Force initialize once

if user_in:
    org_input = None
        # Auto-fill org info

    # --- If user is found ---
    role = user_match["Title"]
    st.session_state["role"] = role
    st.session_state["name"] = user_match.get("Name", user_name)
    st.info(f"Welcome, **{st.session_state['name']}**! Your title: **{role}**")

    # --- Define admin roles by substrings ---
    # admin_keywords = ["director", "president", "principal", "ceo", "admin", "manager", "coordinator", "leader", "owner", "superintendent", "directora", "chief", "mayor", "chair", "founder", "oregonask intern"]

    # Simple role check
    def is_admin_role(role):
        return any(keyword in role.lower() for keyword in admin_keywords)

    # Flag admin access
    # st.session_state["is_admin"] = is_admin_role(st.session_state.get("role", ""))

    # Pull the user's row by email
    user_match = next((u for u in user_records if u["Email"].strip().lower() == user_email), None)

    user_org = user_match.get("Organization", "").strip().lower()
    oregonask_access = user_match.get("OregonASK Access", "").strip().lower() == "true"
    st.session_state["access"] = oregonask_access
    cookies["access_level"] = str(oregonask_access)
    if user_match and user_org!="" and not st.session_state.get("org_input"):
        admin_approved = user_match.get("Admin Approved", "").strip().lower() == "true"
        st.session_state["is_admin"] = admin_approved
        cookies["admin_input"] = str(admin_approved)



        if st.session_state["is_admin"]:
            st.success("You have admin-level access.")
        else:
            st.info("You have standard access.")
            # Automatically log in
        user_org = user_match.get("Organization", "").strip()
        site_input = ""

        st.session_state["org_input"] = user_org
        st.session_state["site_input"] = site_input

        cookies["org_input"] = user_org
        cookies["site_input"] = site_input

        cookies.save()

        st.success(f"Signed in automatically to: {user_org}")

        st.switch_page("pages/home.py")
    else:
        admin_approved = "False"
        st.session_state["is_admin"] = admin_approved
        cookies["admin_input"] = str(admin_approved)


    @st.cache_data(ttl=3600, show_spinner=False)
    def get_org_names():
        sheet = client.open("All Programs Statewide_6.17.25").worksheet("All Programs Statewide")
        records = sheet.get_all_records(head=9)
        org_names = list({row["Account Name"].strip() for row in records if row.get("Account Name")})
        return org_names

    # Now outside the function: enrich with current user's org if missing
    org_names = get_org_names()
    if user_match:
        user_org = user_match.get("Organization", "").strip()
        if user_org and user_org.lower() not in [org.strip().lower() for org in org_names]:
            org_names.append(user_org)

    org_names = sorted(org_names)
    org_names.insert(0, "Search for your organization name...")
    org_names.append("Other")



    # # Load orgs from cache
    # org_names = get_org_names()
    

    def search_orgs(query: str):
        return [org for org in org_names if query.lower() in org.lower()]

    org_search = st.selectbox(
        "Search for your organization",
        options=org_names,
    )

    
    if org_search == "Other":
        custom_org = st.text_input("Please enter your organization name:")
        address = st.text_input("Please enter your site's address:")
        org_input = custom_org.strip()
    elif org_search != "Search for your organization name...":
        user_org = user_match.get("Organization", "").strip().lower()
        selected_org = org_search.strip().lower()
        normalized_orgs = [org.strip().lower() for org in org_names]
        org_input = org_search
        # else:
        #     st.warning("The organization you selected does not match the organization in our system. Please try again.")
        #     org_input = False
    else:
        st.info("Please select the name of the organization you work for.")

  # --- Site input (optional) ---
    site_input = st.text_input("If your organization has multiple sites, please enter your site name (optional):")

    # # --- Continue button ---
    # if st.button("Continue"):
    #     if not org_input:
    #         st.warning("Please select a valid organization before continuing.")
    #     else:
    #         # Save inputs
    #         st.session_state["org_input"] = org_input.strip()
    #         st.session_state["site_input"] = site_input.strip() if site_input else ""
    #         st.session_state["admin_input"] = "false"
    #         st.session_state["access_level"] = str(st.session_state["access"])

    #         # Save cookies
    #         cookies["org_input"] = st.session_state["org_input"]
    #         cookies["site_input"] = st.session_state["site_input"]
    #         cookies["admin_input"] = st.session_state["admin_input"]
    #         cookies["access_level"] = st.session_state["access_level"]
    #         cookies.save()


    #         # Write to sheet only if 'Other'
    #         if org_search == "Other":
    #             def append_clean_row(sheet, values):
    #                 col_a = sheet.col_values(1)
    #                 next_empty_row = len(col_a) + 1
    #                 sheet.update(f"A{next_empty_row}", [values], value_input_option='USER_ENTERED')

    #             append_clean_row(
    #                 sheet,
    #                 ["Active", "", "INSIGHT", custom_org, st.session_state["site_input"], address]
    #             )
    #             st.cache_data.clear()

    #         # Immediately redirect to home.py
    #         st.switch_page("pages/home.py")
    #         st.experimental_rerun()
    
    if st.button("Continue"):
        if not org_input:
            st.warning("Please select a valid organization before continuing.")
        else:
            # Save inputs
            st.session_state["org_input"] = org_input.strip()
            st.session_state["site_input"] = site_input.strip() if site_input else ""
            st.session_state["admin_input"] = str(st.session_state["is_admin"])
            st.session_state["access_level"] = str(st.session_state["access"])

            # Save cookies
            cookies["org_input"] = st.session_state["org_input"]
            cookies["site_input"] = st.session_state["site_input"]
            cookies["admin_input"] = st.session_state["admin_input"]
            cookies["access_level"] = st.session_state["access_level"]
            cookies.save()

            # Only write to sheet if 'Other'
            if org_search == "Other":
                def append_clean_row(sheet, values):
                    col_a = sheet.col_values(1)
                    next_empty_row = len(col_a) + 1
                    sheet.update(f"A{next_empty_row}", [values], value_input_option='USER_ENTERED')

                append_clean_row(
                    sheet,
                    ["Active", "", "INSIGHT", custom_org, st.session_state["site_input"], address]
                )
                st.cache_data.clear()

            st.session_state["page_redirect"] = "pages/home.py"
            st.rerun() # Trigger rerun so the top of script handles the redirect



