

import streamlit as st
st.set_page_config(page_title="INSIGHT", page_icon="./oask_short_logo.png", layout="wide")
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
from streamlit_extras.stylable_container import stylable_container
import numpy as np


cookies = EncryptedCookieManager(prefix="myapp_", password=st.secrets.COOKIE_SECRET)
if not cookies.ready():
    st.stop()





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






st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700;900&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# Inject global styles for consistency
st.markdown("""
    <style>
    .block-container {
        padding-top: 0rem;
    }
    </style>
""", unsafe_allow_html=True)
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
    }
}

def render_variation_buttons():
    st.markdown("""<div style='margin-top: 20px;'>""", unsafe_allow_html=True)

    var_cols = st.columns(3)
    variations = [
        "Youth Development and Engagement",
        "Environment, Health, and Safety",
        "Families, Schools, and Communities",
        "Highly Skilled Personnel",
        "Programming and Activities",
        "Program Management"
    ]


    for i in range(0, len(variations), 3):
        row = st.columns(3)
        for j, variation in enumerate(variations[i:i+3]):
            with row[j]:
                with stylable_container(f"variation_btn_{i+j}", css_styles="""
                    button {
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
                        width: 100%;
                        transition: background-color 0.2s;
                        background-color: #d6e3e7;
                        color: #333;
                        margin-bottom: 10%;
                    }

                    button:focus,
                    button:active, 
                    button:hover {
                        background-color: #084C61 !important;
                        color: white !important;
                        outline: none;
                        box-shadow: none;
                    }
                """):
                    if st.button(variation, use_container_width=True):
                        st.session_state["variation"] = variation

    st.markdown("""</div>""", unsafe_allow_html=True)

# acol, _, col1, col2, col3, col4 = st.columns([1, 5, 1, 1, 1, 1])

acol, _, col1, col2, col3, col4 = st.columns([2, 3, 2, 2, 2, 2])


with acol:
    st.markdown("<h3 style='color:#084C61; margin: 0;'>INSIGHT</h3>", unsafe_allow_html=True)

with col1:
    # st.markdown("<h3 style='color:white; margin: 0;'>INSIGHT</h3>", unsafe_allow_html=True)
    with stylable_container(f"navbar_home_btn", css_styles="""
        button {
            background-color: white;
            color: black;
            border-radius: 6px;
            padding: 8px 16px;
            border: none;
            font-weight: 600;
        }
        button:focus,
        button:active, 
        button:hover {
            background-color: white !important;
            color: #084C61 !important;
            outline: none;
            box-shadow: none;
        }
    """):
        if st.button("Home", use_container_width = True):
            st.switch_page("pages/home.py")
                

with col2:
    with stylable_container(f"navbar_self_btn", css_styles="""
        button {
            background-color: white;
            color: black;
            border-radius: 6px;
            padding: 8px 16px;
            border: none;
            font-weight: 600;
        }
        button:focus,
        button:active, 
        button:hover {
            background-color: white !important;
            color: #084C61 !important;
            outline: none;
            box-shadow: none;
        }
    """):
        if st.button("Self-Assess", use_container_width = True):
            st.rerun()

with col3:
    with stylable_container(f"navbar_view_btn", css_styles="""
        button {
            background-color: white;
            color: black;
            border-radius: 6px;
            padding: 8px 16px;
            border: none;
            font-weight: 600;
        }
        button:focus,
        button:active, 
        button:hover {
            background-color: white !important;
            color: #084C61 !important;
            outline: none;
            box-shadow: none;
        }
    """):
        if st.button("View Results", use_container_width = True):
            st.switch_page("pages/view_results.py")

with col4:
    with stylable_container(f"navbar_logout_btn_{str(uuid.uuid4())}", css_styles="""
        button {
            background-color: #084C61;
            color: white;
            border-radius: 6px;
            padding: 8px 16px;
            border: none;
            font-weight: 600;
        }
        button:focus,
        button:active, 
        button:hover {
        background-color: white !important;
        color: black !important;
        outline: none;
        box-shadow: none;
        }
    """):
        if st.button("Logout", use_container_width = True):
            for key in ["org_input", "user_email", "access_level", "admin_input", "site_input", "variation", "active_page", "access", "is_admin"]:
                st.session_state.pop(key, None)
                cookies[key] = ""
            cookies.save()
            st.switch_page("app.py")
# st.markdown("""</div>""", unsafe_allow_html=True)

st.session_state.pop("variation", None)
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


.faded-bg {{
    position: absolute;
    right: 0;
    top: 0;
    opacity: 0.08;
    max-width: 100%;
    z-index: 0;
}}

#     button {{
# font-weight: 600;
# font-size: .9rem;
# padding: 1rem 2rem;
# border: none;
# border-radius: 2rem;
# cursor: pointer;
# text-align: center;
# text-decoration: none;
# min-width: 33.33%;
# max-width: 100%;
# width: 100%;
# transition: background-color 0.2s;
# background-color: #d6e3e7;
# color: #333;
# margin-bottom: 10%;
# }}

# button:focus {{
#     background-color: #084C61;
#     color: white;
#     color: #fff;
# }}

# button:hover {{
#     background-color: #084C61;
#     color: white;
#     color: #fff;
# }}

@media (max-width: 768px) {{
    # .button-grid {{
    #     grid-template-columns: 1fr;
    # }}
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


    <img src="https://i.imgur.com/8Q3M2NU.png" class="faded-bg" alt="Background Illustration"/>
</div>
""")
render_variation_buttons()
assessment = st.session_state.get("variation", None)
if assessment:
    selfSes = assessment + " Self-Assessment"
    thisStyle = f"""<h3 style='text-align: center; font-size: 35px; font-weight: 600; font-family: Poppins;'>{selfSes}</h3>"""
    st.html(
        thisStyle
    )
    components.iframe(ASSESSMENTS[assessment]["form_url"], width = 1500, height=800, scrolling=True)