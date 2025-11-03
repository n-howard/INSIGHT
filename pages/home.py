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

# st.set_page_config(page_title="INSIGHT", page_icon="./oask_short_logo.png", layout="wide")

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

# Restore from cookies if needed
if "org_input" not in st.session_state:
    cookie_org = cookies.get("org_input")
    cookie_site = cookies.get("site_input")
    if cookie_org:
        st.session_state["org_input"] = cookie_org
        st.session_state["site_input"] = cookie_site or ""

if "admin_input" not in st.session_state:  
    cookie_admin = cookies.get("admin_input")
    if cookie_admin:
        st.session_state["admin_input"] = cookie_admin
if "access_level" not in st.session_state:
    cookie_access = cookies.get("access_level")
    if cookie_access:
        st.session_state["access_level"] = cookie_access

if "email" not in st.session_state:
    email = cookies.get("user_email")
    if email:
        st.session_state["user_email"] = email





if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = str(cookies.get("admin_input", "")).strip().lower() == "true"

if "access" not in st.session_state:
    st.session_state["access"] = str(cookies.get("access_level", "")).strip().lower() == "true"

access_level = st.session_state["access"]

is_admin = st.session_state["is_admin"]





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
    },
}


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
            st.session_state["active_page"] = "home"
                

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
            st.switch_page("pages/self_assess.py")
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
    }
    """):
        if st.button("Logout", use_container_width = True):
            for key in ["org_input", "user_email", "access_level", "admin_input", "site_input", "variation", "active_page", "access", "is_admin"]:
                st.session_state.pop(key, None)
                cookies[key] = ""
            cookies.save()
            st.switch_page("app.py")
# st.markdown("""</div>""", unsafe_allow_html=True)






if st.session_state.get("active_page") == "info":
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

        <img src="https://i.imgur.com/8Q3M2NU.png" class="faded-bg" alt="Background Illustration"/>
    </div>
    """)
    data_form_link = "https://docs.google.com/forms/d/e/1FAIpQLScebVl2SRuhtDmzAEag_sPn0MgaAvLIpbwbm7-Imjup8aD2uw/viewform?embedded=true"
    components.iframe(data_form_link, width=1500, height=800, scrolling = True)

else:
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "home"

    if is_admin:
        data_form_link = "https://docs.google.com/forms/d/e/1FAIpQLScebVl2SRuhtDmzAEag_sPn0MgaAvLIpbwbm7-Imjup8aD2uw/viewform?embedded=true"
        _, acol1 = st.columns([6,4])
        with acol1:
            with stylable_container("data_form", css_styles="""
                button {
                    font-weight: 600;
                    font-size: .9rem;
                    padding: 1rem 2rem;
                    border: none;
                    border-radius: 2rem;
                    cursor: pointer;
                    text-align: center;
                    text-decoration: none;
                    transition: background-color 0.2s;
                    background-color: #d6e3e7;
                    color: #333;
                    max-width: 100%
                    
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
                if st.button("Program Information", use_container_width=True):
                    st.session_state["active_page"] = "info"
                    st.rerun()
                    # components.iframe(data_form_link, width=1500, height=800, scrolling = True)
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
          margin-bottom: 50%
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
            # padding: 40px 20px;
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
    

# Add top padding so content isn't hidden
st.markdown("<div style='height: 90px;'></div>", unsafe_allow_html=True)
# st.html(NAVBAR_HTML)



        

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700;900&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

