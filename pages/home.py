import streamlit as st
import streamlit.components.v1 as components
from urllib.parse import unquote
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.graph_objects as go
import io
from streamlit_cookies_manager import EncryptedCookieManager
import random
import uuid
import re

st.set_page_config(page_title="INSIGHT", page_icon="./oask_short_logo.png", layout="wide")
# st.logo("./oask_light_mode_tagline_2.png", size="large", link="https://oregonask.org/")
# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.html(hide_st_style)

cookies = EncryptedCookieManager(prefix="myapp_", password=st.secrets.COOKIE_SECRET)
if not cookies.ready():
    st.stop()

# --- Restore session state from cookies if missing ---
for key in ["org_input", "site_input", "admin_input", "access_level", "user_email"]:
    if not st.session_state.get(key):
        cookie_val = cookies.get(key)
        if cookie_val:  # only restore if cookie has value
            st.session_state[key] = cookie_val

# Derived values
st.session_state["is_admin"] = str(st.session_state.get("admin_input", "")).strip().lower() == "true"
st.session_state["access"] = str(st.session_state.get("access_level", "")).strip().lower() == "true"

# # Restore from cookies if needed
# if "org_input" not in st.session_state:
#     cookie_org = cookies.get("org_input")
#     cookie_site = cookies.get("site_input")
#     cookie_admin = cookies.get("admin_input")
#     cookie_access = cookies.get("access_level")
#     email = cookies.get("user_email")

#     if cookie_org:
#         st.session_state["org_input"] = cookie_org
#         st.session_state["site_input"] = cookie_site or ""
#         st.session_state["admin_input"] = cookie_admin or ""
#         st.session_state["access_level"] = cookie_access or ""
#         st.session_state["user_email"] = email or ""
# Always restore session state from cookies if the session is fresh or values are missing
cookie_org = cookies.get("org_input", "")
cookie_site = cookies.get("site_input", "")
cookie_admin = cookies.get("admin_input", "")
cookie_access = cookies.get("access_level", "")
cookie_email = cookies.get("user_email", "")

# Restore if missing or empty in session_state
if not st.session_state.get("org_input"):
    st.session_state["org_input"] = cookie_org
if not st.session_state.get("site_input"):
    st.session_state["site_input"] = cookie_site
if not st.session_state.get("admin_input"):
    st.session_state["admin_input"] = cookie_admin
if not st.session_state.get("access_level"):
    st.session_state["access_level"] = cookie_access
if not st.session_state.get("user_email"):
    st.session_state["user_email"] = cookie_email

# Derived roles
st.session_state["is_admin"] = str(st.session_state.get("admin_input", "")).strip().lower() == "true"
st.session_state["access"] = str(st.session_state.get("access_level", "")).strip().lower() == "true"

if not st.session_state.get("org_input"):
    st.warning("Loading session...")
    st.stop()






if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = cookies.get("admin_input", "").strip().lower() == "true"

if "access" not in st.session_state:
    st.session_state["access"] = cookies.get("access_level", "").strip().lower() == "true"

access_level = st.session_state["access"]

is_admin = st.session_state["is_admin"]

if st.session_state["is_admin"]:
    ad = "Admin"
else:
    ad = "Staff"

if st.query_params.get("logout") == "1":
    for key in ["org_input", "site_input", "admin_input", "google_token", "user_info", "access_level"]:
        st.session_state.pop(key, None)

    cookies["org_input"] = ""
    cookies["site_input"] = ""
    cookies["admin_input"] = ""
    cookies["access_level"] = ""
    cookies.save()


    st.success("You have been logged out.")
    st.switch_page("app.py")
# --- LOGOUT BUTTON ---


NAVBAR_HTML = """

<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700;900&display=swap');

html, body, [class*="css"] {{
    font-family: 'Poppins', sans-serif !important;
}}

.navbar{{
display: flex;
    justify-content: center;
    # padding: 20px 40px;
    font-size: 18px;
    flex-wrap: nowrap;
    
}}

# .navbar (max-width: 740px){{
# display: flex;
# flex-direction: column;
# }}
.navbar a {{
    margin-left: 30px;
    color: black;
    text-decoration: none;
}}
.navbar a.active {{
    color: #084C61;
    font-weight: bold;
        }}


</style>

<div class="navbar">
  <a href="?page=home" class="{home_class}">Home</a>
  <a href="?page=self-assess" class="{self_class}">Self-Assess</a>
  <a href="?page=view-results" class="{results_class}">View Results</a>
</div>
"""
st.html("""<style>
    /* ───── Remove header & padding on top ───── */
    [data-testid="stHeader"] {display: none;}
    [data-testid="stMainBlockContainer"] {padding-top: 1rem;}
    
    /* ───── Hide overflowing navbar columns ───── */
    .st-emotion-cache-ocqkz7.eiemyj0 { /* Target navbar container */
        height: 35px; /* Adjust height for logo size */
        overflow: hidden;
    }
    
    
    /* ───── Move sidebar toggle to the right and replace SVG ───── */
    [data-testid="stSidebarCollapsedControl"] {
        position: fixed;
        right: 3rem;
    }
    [data-testid="stSidebarCollapsedControl"] svg {
        display: none;
    }
    
    [data-testid="stSidebarCollapsedControl"]::before {
        content: "☰"; /* Hamburger menu icon */
        font-size: 24px;
        position: fixed;
        right: 3rem;
    }
    
    
    /* ───── Display sidebar button based on screen size ───── */
    @media (min-width: 640px) {
        [data-testid="stSidebarCollapsedControl"] {
            display: none;
        }
    }
    
    @media (max-width: 639px) {
        [data-testid="stSidebarCollapsedControl"] {
            display: flex;
            justify-content: flex-end;  /* Align hamburger icon right */
        }
    }
    </style>""")

st.html("""
<style>
iframe {
    margin: 0 !important;
    padding: 0 !important;
    display: block;
}
</style>
""")

# Check current page
page = st.query_params.get("page", "home")
active_page = page.lower()
navbar = NAVBAR_HTML.format(
    home_class="active" if active_page == "home" else "",
    self_class="active" if active_page == "self-assess" else "",
    results_class="active" if active_page == "view-results" else "",
)
# st.html(navbar)
logout_container = st.container()
col1, _, col2 = st.columns([3,5, 2])
NAVBAR_HTML = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700;900&display=swap');

html, body, [class*="css"] {{
    font-family: 'Poppins', sans-serif !important;
}}

.fixed-header {{
    position: fixed;
    top: 2%;
    width: 98%;
    border-radius: 20px;
    left: 1%;
    right: 1%;
    background-color: white;
    z-index: 10000;
    padding: 10px 20px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}}

.header-content {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
}}

.navbar {{
    display: flex;
    flex-wrap: wrap;
    gap: 30px;
    font-size: 18px;
    justify-content: flex-start;
}}

.navbar a {{
    color: black;
    text-decoration: none;
}}

.navbar a.active {{
    color: #084C61;
    font-weight: bold;
}}

.logout-section {{
    display: flex;
    align-items: center;
    justify-content: flex-end;
}}

.logout-button {{
    background-color: #084C61;
    color: white;
    font-weight: 600;
    font-size: .9rem;
    padding: .4rem .8rem;
    border: none;
    border-radius: 2rem;
    cursor: pointer;
    text-align: center;
    text-decoration: none;
    margin-left: 10px;
}}

.logout-button:hover {{
    background-color: #d6e3e7;
    color: #333;
}}

.org-name-display {{
    font-size: 0.9rem;
    font-weight: 600;
    color: #084c61;
}}

/* Mobile layout: center everything vertically */
@media (max-width: 640px) {{
    .header-content {{
        flex-direction: column;
        align-items: center;
        text-align: center;
    }}
    .navbar {{
        justify-content: center;
    }}
    .logout-section {{
        justify-content: center;
        margin-top: 10px;
    }}
}}
</style>

<div class="fixed-header">
    <div class="header-content">
        <div class="navbar">
            <a href="?page=home" class="{ 'active' if active_page == 'home' else '' }">Home</a>
            <a href="?page=self-assess" class="{ 'active' if active_page == 'self-assess' else '' }">Self-Assess</a>
            <a href="?page=view-results" class="{ 'active' if active_page == 'view-results' else '' }">View Results</a>
        </div>
        <div class="logout-section">
            <div class="org-name-display">{st.session_state.get("org_input", "Organization")} {ad}</div>
            <a href="?logout=1" class="logout-button">Log Out</a>
        </div>
    </div>
</div>
"""

# Add top padding so content isn't hidden
st.markdown("<div style='height: 90px;'></div>", unsafe_allow_html=True)
st.html(NAVBAR_HTML)

# with logout_container:
#     with col1:
#         st.html(navbar)
#     with col2:
#         st.html(f"""
#             <style>
#                 .logout-button-container {{
#                     display: flex;
#                     flex-direction: row;
#                     justify-content: center;
#                     margin-left: 30px;
#                     align-items: center;
#                 }}
#                 .org-name-display {{
#                     font-size: 0.9rem;
#                     font-weight: 600;
#                     color: #084c61;
#                     margin-right: .6rem;

#                 }}
#                 .logout-button {{
#                     background-color: #084C61;
#                     color: white;
#                     font-weight: 600;
#                     font-size: .9rem;
#                     padding: .6rem .8rem;
#                     border: none;
#                     border-radius: 2rem;
#                     cursor: pointer;
#                     margin-right: 2px;
#                     transition: background-color 0.2s;
#                     text-align: center;
#                     text-decoration: none;
#                     width: fit-content;
#                 }}
#                 .logout-button:hover{{
#                     background-color: #d6e3e7;
#                     color: #333;
#                 }}
#                 .logout-button:active{{
#                     background-color: #d6e3e7;
#                     color: #333;
#                 }}

#             </style>
#             <div class="logout-button-container">
#                 <div class="org-name-display"> {st.session_state.get("org_input", "Organization")} {ad}  </div>
#                 <a href="?logout=1" class="logout-button">Log Out</a>
#             </div>
#         """)

        

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700;900&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# NAVBAR_HTML = """

# <style>
# @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700;900&display=swap');

# html, body, [class*="css"] {{
#     font-family: 'Poppins', sans-serif !important;
# }}

# .navbar (min-width: 740px){{
# display: flex;
#     justify-content: flex-end;
#     padding: 20px 40px;
#     font-size: 18px;
#     flex-wrap: wrap;
# }}

# .navbar (max-width: 740px){{
# display: flex;
# flex-direction: column;
# }}
# .navbar a {{
#     margin-left: 30px;
#     color: black;
#     text-decoration: none;
# }}
# .navbar a.active {{
#     color: #084C61;
#     font-weight: bold;
#         }}
# </style>

# <div class="navbar">
#   <a href="?page=home" class="{home_class}">Home</a>
#   <a href="?page=self-assess" class="{self_class}">Self-Assess</a>
#   <a href="?page=view-results" class="{results_class}">View Results</a>
# </div>
# """
# st.html("""<style>
#     /* ───── Remove header & padding on top ───── */
#     [data-testid="stHeader"] {display: none;}
#     [data-testid="stMainBlockContainer"] {padding-top: 1rem;}
    
#     /* ───── Hide overflowing navbar columns ───── */
#     .st-emotion-cache-ocqkz7.eiemyj0 { /* Target navbar container */
#         height: 35px; /* Adjust height for logo size */
#         overflow: hidden;
#     }
    
    
#     /* ───── Move sidebar toggle to the right and replace SVG ───── */
#     [data-testid="stSidebarCollapsedControl"] {
#         position: fixed;
#         right: 3rem;
#     }
#     [data-testid="stSidebarCollapsedControl"] svg {
#         display: none;
#     }
    
#     [data-testid="stSidebarCollapsedControl"]::before {
#         content: "☰"; /* Hamburger menu icon */
#         font-size: 24px;
#         position: fixed;
#         right: 3rem;
#     }
    
    
#     /* ───── Display sidebar button based on screen size ───── */
#     @media (min-width: 640px) {
#         [data-testid="stSidebarCollapsedControl"] {
#             display: none;
#         }
#     }
    
#     @media (max-width: 639px) {
#         [data-testid="stSidebarCollapsedControl"] {
#             display: flex;
#             justify-content: flex-end;  /* Align hamburger icon right */
#         }
#     }
#     </style>""")

# st.html("""
# <style>
# iframe {
#     margin: 0 !important;
#     padding: 0 !important;
#     display: block;
# }
# </style>
# """)

# # Check current page
# page = st.query_params.get("page", "home")
# active_page = page.lower()
# navbar = NAVBAR_HTML.format(
#     home_class="active" if active_page == "home" else "",
#     self_class="active" if active_page == "self-assess" else "",
#     results_class="active" if active_page == "view-results" else "",
# )
# st.html(navbar)
     
ASSESSMENTS = {
    "Environment, Health, and Safety": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLScTWIWH3ucfkk2Ud4Dsv5JGFst3kFxQvOMVp4aYXwyhrppPCg/viewform?embedded=true",
        "sheet_name": "Environment, Health, and Safety (Responses)"
    },
    "Highly Skilled Personnel": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSfCs3lUrb2hEB92aZn33ledpwKNXtDOuPjd1hw40p-ZW-Y0JA/viewform?embedded=true",
        "sheet_name": "Highly Skilled Personnel (Responses)"
    },
    "Program Management": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSfiFsaUqThoawBo-vTQLp5vPslFV-4A_efQw9PBwd3QRiHSIA/viewform?embedded=true",
        "sheet_name": "Program Management (Responses)"
    },
    "Youth Development and Engagement": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSfvrLHuw7dqBQ5gN-i3rjNA-fusFxd96Hl4hsrC1MwKofBP9A/viewform?embedded=true",
        "sheet_name": "Youth Development and Engagement (Responses)"
    },
    "Programming and Activities": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSejk08smadc3IPkfoOYk9P8Hdj4JcS8UEfnh1bUXwAPUEpPDw/viewform?embedded=true",
        "sheet_name": "Programming and Activities (Responses)"
    },
    "Families, Schools, and Communities": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSf2jg-yPBIGx9w2Zhl1aX3SQGcASQIDMTBizMJ4v4zurNTF-w/viewform?embedded=true",
        "sheet_name": "Families, Schools, and Communities (Responses)"
    },
}

if page == "self-assess":
#     st.html("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700;900&display=swap');

# html, body, [class*="css"] {
#     font-family: 'Poppins', sans-serif !important;
# }

# .landing-container {
#     padding: 3rem 4rem;
#     display: flex;
#     flex-direction: column;
#     align-items: flex-start;
#     position: relative;
# }

# .landing-title {
#     font-size: 48px;
#     font-weight: 800;
#     color: #084C61;
#     line-height: 1.1;
# }

# .landing-subtitle {
#     margin-top: 0.5rem;
#     font-size: 18px;
# }

# .button-grid {
#     display: grid;
#     grid-template-columns: repeat(3, minmax(30%, 1fr));
#     gap: 1.2rem;
#     margin-top: 2.5rem;
#     z-index: 1;
#     max-width: 100%;
#     width: 100%;
# }

# @media (max-width: 768px) {
#     .button-grid {
#         grid-template-columns: 1fr;
#     }

#     .landing-title {
#         font-size: 36px;
#         text-align: center;
#     }

#     .landing-subtitle {
#         text-align: center;
#     }

#     .landing-container {
#         align-items: center;
#         text-align: center;
#         padding: 2rem;
#     }
# }



# .custom-button {
#     background-color: #084C61;
#     color: white;
#     font-weight: 600;
#     font-size: .9rem;
#     padding: 1rem 2rem;
#     border: none;
#     border-radius: 2rem;
#     cursor: pointer;
#     margin-right: 2px;
#     transition: background-color 0.2s;
#     text-align: center;
#     text-decoration: none;
#     min-width: 33.33%;
#     max-width: 100%;
# }


# .custom-button:hover {
#     background-color: #0d7084;
# }


# .faded-bg {
#     position: absolute;
#     right: 0;
#     top: 0;
#     opacity: 0.08;
#     max-width: 100%;
#     z-index: 0;
# }

# @media (max-width: 768px) {
#     .landing-title {
#         font-size: 36px;
#         text-align: center;
#     }
#     .landing-subtitle {
#         text-align: center;
#     }
#     .landing-container {
#         align-items: center;
#         text-align: center;
#         padding: 2rem;
#     }
# }
# </style>

# <div class="landing-container">

#     <h1 class="landing-title">Self-<br>Assessment</h1>
#     <p class="landing-subtitle">Assess your organization.</p>

#     <div class="button-grid">
#         <a class="custom-button" href="?page=self-assess&variation=Youth+Development+and+Engagement">Youth Development and Engagement</a>
#         <a class="custom-button" href="?page=self-assess&variation=Environment,+Health,+and+Safety">Environment, Health, and Safety</a>
#         <a class="custom-button" href="?page=self-assess&variation=Families,+Schools,+and+Communities">Families, Schools, and Communities</a>
#         <a class="custom-button" href="?page=self-assess&variation=Highly+Skilled+Personnel">Highly Skilled Personnel</a>
#         <a class="custom-button" href="?page=self-assess&variation=Programming+and+Activities">Programming and Activities</a>
#         <a class="custom-button" href="?page=self-assess&variation=Program+Management">Program Management</a>

#     </div>

#     <img src="https://i.imgur.com/8Q3M2NU.png" class="faded-bg" alt="Background Illustration"/>
# </div>
#     """)

    if "variation" not in st.query_params:
        active_variation = ""
    else:
        active_variation = st.query_params["variation"]

    # Define all your categories
    categories = [
        "Youth Development and Engagement",
        "Environment, Health, and Safety",
        "Families, Schools, and Communities",
        "Highly Skilled Personnel",
        "Programming and Activities",
        "Program Management"
    ]

    # Create HTML for buttons
    button_html = ""
    for cat in categories:
        href = f"?page=self-assess&variation={cat.replace(' ', '+').replace(',', '%2C')}"
        if cat == active_variation:
            class_name = "custom-button active"
        else:
            class_name = "custom-button inactive"
        button_html += f'<a class="{class_name}" href="{href}">{cat}</a>\n'

    # Final HTML
    st.html(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700;900&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif !important;
    }}

    .landing-container {{
        padding: 3rem 4rem;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        position: relative;
    }}

    .landing-title {{
        font-size: 48px;
        font-weight: 800;
        color: #084C61;
        line-height: 1.1;
    }}

    .landing-subtitle {{
        margin-top: 0.5rem;
        font-size: 18px;
    }}

    .button-grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(30%, 1fr));
        gap: 1.2rem;
        margin-top: 2.5rem;
        z-index: 1;
        max-width: 100%;
        width: 100%;
    }}

    .custom-button {{
        font-weight: 600;
        font-size: .9rem;
        padding: 1rem 2rem;
        border: none;
        border-radius: 2rem;
        cursor: pointer;
        text-align: center;
        text-decoration: none;
        min-width: 33.33%;
        max-width: 100%;
        transition: background-color 0.2s;
    }}

    .custom-button.active {{
        background-color: #084C61;
        color: white;
    }}

    .custom-button.inactive {{
        background-color: #d6e3e7;
        color: #333;
    }}

    .custom-button.inactive:hover {{
        background-color: #b6d2da;
    }}

    .faded-bg {{
        position: absolute;
        right: 0;
        top: 0;
        opacity: 0.08;
        max-width: 100%;
        z-index: 0;
    }}

    @media (max-width: 768px) {{
        .button-grid {{
            grid-template-columns: 1fr;
        }}
        .landing-title {{
            font-size: 36px;
            text-align: center;
        }}
        .landing-subtitle {{
            text-align: center;
        }}
        .landing-container {{
            align-items: center;
            text-align: center;
            padding: 2rem;
        }}
    }}
    </style>

    <div class="landing-container">
        <h1 class="landing-title">Self-<br>Assessment</h1>
        <p class="landing-subtitle">Assess your organization.</p>

        <div class="button-grid">
            {button_html}
        </div>

        <img src="https://i.imgur.com/8Q3M2NU.png" class="faded-bg" alt="Background Illustration"/>
    </div>
    """)

    query_params = st.query_params

    if "variation" in query_params:
        # Set to session state (decode + replace + capitalize if needed)
        st.session_state["variation"] = unquote(query_params["variation"])

    # Default fallback or message
    assessment = st.session_state.get("variation", None)
    if assessment:
        selfSes = assessment + " Self-Assessment"
        thisStyle = f"""<h3 style='text-align: center; font-size: 35px; font-weight: 600; font-family: Poppins;'>{selfSes}</h3>"""
        st.html(
            thisStyle
        )
        components.iframe(ASSESSMENTS[assessment]["form_url"], height=800, scrolling=True)



elif page == "view-results":
    if not st.session_state.get("org_input"):
        st.session_state["org_input"] = cookies.get("org_input", "")
    # Access the value stored in session state
    org_input = st.session_state.get("org_input", "")
    st.session_state.admin_input = cookies.get("admin_level")
    admin_input = st.session_state.get("admin_input", "")
    st.session_state.access_level = cookies.get("access_level")
    access_level = st.session_state.get("access_level", "")
#     st.html("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700;900&display=swap');

# html, body, [class*="css"] {
#     font-family: 'Poppins', sans-serif !important;
# }

# .landing-container {
#     padding: 3rem 4rem;
#     display: flex;
#     flex-direction: column;
#     align-items: flex-start;
#     position: relative;
# }

# .landing-title {
#     font-size: 48px;
#     font-weight: 800;
#     color: #084C61;
#     line-height: 1.1;
# }

# .landing-subtitle {
#     margin-top: 0.5rem;
#     font-size: 18px;
# }

# .button-grid {
#     display: grid;
#     grid-template-columns: repeat(3, minmax(30%, 1fr));
#     gap: 1.2rem;
#     margin-top: 2.5rem;
#     z-index: 1;
#     max-width: 100%;
#     width: 100%;
# }

# @media (max-width: 768px) {
#     .button-grid {
#         grid-template-columns: 1fr;
#     }

#     .landing-title {
#         font-size: 36px;
#         text-align: center;
#     }

#     .landing-subtitle {
#         text-align: center;
#     }

#     .landing-container {
#         align-items: center;
#         text-align: center;
#         padding: 2rem;
#     }
# }



# .custom-button {
#     background-color: #084C61;
#     color: white;
#     font-weight: 600;
#     font-size: .9rem;
#     padding: 1rem 2rem;
#     border: none;
#     border-radius: 2rem;
#     cursor: pointer;
#     margin-right: 2px;
#     transition: background-color 0.2s;
#     text-align: center;
#     text-decoration: none;
#     min-width: 33.33%;
#     max-width: 100%;
# }


# .custom-button:hover {
#     background-color: #0d7084;
# }


# .faded-bg {
#     position: absolute;
#     right: 0;
#     top: 0;
#     opacity: 0.08;
#     max-width: 100%;
#     z-index: 0;
# }

# @media (max-width: 768px) {
#     .landing-title {
#         font-size: 36px;
#         text-align: center;
#     }
#     .landing-subtitle {
#         text-align: center;
#     }
#     .landing-container {
#         align-items: center;
#         text-align: center;
#         padding: 2rem;
#     }
# }
# </style>

# <div class="landing-container">

#     <h1 class="landing-title">Results<br>Dashboard</h1>
#     <p class="landing-subtitle">View results.</p>

#     <div class="button-grid">
#         <a class="custom-button" href="?page=view-results&variation=Youth+Development+and+Engagement">Youth Development and Engagement</a>
#         <a class="custom-button" href="?page=view-results&variation=Environment,+Health,+and+Safety">Environment, Health, and Safety</a>
#         <a class="custom-button" href="?page=view-results&variation=Families,+Schools,+and+Communities">Families, Schools, and Communities</a>
#         <a class="custom-button" href="?page=view-results&variation=Highly+Skilled+Personnel">Highly Skilled Personnel</a>
#         <a class="custom-button" href="?page=view-results&variation=Programming+and+Activities">Programming and Activities</a>
#         <a class="custom-button" href="?page=view-results&variation=Program+Management">Program Management</a>
#     </div>

#     <img src="https://i.imgur.com/8Q3M2NU.png" class="faded-bg" alt="Background Illustration"/>
# </div>

#     """)
    if "variation" not in st.query_params:
        active_variation = ""
    else:
        active_variation = st.query_params["variation"]

    # Define all your categories
    categories = [
        "Youth Development and Engagement",
        "Environment, Health, and Safety",
        "Families, Schools, and Communities",
        "Highly Skilled Personnel",
        "Programming and Activities",
        "Program Management"
    ]

    # Create HTML for buttons
    button_html = ""
    for cat in categories:
        href = f"?page=view-results&variation={cat.replace(' ', '+').replace(',', '%2C')}"
        if cat == active_variation:
            class_name = "custom-button active"
        else:
            class_name = "custom-button inactive"
        button_html += f'<a class="{class_name}" href="{href}">{cat}</a>\n'

    # Final HTML
    st.html(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700;900&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif !important;
    }}

    .landing-container {{
        padding: 3rem 4rem;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        position: relative;
    }}

    .landing-title {{
        font-size: 48px;
        font-weight: 800;
        color: #084C61;
        line-height: 1.1;
    }}

    .landing-subtitle {{
        margin-top: 0.5rem;
        font-size: 18px;
    }}

    .button-grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(30%, 1fr));
        gap: 1.2rem;
        margin-top: 2.5rem;
        z-index: 1;
        max-width: 100%;
        width: 100%;
    }}

    .custom-button {{
        font-weight: 600;
        font-size: .9rem;
        padding: 1rem 2rem;
        border: none;
        border-radius: 2rem;
        cursor: pointer;
        text-align: center;
        text-decoration: none;
        min-width: 33.33%;
        max-width: 100%;
        transition: background-color 0.2s;
    }}

    .custom-button.active {{
        background-color: #084C61;
        color: white;
    }}

    .custom-button.inactive {{
        background-color: #d6e3e7;
        color: #333;
    }}

    .custom-button.inactive:hover {{
        background-color: #b6d2da;
    }}

    .faded-bg {{
        position: absolute;
        right: 0;
        top: 0;
        opacity: 0.08;
        max-width: 100%;
        z-index: 0;
    }}

    @media (max-width: 768px) {{
        .button-grid {{
            grid-template-columns: 1fr;
        }}
        .landing-title {{
            font-size: 36px;
            text-align: center;
        }}
        .landing-subtitle {{
            text-align: center;
        }}
        .landing-container {{
            align-items: center;
            text-align: center;
            padding: 2rem;
        }}
    }}
    </style>

    <div class="landing-container">
        <h1 class="landing-title">Results<br>Dashboard</h1>
        <p class="landing-subtitle">View results.</p>

        <div class="button-grid">
            {button_html}
        </div>

        <img src="https://i.imgur.com/8Q3M2NU.png" class="faded-bg" alt="Background Illustration"/>
    </div>
    """)

    query_params = st.query_params

    if "variation" in query_params:
        # Set to session state (decode + replace + capitalize if needed)
        st.session_state["variation"] = unquote(query_params["variation"])
    assessment = st.session_state.get("variation", None)
    if assessment:
    #     title = assessment + " Results"
    #     thisStyle = f"""<h3 style='text-align: center; font-size: 35px; font-weight: 600; font-family: Poppins;'>{title}</h3>"""
    #     st.html(
    #         thisStyle
    #     )
                # Authorize and load the sheet
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
        client = gspread.authorize(creds)
        sheet = client.open(ASSESSMENTS[assessment]["sheet_name"]).sheet1
        org_input = cookies.get("org_input")
        org_name = cookies.get("org_input")
        if not st.session_state.get("org_input"):
            st.session_state["org_input"] = org_name
        # Access the value stored in session state
        org_input = st.session_state.get("org_input", "")
        st.session_state.admin_input = cookies.get("admin_level")
        admin_input = st.session_state.get("admin_input", "")
        st.session_state.access_level = cookies.get("access_level")
        access_level = st.session_state.get("access_level", "")


        if not org_input:
            st.warning("Please enter your organization name on the main page.")
            st.switch_page("app.py")
    
        # Load raw data and headers for the specific organization.
        raw_data = sheet.get_all_values()
        headers = raw_data[0]

        # Make headers unique to avoid duplicate error
        seen = {}
        unique_headers = []
        for h in headers:
            if h in seen:
                seen[h] += 1
                unique_headers.append(f"{h} ({seen[h]})")
            else:
                seen[h] = 0
                unique_headers.append(h)

        # Create DataFrame
        df = pd.DataFrame(raw_data[1:], columns=unique_headers)
        reg_df = df.copy()

        Program_Name = "Please enter the organization name you logged in with." 
    
        
        # --- STEP 1: Dynamically detect the "Program Name" column ---
        candidate_keywords = ["organization name", "program name", "your org", "site or organization", "Please enter the organization name you logged in with."]
        Program_Name = None

        for col in df.columns:
            col_lower = col.strip().lower()
            if any(keyword in col_lower for keyword in candidate_keywords):
                Program_Name = col
                break

        # If no matching column found, show error
        if not Program_Name:
            st.error("Could not find the column with organization/program name. Please check your form question titles.")
            st.stop()
        
        if access_level:
            org_df = df.copy()

            
            if Program_Name in org_df.columns:

                org_df["Extracted Orgs"] = org_df[Program_Name].fillna("").astype(str).str.strip()

                # Fallback: if all lists are empty, just use raw org names
                if org_df["Extracted Orgs"].apply(len).sum() == 0:
                    org_df["Extracted Orgs"] = org_df[Program_Name].apply(lambda x: [x.strip()] if x else [])


                all_orgs = sorted(set(org for org in org_df["Extracted Orgs"] if org))
                over_scores = {}
                if all_orgs:
                    # Step 1: Get all columns that include "Overall Score"
                    over_score_col = [col for col in org_df.columns if "Overall Score" in col]

                    # Step 2: Collect all numeric values from these columns
                    for org in all_orgs:
                        these_all_scores = []

                        for col in over_score_col:
                            series = pd.to_numeric(org_df[col], errors="coerce")  # convert to numbers, NaN if invalid
                            scores = series.dropna().tolist()  # drop non-numeric
                            these_all_scores.extend(scores)

                        # Step 3: Calculate the average
                        if these_all_scores:
                            over_scores[org] = sum(these_all_scores) / len(these_all_scores)
                        else:
                            over_scores[org] = 0
                else:
                    selected_orgs = []
            else:
                
                selected_orgs = []

            def matches_selected_orgs(org_list):
                return any(org in org_list for org in selected_orgs)
        
        else:
            all_orgs = False
            if Program_Name not in df.columns:
                st.error("Column Program Name not found in the data.")
                st.stop()

            # Clean both Program Name column and org_input for flexible comparison
            df["Program Name_clean"] = df[Program_Name].str.strip().str.lower()
            org_clean = org_input.strip().lower()

            # Filter the DataFrame to just this org
            df = df[df["Program Name_clean"] == org_clean]

            org_df = df.copy()

            # Drop the temporary clean column
            df = df.drop(columns=["Program Name_clean"])
            
        site_name = "Please enter the name of the site and/or program you work at."

        if site_name not in org_df.columns:
            site_keywords = ["name of the site", "site", "the site", "which site", "Please enter the name of the site and/or program you work at."]
            for col in df.columns:
                col_lower = col.strip().lower()
                if any(keyword in col_lower for keyword in site_keywords):
                    site_name = col
        # --- MULTI-FILTER CONTROLS ---
            # Normalize Site Name
            if site_name in org_df.columns:
                org_df["Site Name"] = org_df[site_name].fillna("").astype(str).str.strip()
            else:
                org_df["Site Name"] = ""  # Add a blank column if missing

            # Get site name from session (if any)
            site_input = st.session_state.get("site_input", "").strip()

            # site_column_name = next((col for col in df.columns if site_name.lower() in col.lower()), None)
            # site_column_name = df["Site Name"]

            # if site_column_name is None:
            #     site_column_name = "__NO_SITE_COL__"
            #     df[site_column_name] = ""
            def extract_sites(text):
                lines = text.split('\n')
                site_names = []
                for line in lines:
                    match = re.match(r"\s*-\s*(.*?):", line)
                    if match:
                        site_names.append(match.group(1).strip())
                return site_names 
       # --- MULTI-FILTER CONTROLS ---
        # Normalize Site Name
        if site_name in org_df.columns:
            org_df["Site Name"] = org_df[site_name].fillna("").astype(str).str.strip()
        else:
            org_df["Site Name"] = ""  # Add a blank column if missing

        # Get site name from session (if any)
        site_input = st.session_state.get("site_input", "").strip()


        # Apply to org_df only (filtered by org_input earlier)
        org_df["Extracted Sites"] = org_df["Site Name"]


        # Build site dropdown options (only if admin has sites)
        all_sites = sorted(set(site for site in org_df["Extracted Sites"] if site))

        # if (is_admin or access_level) and all_sites:
        #     # Add site filtering here? Or maybe add a site column
        # else:
        #     selected_sites = []  # No site filtering available or needed


        # # Filter to rows that contain at least one of the selected sites
        # def matches_selected_sites(site_list):
        #     return any(site in site_list for site in selected_sites)        
        selected_contacts = []
        

        # Try converting all columns to numeric
        converted_df = df.copy()
        # Apply staff and site filters to org_df before generating charts

        chart_df = org_df.copy() 

        if st.session_state.get("user_email")!="":
            email = st.session_state.get("user_email")
        else:
            email = None

        is_admin = st.session_state.get("is_admin", False)
        if is_admin:
            chart_df = org_df.copy()
        else:
            chart_df = reg_df[reg_df["Contact Email"].str.lower().str.strip() == email.strip().lower()]

        # if selected_contacts:
        #     chart_df = chart_df[chart_df["Contact Name"].isin(selected_contacts)]

        # if selected_sites:
        #     chart_df = chart_df[chart_df["Extracted Sites"].apply(matches_selected_sites)]
        # if access_level:
        #     if selected_orgs:
        #         chart_df = chart_df[chart_df["Extracted Orgs"].apply(matches_selected_orgs)]

        # Convert to numeric
        converted_df = chart_df.copy()
        for col in converted_df.columns:
            converted_df[col] = pd.to_numeric(converted_df[col], errors="coerce")

        # Keep only mostly-numeric columns
        EXCLUDED_SUBSTRINGS = ["How many students", "Timestamp", "Contact Phone", "Program Zip Code", "Program Street Address"]

        def is_numeric_column(series):
            return (
                series.notna().mean() >= 0.6 and
                series.apply(lambda x: isinstance(x, (int, float)) or (isinstance(x, str) and "," not in x)).all()
            )

        numeric_cols = [
            col for col in converted_df.columns
            if is_numeric_column(converted_df[col]) and not any(sub.lower() in col.lower() for sub in EXCLUDED_SUBSTRINGS)
        ]

        filtered_df = converted_df[numeric_cols].dropna(axis=1, how="all")



        # overall_score = 3.40
        # standard_scores = [("Standard 1", 3.40), ("Standard 2", 3.70)]
        # score_over_time = [2.1, 2.4, 2.2, 2.5, 2.8, 2.6, 2.3, 2.6, 3.0, 3.2, 3.4, 3.6]
        # submissions = {"Submission 1": 2.90, "Submission 2": 3.1231}
        # staff_scores = {"Nat Howard": 3.50, "Bob Kaplan": 3.00, "Jake Goodman": 2.10}


        if is_admin or access_level:
            staff_scores = {}
            staff_scores_num = {}
            submissions = {}
            score_over_time = []
            standard_scores = []

            # Step 1: Get all columns that include "Overall Score"
            overall_score_cols = [col for col in org_df.columns if "Overall Score" in col]

            # Step 2: Collect all numeric values from these columns
            all_scores = []

            for col in overall_score_cols:
                series = pd.to_numeric(org_df[col], errors="coerce")  # convert to numbers, NaN if invalid
                scores = series.dropna().tolist()  # drop non-numeric
                all_scores.extend(scores)

            # Step 3: Calculate the average
            if all_scores:
                overall_score = sum(all_scores) / len(all_scores)
            else:
                overall_score = 1000  # fallback value or message



            if not access_level:

                if overall_score_cols:
                    score_col = overall_score_cols[0] 
                    score_series = pd.to_numeric(org_df[score_col], errors="coerce")
                    
                    # Optional: Add label (e.g., "Submission 1", "Submission 2", or use timestamps)
                    for i, score in enumerate(score_series):
                        if not pd.isna(score):
                            label = f"Submission {i+1}"
                            submissions[label] = score
                            score_over_time.append(score)

            if "Contact Name" in org_df.columns:
                # Normalize the Contact Name column
                org_df["__normalized_contact__"] = org_df["Contact Name"].astype(str).str.strip().str.lower()

                # Get unique normalized names (original casing preserved via mapping)
                original_names = org_df.dropna(subset=["Contact Name"])["Contact Name"]
                normalized_map = {name.strip().lower(): name for name in original_names.unique()}

                contacts_to_show = list(normalized_map.keys())

                for contact_norm in contacts_to_show:
                    contact_display = normalized_map[contact_norm]
                    staff_scores[contact_display] = []

                    contact_df = org_df[org_df["__normalized_contact__"] == contact_norm]
                    if contact_df.empty:
                        continue

                    for column in contact_df.columns:
                        series = contact_df[column].replace('%', '', regex=True)
                        series = pd.to_numeric(series, errors="coerce")
                        avg = series.mean()
                        if pd.notna(avg):
                            if "Overall Score" in column:
                                staff_scores[contact_display].append((column, avg))
                                staff_scores_num[contact_display] = avg
                            elif "Standard" in column:
                                if "percent" in column.lower() or "%" in column:
                                    staff_scores[contact_display].append((column, avg))
                                elif 0 <= avg < 1:
                                    avg *= 100
                                    staff_scores[contact_display].append((column, avg))
                                else:
                                    staff_scores[contact_display].append((column, avg))
                            elif "Indicator" in column:
                                staff_scores[contact_display].append((column, avg))
                        elif "Indicator" in column:
                            staff_scores[contact_display].append((column, avg))
                    
            if not access_level:
                for column in org_df:
                    if "Overall Score" in column and (("Standard" not in column) or ("-" in column)):
                        continue

                    # Clean and convert
                    series = org_df[column].replace('%', '', regex=True)
                    series = pd.to_numeric(series, errors="coerce")
                    av = series.mean()
                    if pd.notna(av):
                        if "Standard" in column:
                            if "percent" in column.lower() or "%" in column:
                                standard_scores.append((column, av))
                            elif 0 <= av < 1:
                                av*=100
                                standard_scores.append((column, av))
                            else:
                                standard_scores.append((column, av))
                        elif "Indicator" in column:
                            standard_scores.append((column, av))


                    # elif "Indicator" in column:
                    #     standard_scores.append((column, av))
            else:
                standard_scores = {}
                over_scores = {}

                # Create a mapping from normalized org -> original org
                normalized_org_map = {}
                for org in all_orgs:
                    normalized = org.strip().lower()
                    normalized_org_map[normalized] = org  # preserve original for display

                # Normalize Extracted Orgs column in the DataFrame
                org_df["__normalized_extracted_orgs__"] = org_df["Extracted Orgs"].apply(
                    lambda x: [i.strip().lower() for i in x] if isinstance(x, list) else [str(x).strip().lower()]
                )
                
                    
                j = 0
                    
                for norm_org, display_org in normalized_org_map.items():
                    
                    # Match rows where normalized org is in normalized extracted list
                    torg_df = org_df[org_df["__normalized_extracted_orgs__"].apply(lambda x: norm_org in x)]

                    # Overall Score
                    all_scores = []
                    for col in torg_df.columns:
                        if "Overall Score" in col:
                            series = pd.to_numeric(torg_df[col], errors="coerce")
                            scores = series.dropna().tolist()
                            all_scores.extend(scores)
                    over_scores[display_org] = sum(all_scores) / len(all_scores) if all_scores else 0
                    if overall_score_cols:
                        score_col = overall_score_cols[0] 
                        score_series = pd.to_numeric(torg_df[score_col], errors="coerce")
                        for k, score in enumerate(score_series):
                            if not pd.isna(score):
                                label = f"Submission {j+1}: {display_org}"
                                submissions[label] = score
                                score_over_time.append(score)
                            j+=1
                    # Standards/Indicators
                    standard_scores[display_org] = []
                    for column in torg_df.columns:
                        if "Overall Score" in column and (("Standard" not in column) or ("-" in column)):
                            continue

                        series = torg_df[column].replace('%', '', regex=True)
                        series = pd.to_numeric(series, errors="coerce")
                        av = series.mean()

                        if pd.notna(av):
                            if "Standard" in column:
                                if "percent" in column.lower() or "%" in column:
                                    standard_scores[display_org].append((column, av))
                                elif 0 <= av < 1:
                                    standard_scores[display_org].append((column, av * 100))
                                else:
                                    standard_scores[display_org].append((column, av))
                            elif "Indicator" in column:
                                standard_scores[display_org].append((column, av))
                        elif "Indicator" in column:
                            standard_scores[display_org].append((column, av))

        else:
            standard_scores = {}
            submissions = {}
            score_over_time = []
            email = st.session_state.get("user_email", "").strip().lower()
            edf = chart_df.copy()
             # Step 1: Get all columns that include "Overall Score"
            overall_score_cols = [col for col in edf.columns if "Overall Score" in col]

            # Step 2: Collect all numeric values from these columns
            all_scores = []

            for col in overall_score_cols:
                series = pd.to_numeric(edf[col], errors="coerce")  # convert to numbers, NaN if invalid
                scores = series.dropna().tolist()  # drop non-numeric
                all_scores.extend(scores)

            # Step 3: Calculate the average
            if all_scores:
                overall_score = sum(all_scores) / len(all_scores)
            else:
                overall_score = 1000  # fallback value or message


            if overall_score_cols:
                score_col = overall_score_cols[0] 
                score_series = pd.to_numeric(edf[score_col], errors="coerce")
                
                # Optional: Add label (e.g., "Submission 1", "Submission 2", or use timestamps)
                for k, score in enumerate(score_series):
                    if not pd.isna(score):
                        label = f"Submission {k+1}"
                        submissions[label] = score
                        score_over_time.append(score)
            for column in edf.columns:
                series = edf[column].replace('%', '', regex=True)
                series = pd.to_numeric(series, errors="coerce")
                av = series.mean()

                if pd.notna(av):
                    if "Standard" in column:
                        if "percent" in column.lower() or "%" in column:
                            standard_scores[column] = av
                        elif 0 <= av < 1:
                            standard_scores[column] = av * 100
                        else:
                            standard_scores[column] = av
                    elif "Indicator" in column:
                        standard_scores[column] = av
                elif "Indicator" in column:
                    standard_scores[column] = av

        # Donut Dial Function
        def draw_score_dial(score, label="Overall Score"):
            unique_prefix = str(uuid.uuid4()) 
            fig = go.Figure(go.Pie(
                values=[score, 4 - score],
                labels=["", ""],
                marker_colors=["#FFFFFF", "#56A3A6"],
                hole=0.7,
                sort=False,
                direction='clockwise',
                textinfo='none',
                ids=[f"{unique_prefix}-score", f"{unique_prefix}-remaining"], 
            ))
            fig.update_layout(
                showlegend=False,
                margin=dict(t=20, b=20, l=0, r=0),
                annotations=[dict(
                    text=f"<b style='color:white;'>{score:.2f}</b><br><span style='font-size:13px; color:white;'>{label}</span>",
                    x=0.5, y=0.5, showarrow=False, align="center", font=dict(size=24, family="Poppins")
                )],
                height=200,
                width=200,
                paper_bgcolor="rgba(0,0,0,0)",
            )
            return fig





        def display_recommendation(indicator, sheet2_data, org_name):
                """Helper function to display a single recommendation"""
                column = indicator['name']
                
                # Find the matching row in sheet2
                for row in sheet2_data:
                    if len(row) >= 2 and row[0] == column:  # Column A matches our indicator
                        # Get the organization name and replace placeholder
                        # org_name = st.session_state.get("org_input", cookies.get("org_input"))
                        recommendation = row[1].replace("{YOUR PROGRAM NAME}", org_name)
                        name_op = column.replace("Score","")
                        if "Standard" in name_op:
                            l = name_op.split(" ")
                            new = []
                            for i in range(len(l)):
                                if "Indicator" in l[i]:
                                    new = l[i:]

                            name_new = ""
                            for k in range(len(new)-1):
                                name_new+=new[k] + " "
                            name_new+=new[len(new)-1]
                            if name_new!="":
                                name_new = name_new.replace("(", "")
                                name_new = name_new.replace(")", "") 
                                name_op = name_new
                        st.write(f"**{name_op} INSIGHT:** {recommendation}")
                        break

        def display(column, sheet2_data, org_name):
            for row in sheet2_data:
                if len(row) >= 2 and row[0] == column:
                    recommendation = row[1].replace("{YOUR PROGRAM NAME}", org_name)
                    name_op = column.replace("Score","")
                    st.write(f"**{name_op} INSIGHT:** {recommendation}")
                    break

        def recs():
            # Open the spreadsheet and get the "Recommendations" worksheet
            spreadsheet = client.open(ASSESSMENTS[assessment]["sheet_name"])
            recs_sheet = spreadsheet.worksheet("Recommendations")
            
            # Get all data from sheet2 as a list of lists
            sheet2_data = recs_sheet.get_all_values()
            
            # First, identify all low indicators
            low_indicators = []
            
            for column in org_df:
                series = org_df[column].replace('%', '', regex=True)
                series = pd.to_numeric(series, errors="coerce")
                av = series.mean()
                
                # if pd.notna(av):
                #     if "Indicator" in column:
                #         if av < 3:
                #             low_indicators.append({"name": column, "average": av, "name_op": column.replace("Score",""), "per":""})
                #         elif "Percent" in column:
                #             if av < 75:
                #                 low_indicators.append({"name": column, "average": av, "name_op": column.replace("Score",""), "per":"%"})
                if pd.notna(av):
                    if "Indicator" in column:
                        low_indicators.append({"name": column, "average": av, "name_op": column.replace("Score",""), "per":""})
                
            
            if not low_indicators:
                return None, sheet2_data
            return low_indicators, sheet2_data
        
            
        
            
        low_indicators, sheet2_data = recs()

        def desc(sheet_data, label):
            data_rows = sheet3_data[1:]

            # Create a mapping from Column A to Column B
            col_a_to_b = {row[0]: row[1] for row in data_rows if len(row) >= 2 and row[0]}
            defst = ""
            l = list(col_a_to_b.keys())
            
            for category in l:
                if category in label:
                    tdef = col_a_to_b[category]
                    defst+= f"""**{category}**: {tdef} \n\n"""
            st.write(defst)

        # Render one unified score card
        def render_score_card(sheet3_data, sheet2_data, score: float, label: str = "Overall Score", max_score: float = 4.0, org_name: str = st.session_state.get("org_input")):
            # spreadsheet = client.open(ASSESSMENTS[assessment]["sheet_name"])
            # cat_sheet = spreadsheet.worksheet("Indicators")
            # sheet3_data = cat_sheet.get_all_values()

            # Extract data (skip header row)
            data_rows = sheet3_data[1:]

            # Create a mapping from Column A to Column B
            col_a_to_b = {row[0]: row[1] for row in data_rows if len(row) >= 2 and row[0]}
            defst = ""
            l = list(col_a_to_b.keys())
            
            for category in l:
                if category in label:
                    tdef = col_a_to_b[category]
                    defst+= f"""**{category}**: {tdef} \n\n"""
                    if "Overall Score" in label and "Standard" in label:
                        label = category + " Score"
            # Setup
            # score = 3.1231
            if score <=4.0:
                max_score = 4.0
                percent = score / max_score
            else:
                max_score = 100.0
                percent = score / max_score

                           # --- Create circular progress ring with Plotly ---
            fig = go.Figure(go.Pie(
                values=[percent, 1 - percent],
                labels=["", ""],
                marker_colors=["#FFFFFF", "#56A3A6"],  # Teal fill, white background
                hole=0.7,
                sort=False,
                direction="clockwise",
                textinfo="none"
            ))
            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                width=60,
                height=60,
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
            )
            buffer = io.StringIO()
            fig.write_html(buffer, include_plotlyjs='cdn')  # or include_plotlyjs=True if you want to bundle it
            html_string = buffer.getvalue()
            if "Percent" in label:
                s = f"{score:.0f}%"
            else:
                s = f"{score:.3f}"
            # --- Create custom styled card ---
            card_html = """<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
            <style>
            .card-container {
                margin: 0px 0px 0px 0px;
                background-color: #084C61;
                border-radius: 12px;
                padding: 0.8rem 1.2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 100%;
                height: fit-content;
            }
            .card-left {
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            .card-score {
                font-family: 'Poppins', sans-serif;
                font-size: 20px;
                font-weight: 600;
                color: white;
                margin-bottom: 0px;
            }
            .card-label {
                font-family: 'Poppins', sans-serif;
                font-size: 14px;
                font-weight: 400;
                color: white;
            }
            .desc-display {
                font-size: 0.9rem;
                color: #084c61;
                font-family: 'Poppins', sans-serif;

            }
            </style>
            <div class="card-container">
                <div class="card-left">
                    <div class="card-score">""" + f"{s}" + """</div>
                    <div class="card-label">"""+ f"{label}" + """</div>
                </div>
                <div class="card-ring">""" + f"{html_string}" + """</div></div>"""
        

            # Estimate height based on content
            base_height = 85
            line_height = 15
            num_lines = 2 if len(label) > 30 else 1  # crude logic
            card_height = base_height + (num_lines * line_height)

            components.html(card_html, height=card_height)
            x = False
            if access_level or is_admin:
                if "Standard" in label:
                    if "Indicator" in label and ((score>=3.0 and score <=4.0) or (score>=75.0)):
                        st.markdown(defst)
                        return
                    elif "Indicator" not in label:
                        st.markdown(defst)
                        return
                    else:
                        for category in l:
                            if "Standard" in category and category in label:
                                if (not is_admin) and (not access_level):
                                    st.markdown(defst)
                                    return
                                tdef = col_a_to_b[category]
                                sl = f"""**{category}**: {tdef}"""
                                st.markdown(sl)
                                
                                
                if low_indicators!=None:
                    for cat in low_indicators:
                #         if cat["name"] in label and score<3.0 or (score>4.0 and score<75.0):
                #             display_recommendation(cat, sheet3_data, org_name)
                #             return
                        label_norm = label.lower().replace("score", "").strip()  
                        cat_name_norm = cat["name"].lower().replace("score", "").strip()
                        if (cat_name_norm in label_norm and score < 3.0) or (cat_name_norm in label_norm and 4.0 < score < 75.0):
                            display_recommendation(cat, sheet2_data, org_name)
                            return
            if not x:
                st.markdown(defst)




        def score_trend(scores):
            df = pd.DataFrame({
                "Submission": list(range(1, len(scores)+1)),
                "Overall Score": scores
            })
            fig = px.line(df, x="Submission", y="Overall Score", markers=True)
            fig.update_traces(line_color="#56A3A6", marker=dict(color="#084C61", size=10))
            fig.update_layout(height=300, margin=dict(l=40, r=40, t=40, b=40), paper_bgcolor="rgba(0,0,0,0)", title=dict(
                text="Score over Time", 
                font=dict(size=24)))
            return fig

        # Staff Bar Chart
        def staff_bar(scores):
            df = pd.DataFrame(scores.items(), columns=["Staff", "Score"])
            fig = px.bar(df, y="Staff", x="Score", orientation="h", color="Score", color_continuous_scale=["#56A3A6", "#084C61"])
            fig.update_layout(height=300, margin=dict(l=40, r=40, t=40, b=40), paper_bgcolor="rgba(0,0,0,0)", 
            coloraxis_showscale=True, title=dict(
                text="Score by Staff", 
                font=dict(size=24)))
            return fig

        def reg_staff_bar(scores):
            # df = pd.DataFrame(scores.items(), columns=["Category", "Score"])
            # fig = px.bar(df, y="Category", x="Score", orientation="h", color="Score", color_continuous_scale=["#56A3A6", "#084C61"])
            # fig.update_layout(height=300, margin=dict(l=40, r=40, t=40, b=40), paper_bgcolor="rgba(0,0,0,0)", 
            # coloraxis_showscale=True, title=dict(
            #     text="Score by Category", 
            #     font=dict(size=24)))
            # return fig
            df = pd.DataFrame(scores.items(), columns=["Category", "Score"])
            df["Score"] = pd.to_numeric(df["Score"], errors="coerce")

            # Custom sort key
            # def sort_key(label):
            #     if "Standard" in label:
            #         match = re.search(r"Standard (\d+)", label)
            #         return (0, int(match.group(1)) if match else 0)
            #     elif "Indicator" in label:
            #         match = re.search(r"Indicator (\d+)\.(\d+)", label)
            #         if match:
            #             return (1, int(match.group(1)), int(match.group(2)))
            #         else:
            #             return (1, 999, 999)  # fallback
            #     else:
            #         return (2, label)  # Anything else goes last
            def sort_key(label):
                standard_match = re.search(r"Standard (\d+)", label)
                indicator_match = re.search(r"Indicator (\d+)\.(\d+)", label)

                if standard_match:
                    standard_num = int(standard_match.group(1))
                    return (standard_num, 0, 0)  # Standards first in each group
                elif indicator_match:
                    standard_num = int(indicator_match.group(1))
                    indicator_num = int(indicator_match.group(2))
                    return (standard_num, 1, indicator_num)  # Indicators sorted within their Standard group
                else:
                    return (999, 999, label)  # Anything else goes at the end

            # Sort the DataFrame using the custom key
            df = df.sort_values(by="Category", key=lambda col: col.map(sort_key))

            fig = px.bar(
                df,
                y="Category",
                x="Score",
                orientation="h",
                color="Score",
                color_continuous_scale=["#56A3A6", "#084C61"]
            )

            fig.update_yaxes(autorange="reversed")

            fig.update_layout(
                height=300,
                margin=dict(l=40, r=40, t=40, b=40),
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=True,
                title=dict(text="Score by Category", font=dict(size=24))
            )

            return fig
        st.html("""<style>.st-key-white_container_big{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}</style>""")
        # Title

        spreadsheet = client.open(ASSESSMENTS[assessment]["sheet_name"])
        cat_sheet = spreadsheet.worksheet("Indicators")
        sheet3_data = cat_sheet.get_all_values()
        if is_admin or access_level:
            
            with st.container(key = "white_container_big"):
                
                st.markdown(f"<h1 style='color:#084C61; font-size:48px; font-weight:800;'>{assessment}</h1>", unsafe_allow_html=True)
                st.write("View results.")

                # Layout: 3 main columns
                col1, col2, col3 = st.columns([6, 7, 7])
                
                def white_container(i):
                    return st.html(f"""<style>.st-key-white_container_{i}{{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}}</style>""")
                st.html("""<style>.st-key-white_container_1{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}</style>""")
                st.html("""<style>.st-key-white_container_2{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}</style>""")
                st.html("""<style>.st-key-white_container_3{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}</style>""")
                
                st.html("""<style>.st-key-teal_container{background-color: #084C61; border-radius: 20px; padding: 5%;}</style>""")
                if overall_score == 1000:
                    st.html("""<style>.st-key-white_container_small{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 1%;}</style>""")
                    with st.container(key ="white_container_small"):
                        st.write(f"**No {assessment} results were found.**")
                else:
                    with col1:
                        if not all_orgs:
                            with st.container(key ="white_container_1"):
                                
                                with st.container(key ="teal_container"):
                                    st.plotly_chart(draw_score_dial(overall_score), use_container_width=True)
                                with st.expander("**Scores by Standards and Indicators**"):
                                    for label, score in standard_scores:
                                        if pd.isna(score):
                                            continue
                                        # st.plotly_chart(draw_standards(), use_container_width=True)
                                        render_score_card(sheet3_data, sheet2_data, score, label)

                        if is_admin and not access_level:
                            w_prefix = str(uuid.uuid4())
                            wa = "white_container_" + w_prefix
                            st.html(f"""<style>.st-key-{wa}{{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}}</style>""")
                            site_col_candidates = ["Extracted Sites", "Site Name"]
                            site_series = None
                            for col in site_col_candidates:
                                if col in org_df.columns and org_df[col].dropna().apply(lambda x: isinstance(x, str) and x.strip() != "").any():
                                    site_series = org_df[col]
                                    break
                            if site_series is not None:
                                with st.container(key=wa):
                                    st.write("#### Scores by Site")

                                    # Determine the site column, or skip if none found
                                    site_col_candidates = ["Extracted Sites", "Site Name"]
                                    site_series = None
                                    for col in site_col_candidates:
                                        if col in org_df.columns and org_df[col].dropna().apply(lambda x: isinstance(x, str)).any():
                                            site_series = org_df[col]
                                            break
                                    # Build normalized-to-original site name map
                                    site_display_map = {}
                                    for raw in site_series.dropna().unique():
                                        if isinstance(raw, str):
                                            norm = raw.strip().lower()
                                            if norm not in site_display_map:
                                                site_display_map[norm] = raw  # preserve original casing

                                    for norm_site, display_site in site_display_map.items():
                                        if display_site!="" and display_site!=" ":
                                            # Match using normalized form
                                            matching_df = org_df[site_series.astype(str).str.strip().str.lower() == norm_site]
                                            if matching_df.empty:
                                                continue

                                            # Compute overall score
                                            all_scores = []
                                            for col in overall_score_cols:
                                                all_scores.extend(pd.to_numeric(matching_df[col], errors="coerce").dropna().tolist())

                                            if not all_scores:
                                                continue

                                            avg_score = sum(all_scores) / len(all_scores)

                                            with st.expander(f"**{display_site}'s Results**"):
                                                ta = "teal_container_" + str(uuid.uuid4())
                                                st.html(f"""<style>.st-key-{ta}{{background-color: #084C61; border-radius: 20px; padding: 5%;}}</style>""")
                                                with st.container(key =ta):
                                                    st.plotly_chart(draw_score_dial(avg_score, "Overall Score"), use_container_width=True)

                                                for col in matching_df.columns:
                                                    if "Overall Score" in col and (("Standard" not in col) or ("-" in col)):
                                                        continue
                                                    series = matching_df[col].replace('%', '', regex=True)
                                                    series = pd.to_numeric(series, errors="coerce")
                                                    avg = series.mean()
                                                    if pd.notna(avg) and ("Standard" in col or "Indicator" in col):
                                                        render_score_card(sheet3_data, sheet2_data, avg, col, org_name=display_site)
                        else:
        
                            # with st.container(key="white_container_1"):
                            #     st.write("#### All Organizations' Scores")
                            #     with st.container(key ="teal_container"):
                            #         st.plotly_chart(draw_score_dial(overall_score), use_container_width=True)
                            #     for org in all_orgs:
                            #         corg = org.rstrip()
                            #         with st.expander(f"**{corg}'s Results**"):
                            #             this_prefix = str(uuid.uuid4()) 
                            #             t = "teal_container_" + this_prefix
                            #             st.html(f"""<style>.st-key-{t}{{background-color: #084C61; border-radius: 20px; padding: 5%;}}</style>""")
                                        
                            #             # st.write("##### " + corg)
                            #             with st.container(key =t):
                            #                 st.plotly_chart(draw_score_dial(over_scores[org]), key=org, use_container_width=True)
                            #             for label, score in standard_scores[org]:
                            #                 # st.plotly_chart(draw_standards(), use_container_width=True)
                            #                 render_score_card(sheet3_data, score, label, org_name = org)
                            if access_level:
                                for org in all_orgs:
                                    corg = org.rstrip()
                                    # Filter rows for this org
                                    torg_df = org_df[org_df["Extracted Orgs"].apply(
                                        lambda x: corg.lower() in x if isinstance(x, list) else corg.lower() == x.strip().lower()
                                    )]

                                    if torg_df.empty:
                                        continue

                                    # --- Compute Org-Level Scores ---
                                    all_scores = []
                                    for col in overall_score_cols:
                                        all_scores.extend(pd.to_numeric(torg_df[col], errors="coerce").dropna().tolist())
                                    org_avg_score = sum(all_scores) / len(all_scores) if all_scores else None

                                    # --- Compute Standards/Indicators ---
                                    standard_scores_org = []
                                    for col in torg_df.columns:
                                        if "Overall Score" in col and (("Standard" not in col) or ("-" in col)):
                                            continue
                                        series = pd.to_numeric(torg_df[col].replace('%', '', regex=True), errors="coerce")
                                        avg = series.mean()
                                        if pd.notna(avg) and ("Standard" in col or "Indicator" in col):
                                            standard_scores_org.append((col, avg))

                                    # --- Display White Container per Org ---
                                    w_prefix = str(uuid.uuid4())
                                    wa = f"white_container_{w_prefix}"
                                    st.html(f"""<style>.st-key-{wa}{{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}}</style>""")
                                    st.html(f"""<style>.st-key-teal_container_{w_prefix}{{background-color: #084C61; border-radius: 20px; padding: 5%;}}</style>""")
                                    with st.container(key=wa):
                                        st.write(f"#### {corg}'s Scores")

                                        if org_avg_score is not None:
                                            with st.container(key=f"teal_container_{w_prefix}"):
                                                st.plotly_chart(draw_score_dial(org_avg_score, "Overall Score"), use_container_width=True)

                                        if standard_scores_org:
                                            with st.expander("**Scores by Standards and Indicators**"):
                                                for label, score in standard_scores_org:
                                                    if pd.isna(score):
                                                        continue 
                                                    render_score_card(sheet3_data, sheet2_data, score, label, org_name=corg)

                                        # --- Show Site Scores if Available ---
                                        site_col = None
                                        for col in ["Extracted Sites", "Site Name"]:
                                            if col in torg_df.columns and torg_df[col].dropna().apply(lambda x: isinstance(x, str)).any():
                                                site_col = torg_df[col]
                                                break

                                        if site_col is not None:
                                            # Build normalized display map
                                            site_display_map = {}
                                            for raw in site_col.dropna().unique():
                                                if isinstance(raw, str):
                                                    norm = raw.strip().lower()
                                                    if norm and norm not in site_display_map:
                                                        site_display_map[norm] = raw

                                            if site_display_map:
                                                st.markdown("##### Site-Level Results")
                                                for norm_site, display_site in site_display_map.items():
                                                    site_df = torg_df[site_col.astype(str).str.strip().str.lower() == norm_site]
                                                    if site_df.empty:
                                                        continue

                                                    site_scores = []
                                                    for col in overall_score_cols:
                                                        site_scores.extend(pd.to_numeric(site_df[col], errors="coerce").dropna().tolist())
                                                    site_avg = sum(site_scores) / len(site_scores) if site_scores else None

                                                    if site_avg is not None:
                                                        c_prefix = str(uuid.uuid4())
                                                        ca = "teal_expander_" + c_prefix
                                                        st.html(f"""<style>.st-key-{ca}{{background-color: #084C61; border-radius: 20px; padding: 5%;}}</style>""")
                                                        with st.expander(f"**{display_site}**"):
                                                            with st.container(key=ca):
                                                                st.plotly_chart(draw_score_dial(site_avg, "Overall Score"), use_container_width=True)

                                                            for col in site_df.columns:
                                                                if "Overall Score" in col and (("Standard" not in col) or ("-" in col)):
                                                                    continue
                                                                series = site_df[col].replace('%', '', regex=True)
                                                                series = pd.to_numeric(series, errors="coerce")
                                                                avg = series.mean()
                                                                if pd.notna(avg) and ("Standard" in col or "Indicator" in col):
                                                                    render_score_card(sheet3_data, sheet2_data, avg, col, org_name=display_site)

                    with col2:
                        with st.container(key ="white_container_2"):
                            st.plotly_chart(score_trend(score_over_time), use_container_width=True)
                            with st.expander("**Overall Score by Submission**"):
                                for label, score in submissions.items():
                                    if pd.isna(score):
                                        continue
                                    render_score_card(sheet3_data, sheet2_data, score, label)

                    with col3:
                        with st.container(key ="white_container_3"):
                            st.plotly_chart(staff_bar(staff_scores_num), use_container_width=True)
                            
                            for name, score in staff_scores.items():
                                that_prefix = str(uuid.uuid4())
                                tname = name.rstrip()
                                # st.write("##### " + tname)
                                with st.expander(f"**{tname}'s Results**"):
                                    for label, s in score:
                                        if pd.isna(s):
                                            continue 
                                        if "Overall Score" in label:
                                            la = "teal_container_" + that_prefix
                                            st.html(f"""<style>.st-key-{la}{{background-color: #084C61; border-radius: 20px; padding: 5%;}}</style>""")
                                            with st.container(key = la):
                                                lab = f"{tname}'s {label}"
                                                st.plotly_chart(draw_score_dial(s, "Overall Score"), use_container_width=True)
                                        if "Overall Score" in label and "Standard" in label and ("-" not in label):
                                            if not access_level:
                                                render_score_card(sheet3_data, sheet2_data, s, label)
                                            if access_level:
                                                render_score_card(sheet3_data, sheet2_data, s, label, org_name = tname)
                                        elif "Overall Score" in label and (("Standard" not in label) or ("-" in label)):
                                            continue
                                        else:
                                            if not access_level:
                                                render_score_card(sheet3_data, sheet2_data, s, label)
                                            if access_level:
                                                render_score_card(sheet3_data, sheet2_data, s, label, org_name = tname)
        else:
            with st.container(key = "white_container_big"):
                st.markdown(f"<h1 style='color:#084C61; font-size:48px; font-weight:800;'>{assessment}</h1>", unsafe_allow_html=True)
                st.write("View results.")

                # Layout: 3 main columns
                colo1, colo2 = st.columns([13, 7])

                col1, col2, col3 = st.columns([6, 7, 7])
                
            
                st.html("""<style>.st-key-white_container_1{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}</style>""")
                st.html("""<style>.st-key-white_container_2{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}</style>""")
                st.html("""<style>.st-key-white_container_3{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}</style>""")
                st.html("""<style>.st-key-white_container_4{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}</style>""")
                st.html("""<style>.st-key-teal_container{background-color: #084C61; border-radius: 20px; padding: 5%;}</style>""")
                if overall_score == 1000:
                    st.html("""<style>.st-key-white_container_small{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 1%;}</style>""")
                    with st.container(key ="white_container_small"):
                        st.write(f"**No {assessment} results were found for {email}.**")
                else:
                    
                        
                    with col1:
                        with st.container(key ="white_container_1"):
                            with st.container(key ="teal_container"):
                                st.plotly_chart(draw_score_dial(overall_score), use_container_width=True)
                            with st.expander("**Score by Standards and Indicators**"):
                                        for label in standard_scores:
                                            score = standard_scores[label]
                                            if pd.isna(score):
                                                continue
                                            # st.plotly_chart(draw_standards(), use_container_width=True)
                                            render_score_card(sheet3_data, sheet2_data, score, label)    
                    
                    with col2:
                        with st.container(key = "white_container_3"):
                            st.plotly_chart(reg_staff_bar(standard_scores), use_container_width=True)
                            with st.expander("**Category Descriptions**"):
                                for label in standard_scores:
                                    desc(sheet3_data, label)

                            
                    with col3:
                        with st.container(key ="white_container_2"):
                            st.plotly_chart(score_trend(score_over_time), use_container_width=True)
                            with st.expander("**Score by Submission**"):
                                for label, score in submissions.items():
                                    if pd.isna(score):
                                        continue
                                    render_score_card(sheet3_data, sheet2_data, score, label)


else:
    # Home Page with HTML navigation
    st.html(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700;900&display=swap');
        html, body {{
          margin: 0;
          font-family: 'Poppins', sans-serif !important;
        }}
        # .navbar {{
        #   display: flex;
        #   justify-content: flex-end;
        #   padding: 20px 40px;
        #   font-size: 18px;
        #   flex-wrap: wrap;
        # }}
        # .navbar a {{
        #   margin-left: 30px;
        #   color: black;
        #   text-decoration: none;
        # }}
        # .navbar a:first-child {{
        #   color: #084C61;
        #   font-weight: bold;
        # }}
        .main-container {{
          display: flex;
          justify-content: space-between;
          align-items: center;
        #   padding: 60px 40px;
          flex-wrap: wrap;
        }}
        .text-content {{
          max-width: 500px;
          flex: 1 1 300px;
        #   padding: 20px;
        }}
        .title {{
          font-size: 48px;
          font-weight: 800;
          color: #084C61;
        }}
        .subtitle {{
          font-size: 18px;
          margin-top: 10px;
        }}
        .image-content {{
          flex: 1 1 300px;
        #   padding: 20px;
          text-align: center;
        }}
        .image-content img {{
          max-width: 100%;
          height: auto;
        }}
        @media (max-width: 768px) {{
          .main-container {{
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
          }}
        #   .navbar {{
        #     justify-content: center;
        #     padding: 10px 20px;
        #   }}
          .title {{
            font-size: 36px;
            text-align: center;
            margin-top: 20%;
          }}
          .subtitle {{
            text-align: center;
            margin-bottom: 0px;
          }}
          .image-content{{
            margin-top: 0px;
            padding: 0px;
            text-align: center;
          }}
          .image-content img{{
            max-width: 90vw;
            height: auto;
          }}
        }}
      </style>
    </head>
    <body>
      <div class="main-container">
        <div class="text-content">
          <div class="title">INSIGHT</div>
          <div class="subtitle">Assess your organization or view results.</div>
        </div>
        <div class="image-content">
          <img src="https://i.imgur.com/8Q3M2NU.png" alt="Dashboard Illustration"/>
        </div>
      </div>
    </body>
    </html>
    """)
