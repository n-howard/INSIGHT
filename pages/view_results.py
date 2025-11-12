

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
import time
from simple_salesforce import Salesforce
from streamlit_integration import create_sf, get_org_records, get_all_org_records, get_all_overall, get_overall, get_recs_desc, get_avg_records, get_avg_overall, get_all_avg_overall
from collections import defaultdict

cookies = EncryptedCookieManager(prefix="myapp_", password=st.secrets.COOKIE_SECRET)
if not cookies.ready():
    st.stop()

st.session_state.org_input = st.session_state.org_input
st.session_state.access = st.session_state.access
st.session_state.is_admin = st.session_state.is_admin





sf = create_sf()





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
        "sheet_name": "Environment, Health, and Safety (Responses)",
        "fields": ['Timestamp__c', 'Site__c', 'Contact_Name__c', 'Overall_Score__c', 'Standard_1__c', 'Indicator_1_1__c', 'Indicator_1_2__c', 'Standard_2__c', 'Indicator_2_1__c', 'Indicator_2_2__c', 'Standard_3__c', 
            'Indicator_3_1__c', 'Indicator_3_2__c', 'Indicator_3_3__c', 'Standard_4__c', 'Indicator_4_1__c', 'Indicator_4_2__c', 'Indicator_4_3__c'
            ]
    },
    "Highly Skilled Personnel": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSfCs3lUrb2hEB92aZn33ledpwKNXtDOuPjd1hw40p-ZW-Y0JA/viewform?embedded=true",
        "sheet_name": "Highly Skilled Personnel (Responses)",
        "fields": ['Timestamp__c', 'Site__c', 'Contact_Name__c', 'Overall_Score__c', 'Standard_1__c', 'Indicator_1_1__c', 'Standard_2__c', 'Indicator_2_1__c', 'Indicator_2_2__c', 'Standard_3__c', 
            'Indicator_3_1__c', 'Indicator_3_2__c'
            ]
    },
    "Program Management": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSfiFsaUqThoawBo-vTQLp5vPslFV-4A_efQw9PBwd3QRiHSIA/viewform?embedded=true",
        "sheet_name": "Program Management (Responses)",
        "fields": ['Timestamp__c', 'Site__c', 'Contact_Name__c', 'Overall_Score__c', 'Percent_Complete__c', 'Percent_In_Progress__c', 'Standard_2__c', 'Indicator_2_1__c', 'Standard_3__c', 
            'Indicator_3_1__c', 'Standard_4__c', 'Indicator_4_1__c', 'Standard_5__c', 'Indicator_5_1__c',
            ]
    },
    "Youth Development and Engagement": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSfvrLHuw7dqBQ5gN-i3rjNA-fusFxd96Hl4hsrC1MwKofBP9A/viewform?embedded=true",
        "sheet_name": "Youth Development and Engagement (Responses)",
        "fields": ['Timestamp__c', 'Site__c', 'Contact_Name__c', 'Overall_Score__c', 'Standard_1__c', 'Indicator_1_1__c', 'Standard_2__c', 'Indicator_2_1__c', 'Standard_3__c', 
            'Indicator_3_1__c', 'Indicator_3_2__c', 'Indicator_3_3__c', 'Standard_4__c', 'Indicator_4_1__c', 'Indicator_4_2__c', 'Indicator_4_3__c'
            ]
        
    },
    "Programming and Activities": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSejk08smadc3IPkfoOYk9P8Hdj4JcS8UEfnh1bUXwAPUEpPDw/viewform?embedded=true",
        "sheet_name": "Programming and Activities (Responses)",
        "fields": ['Timestamp__c', 'Site__c', 'Contact_Name__c', 'Overall_Score__c', 'Standard_1__c', 'Indicator_1_1__c', 'Indicator_1_2__c', 'Indicator_1_3__c', 'Standard_2__c', 
            'Indicator_2_1__c', 'Indicator_2_2__c', 'Indicator_2_3__c'
            ]

    },
    "Families, Schools, and Communities": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSf2jg-yPBIGx9w2Zhl1aX3SQGcASQIDMTBizMJ4v4zurNTF-w/viewform?embedded=true",
        "sheet_name": "Families, Schools, and Communities (Responses)",
        "fields": ['Timestamp__c', 'Site__c', 'Contact_Name__c', 'Overall_Score__c', 'Standard_1__c', 'Indicator_1_1__c', 'Indicator_1_2__c', 'Indicator_1_3__c', 'Indicator_1_4__c']
    },
}

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
            st.switch_page("pages/self_assess.py")

with col3:
    with stylable_container(f"navbar_view_btn", css_styles="""
        button {
            background-color: white;
            color: black;
            border-radius: 6px;
            padding: 8px 16px;
            border: none;
            font-weight: 600;
            transition: background-color 0.2s;
        }
        button:focus,
        button:active, 
        button:hover {
            background-color: white;
            color: #084C61;
            outline: none;
            box-shadow: none;
        }
    """):
        if st.button("View Results", use_container_width = True):
            st.rerun()

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
            st.cache_data.clear()
            st.switch_page("app.py")



st.html("""
<style>
.score-card {
  background-color: white;
  filter:drop-shadow(2px 2px 2px grey);
  border-radius: 20px;
  padding: 14px 12px;
}
.score-card__title {
  /* Make the title area a fixed height so cards align */
  min-height: 70px;          /* desktop */
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #084C61;
  font-weight: 600;
  font-size: 16px;
  line-height: 1.2;
  margin-bottom: 6px;
  padding: 0 8px;
  word-break: break-word;    /* avoid overflow on very long words */
}
.score-card__title .clamp {
  display: -webkit-box;
  -webkit-line-clamp: 6;     /* show up to 2 lines */
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.score-card__dial {
  display: flex;
  justify-content: center;
}
</style>
""")
def render_overall_score(title: str, score: float, key_suffix: str = ""):
    """Renders a fixed-height title + dial so cards align across the row."""
    # Unique container key per card
    k = f"score_card_{key_suffix or uuid.uuid4()}"
    st.html(f"""
        <div class="score-card">
            <div class="score-card__title">
            <span class="clamp">{title}</span>
            </div>
        </div>
    """)

# def render_all_scores(ASSESSMENTS):
    
             



# st.markdown("""</div>""", unsafe_allow_html=True)

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
                    if st.button(variation, width='stretch'):
                        st.session_state["variation"] = variation

    st.markdown("""</div>""", unsafe_allow_html=True)
# Donut Dial Function
def draw_score_dial(score, label="Overall Score"):
    unique_prefix = str(uuid.uuid4()) 
    fig = go.Figure(go.Pie(
        values=[score, 4 - score],
        labels=["", ""],
        marker_colors=["#D3F3FD", "#013747"],
        hole=0.78,
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
    # st.markdown("""</div>""", unsafe_allow_html=True)




# render_variation_buttons()

st.write("\n")


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

button {{
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
}}

button:focus {{
    background-color: #084C61;
    color: white;
    color: #fff;
}}

button:hover {{
    background-color: #084C61;
    color: white;
    color: #fff;
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

    <img src="https://i.imgur.com/8Q3M2NU.png" class="faded-bg" alt="Background Illustration"/>
</div>
""")

with stylable_container(f"all_assessment", css_styles="""
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
    margin-bottom: 0%;
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
    if st.button("All Assessments", width='stretch'):
        st.session_state["variation"] = "all"
    
render_variation_buttons()



assessment = st.session_state.get("variation", None)


def sess_state_create():
    st.session_state.access = str(cookies.get("access_level", "")).strip().lower()=="true"
    st.session_state.is_admin = str(cookies.get("admin_input", "")).strip().lower()=="true"
sess_state_create()


if assessment == "all":

    # --- Helpers ---
    def norm(s):
        return str(s).strip().lower()


    
    org_input = st.session_state.org_input
    cols = st.columns(6)

    for i, (assessment, cfg) in enumerate(ASSESSMENTS.items()):
        with cols[i % 6]:
            
            # df = all_data[f"{assessment}|Scores"]["df"]

            results = get_avg_overall(org_input, sf, assessment, st.session_state.is_admin, st.session_state.access, st.session_state.user_email)

            # df = pd.DataFrame.from_dict(results["records"])

            

            # if df.empty:
            if len(results["records"]) == 0:
                w_prefix = str(uuid.uuid4())
                wa = f"white_container_{w_prefix}"
                st.html(f"""<style>.st-key-{wa}{{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}}</style>""")
                
                with st.container(key=wa):
                    st.write(f"**No {assessment} results were found.**")
                continue
            else:
            
                j = 1
                if st.session_state.access:
                    for li in results["records"]:
                        for avg in li.values():
                            j+=1
                            if isinstance(avg, float):
                         
                                w_prefix = str(uuid.uuid4())
                                wa = f"white_container_{w_prefix}"
                                st.html(f"""<style>.st-key-{wa}{{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}}</style>""")
                                st.html(f"""<style>.st-key-teal_container_{w_prefix}{{background-color: #084C61; border-radius: 20px; padding: 5%;}}</style>""")
                                with st.container(key=wa):
                                    org = li["Organization__c"]
                                    render_overall_score(f"{org}'s Average Overall Score for {assessment}", avg, key_suffix=f"{assessment}__{i}_{j}")
                                    st.html(f"""<style>.st-key-teal_container_{w_prefix}_{j}{{background-color: #084C61; border-radius: 20px; padding: 5%;}}</style>""")
                                    with st.container(key=f"teal_container_{w_prefix}_{j}"):
                                        st.plotly_chart(draw_score_dial(avg), width='stretch')
                else:

                    avg = results["records"][0]["Overall_Score__c"]
                    w_prefix = str(uuid.uuid4())
                    wa = f"white_container_{w_prefix}"
                    st.html(f"""<style>.st-key-{wa}{{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}}</style>""")
                    st.html(f"""<style>.st-key-teal_container_{w_prefix}{{background-color: #084C61; border-radius: 20px; padding: 5%;}}</style>""")
                    with st.container(key=wa):
                        render_overall_score(f"Average Overall Score for {assessment}", avg, key_suffix=f"{assessment}__{i}_{i}{i}")
                        with st.container(key=f"teal_container_{w_prefix}"):
                            st.plotly_chart(draw_score_dial(avg), width='stretch')
                    
     
elif assessment:

           



    org_input = st.session_state.org_input
    results = {}
    if st.session_state.is_admin or st.session_state.access:
        results = get_avg_records(st.session_state.org_input, sf, ASSESSMENTS[assessment], assessment, st.session_state.is_admin, st.session_state.access, st.session_state.user_email)
    else:
        results = get_org_records(st.session_state.org_input, sf, ASSESSMENTS[assessment], assessment, st.session_state.is_admin, st.session_state.access, st.session_state.user_email)
    
    if len(results["records"]) == 0:
    # if df is None:
        w_prefix = str(uuid.uuid4())
        wa = f"white_container_{w_prefix}"
        st.html(f"""<style>.st-key-{wa}{{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 1%;}}</style>""")
                
        with st.container(key=wa):
            st.write(f"**No {assessment} results were found.**")
    else:

        df = pd.DataFrame.from_dict(results["records"])


        def norm_col(column):
            col = column[:-3]
            if "Percent" not in col:
                
                col = col.replace("_", " ", 1) 
                col = col + " Score"
            if "Indicator" in col:
                col = col.replace("_", ".")
            
            if "Percent" in col:
                col = col.replace("_", " ")
            return col
        
        def ind_col(column):
            col = column[:-3]
            if "Percent" not in col:
                col = col.replace("_", " ", 1) 
            if "Indicator" in col:
                col = col.replace("_", ".")
            
            if "Percent" in col:
                col = col.replace("_", " ")
            return col

        overall = get_overall(org_input, sf, assessment, st.session_state.is_admin, st.session_state.access, st.session_state.user_email)
        overall_score = 1000
        # over_scores = {}
        # all_orgs = []
        if len(overall["records"])==0:
            overall_score = 1000
        else:
            overall_score = get_avg_overall(org_input, sf, assessment, st.session_state.is_admin, st.session_state.access, st.session_state.user_email)["records"][0]["Overall_Score__c"]



        def render_score_card(score, label, org_name: str = st.session_state.get("org_input")):
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
                    marker_colors=["#D3F3FD", "#013747"],  
                    hole=0.8,
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
                fig.write_html(buffer, config= {'displaylogo': False, 'modeBarButtonsToRemove': ['toImage']}, include_plotlyjs='cdn')  # or include_plotlyjs=True if you want to bundle it
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

            
            




        
        def score_trend(timestamp_score_triples):

            df = pd.DataFrame(timestamp_score_triples, columns=["Timestamp", "Overall Score", "Org Name"])
            # df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
            df = df.dropna(subset=["Timestamp", "Overall Score", "Org Name"])

            if df.shape[0] == 1:
                # Only one point: use formatted label as category
                # df["Label"] = df["Timestamp"].dt.strftime("%B %d, %Y")
                # fig = px.line(df, x="Label", y="Overall Score", markers=True, color_discrete_sequence=[
                fig = px.line(df, x="Timestamp", y="Overall Score", markers=True, color_discrete_sequence=[
                        "#084C61", "#0F6B75", "#138D90", "#56A3A6", "#A7D4D5", "#CBE8E8", "#E6F5F5"
                    ])
                fig.update_layout(
                    xaxis_title="Date",
                    xaxis=dict(tickformat="%b %d, %Y"),
                    height=300,
                    margin=dict(l=40, r=40, t=40, b=40),
                    paper_bgcolor="rgba(0,0,0,0)",
                    title=dict(text="Score Over Time", font=dict(size=24)))
            else:
                fig = px.line(
                    df,
                    x="Timestamp",
                    y="Overall Score",
                    color="Org Name" if st.session_state.access else None,
                    markers=True,
                    color_discrete_sequence=[
                        "#084C61", "#0F6B75", "#138D90", "#56A3A6", "#A7D4D5", "#CBE8E8", "#A8C6C6"
                    ]
                )

                fig.update_traces(marker=dict(size=10))
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Overall Score",
                    xaxis=dict(tickformat="%b %d, %Y"),
                    height=300,
                    margin=dict(l=40, r=40, t=40, b=40),
                    paper_bgcolor="rgba(0,0,0,0)",
                    title=dict(text="Score Over Time", font=dict(size=24))
                )

            return fig

        def staff_bar(scores):
            df = pd.DataFrame(scores.items(), columns=["Staff", "Score"])
            fig = px.bar(df, y="Staff", x="Score", orientation="h", color="Score", color_continuous_scale=["#56A3A6", "#084C61"])
            fig.update_layout(height=300, margin=dict(l=40, r=40, t=40, b=40), paper_bgcolor="rgba(0,0,0,0)", 
            coloraxis_showscale=True, title=dict(
                text="Score by Staff", 
                font=dict(size=24)))
            return fig

        def reg_staff_bar(scores):

            df = pd.DataFrame(scores.items(), columns=["Category", "Score"])
            df["Score"] = pd.to_numeric(df["Score"], errors="coerce")


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

        if st.session_state.is_admin or st.session_state.access:
            
            
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
                        def collapse_average(text):
                            if not isinstance(text, str):
                                return text
                            # Replace multiple "Average" repeats (case-insensitive)
                            return re.sub(r'(\bAverage\b\s*){2,}', 'Average ', text, flags=re.IGNORECASE).strip()

                        df["Organization__c"] = df["Organization__c"].apply(collapse_average)
                        df["Site__c"] = df["Site__c"].apply(collapse_average)
                        df["Organization__c"] = (
                            df["Organization__c"]
                            .astype(str)
                            .str.strip()
                            .apply(collapse_average)
                        )
                        df["Site__c"] = (
                            df["Site__c"]
                            .astype(str)
                            .str.strip()
                            .apply(collapse_average)
                        )

                        # if not all_orgs:
                        if st.session_state.is_admin and not st.session_state.access:
                            # all_sites = [site for site in df["Site__c"] if site is not None]
                            org_rows = df.loc[df["Organization__c"].str.contains("Average", case=False, na=False)]
                            with st.container(key ="white_container_1"):
                                
                                with st.container(key ="teal_container"):
                                    st.plotly_chart(draw_score_dial(overall_score), width='stretch')
                                with st.expander("**Scores by Standards and Indicators**"):
                                    for _, org_row in org_rows.iterrows():
                                        for column in org_row.index:
                                            normed_col = norm_col(column)
                                            if isinstance(org_row[column], float):
                                                
                                                av = org_row[column]
                                                # series = df[column]
                                                # series = pd.to_numeric(series, errors="coerce")
                                                # av = series.mean()
                                                if pd.notna(av):
                                                    if "Overall Score" in normed_col:
                                                        continue
                                                    
                                                    if "Standard" or "Indicator" or "Percent" in column:
                                                        render_score_card(av, normed_col)
                                                    if ("Indicator" in column and av < 3.0) or ("Percent_Complete" in column and av<75.0) or ("Percent_in" in column and av>50.0):
                                                        st.markdown(f"**{ind_col(column)} INSIGHT:** " + recs["records"][0][column].replace("{YOUR PROGRAM NAME}", org_input))
                                                    else:
                                                        st.markdown(f"**{normed_col}:** " + desc["records"][0][column])
                            # sites = {}
                            # for site in all_sites:
                            #     normalized = site.strip().lower()
                            #     sites[normalized] = site
                            site_loc = df.loc[df["Site__c"].str.contains("Average", case=False, na=False)]

                            if not site_loc.empty:
                                site_loc = site_loc.drop_duplicates(subset=["Organization__c", "Site__c"], keep="first")
                                w_prefix = str(uuid.uuid4())
                                wa = "white_container_" + w_prefix
                                st.html(f"""<style>.st-key-{wa}{{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}}</style>""")
                                with st.container(key=wa):
                                    st.write("#### Scores by Site")
                                    # df["normalized__site"] = df["Site__c"].apply(lambda x: str(x).strip().lower())
                                    # for norm_site, display_site in sites.items():
                                    for _, site_row in site_loc.iterrows():
                                        site = site_row["Site__c"].split("Average")[0].strip()
                                        with st.expander(f"**{site}'s Results**"):
                                            ta = "teal_container_" + str(uuid.uuid4())
                                            st.html(f"""<style>.st-key-{ta}{{background-color: #084C61; border-radius: 20px; padding: 5%;}}</style>""")
                                            
                                            # sdf = df[df["normalized__site"].apply(lambda x: norm_site in x)]
                                            # if sdf is not None:
                                            for column in site_row.index:
                                                if isinstance(site_row[column], float):
                                                    av = site_row[column]
                                                    # series = sdf[column]
                                                    # series = pd.to_numeric(series, errors="coerce")
                                                    # av = series.mean()
                                            
                                                    if pd.notna(av):
                                                        normed_col = norm_col(column)
                                        
                                                        if "Overall Score" in normed_col: 
                                                            with st.container(key =ta):
                                                                st.plotly_chart(draw_score_dial(av, "Overall Score"), width='stretch')
                                                            continue
                                                        if "Standard" or "Indicator" or "Percent" in column:
                                                            render_score_card(av, normed_col)
                                                        if ("Indicator" in column and av < 3.0) or ("Percent_Complete" in column and av<75.0) or ("Percent_in" in column and av>50.0):
                                                            st.markdown(f"**{ind_col(column)} INSIGHT:** " + recs["records"][0][column].replace("{YOUR PROGRAM NAME}", display_site))
                                                        else:
                                                            st.markdown(f"**{normed_col}:** " + desc["records"][0][column])

                
                        else:
                        
                            
                                
                            j = 0

                           
                            org_loc = df.loc[df["Organization__c"].str.contains("Average", case=False, na=False)]
                            for _, org_row in org_loc.iterrows():
                                display_org = org_row["Organization__c"]
                                w_prefix = str(uuid.uuid4())
                                wa = f"white_container_{w_prefix}"
                                st.html(f"""<style>.st-key-{wa}{{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}}</style>""")
                                st.html(f"""<style>.st-key-teal_container_{w_prefix}{{background-color: #084C61; border-radius: 20px; padding: 5%;}}</style>""")
                                with st.container(key=wa):
                                    st.write(f"#### {display_org}'s Scores")
                                    with st.container(key=f"teal_container_{w_prefix}"):
                                            st.plotly_chart(draw_score_dial(org_row["Overall_Score__c"], "Overall Score"), width='stretch')

                
                                    # torg_df = df[df["__normalized_extracted_orgs__"].apply(lambda x: norm_org in x)]

                              
                                    with st.expander("**Scores by Standards and Indicators**"):
                                        for column in org_row.index:
                                    
                                            if isinstance(org_row[column], float):
                                                # series = torg_df[column]
                                                # series = pd.to_numeric(series, errors="coerce")
                                                # av = series.mean()
                                                av = org_row[column]
                                                if pd.notna(av):
                                                    normed_col = norm_col(column)
                                    
                                                    if "Overall Score" in normed_col: 
                                                        continue
                                                        # standard_scores[display_org].append((norm_col(column), av))
                                                    if "Standard" or "Indicator" or "Percent" in column:
                                                        render_score_card(av, normed_col, display_org)
                                                    if ("Indicator" in column and av < 3.0) or ("Percent_Complete" in column and av<75.0) or ("Percent_in" in column and av>50.0):
                                                        st.write(f"**{ind_col(column)} INSIGHT:** " + recs["records"][0][column].replace("{YOUR PROGRAM NAME}", display_org))
                                                    else:
                                                        st.write(f"**{normed_col}:** " + desc["records"][0][column]) 

                                    # torg_sites = [site for site in torg_df["Site__c"] if site is not None]
                                    # sites = {}
                                    # for site in torg_sites:
                                    #     normalized = site.strip().lower()
                                    #     sites[normalized] = site
                                    sites = df.loc[
                                        df["Site__c"].str.contains("Average", case=False, na=False)
                                        & (df["Organization__c"] == display_org)
                                    ]

                                    if not sites.empty:
                                        # torg_df["normalized__site"] = torg_df["Site__c"].apply(lambda x: [i.strip().lower() for i in x] if isinstance(x, list) else [str(x).strip().lower()])
                                        # for norm_site, display_site in sites.items():
                                        for _, site in sites.iterrows():
                                            display_site = sites["Site__c"].split("Average")[0].strip()
                                            # sdf = torg_df[torg_df["normalized__site"].apply(lambda x: norm_site in x)]
                                            # if sdf is not None:
                                            with st.expander(f"**{display_site}**"):
                                            
                                                for column in site.index:
                                                    
                                                    if isinstance(site[column], float):
                                                    # series = sdf[column]
                                                    # series = pd.to_numeric(series, errors="coerce")
                                                    # av = series.mean()
                                                        av = site[column]
                                                
                                                        if pd.notna(av):
                                                            normed_col = norm_col(column)
                                            
                                                            if "Overall Score" in normed_col: 
                                                                ta = "teal_container_" + str(uuid.uuid4())
                                                                st.html(f"""<style>.st-key-{ta}{{background-color: #084C61; border-radius: 20px; padding: 5%;}}</style>""")
                                                                with st.container(key =ta):
                                                                    st.plotly_chart(draw_score_dial(av, "Overall Score"), width='stretch')
                                                                continue
                                                            if "Standard" or "Indicator" or "Percent" in column:
                                                                render_score_card(av, normed_col, display_site)
                                                            if ("Indicator" in column and av < 3.0) or ("Percent_Complete" in column and av<75.0) or ("Percent_in" in column and av>50.0):
                                                                st.markdown(f"**{ind_col(column)} INSIGHT:** " + recs["records"][0][column].replace("{YOUR PROGRAM NAME}", display_site))
                                                            else:
                                                                st.markdown(f"**{normed_col}:** " + desc["records"][0][column])

                            
                    with col2:
                        with st.container(key ="white_container_2"):
                        

                        
                            tdf = pd.DataFrame.from_dict(overall["records"])
                            timestamp_score_triples = []
                            for index, d in tdf.iterrows():
                                if d["Timestamp__c"] is not None:
                                    ts = pd.to_datetime(d["Timestamp__c"], errors='coerce')
                                    scores = d["Overall_Score__c"]
                                    if st.session_state.access:
                                        display_org = d["Organization__c"]
                                        label = display_org + ": " + ts.strftime("%B %d, %Y").replace(" 0", " ") 
                                        timestamp_score_triples.append((label, scores, display_org))
                                    else:
                                        contact_display = d["Contact_Name__c"]
                                        label =  contact_display + ": " + ts.strftime("%B %d, %Y").replace(" 0", " ") 
                                        timestamp_score_triples.append((label, scores, st.session_state.org_input))
                            
                            
                         
                            fig = score_trend(timestamp_score_triples)
                            st.plotly_chart(fig, width='stretch')
                            if st.session_state.access:
                                st.write(f"This chart shows the overall scores for {assessment} by organization over time.")
                            else:
                                st.write(f"This chart shows {org_input}'s overall scores for {assessment} over time.")
                            with st.expander("**Overall Score Over Time**"):
                                # for label, score in submissions.items():
                                for label, score, org in timestamp_score_triples:
                                    if pd.isna(score):
                                        continue
                                    # render_score_card(sheet3_data, sheet2_data, score, label)

                                    render_score_card(score, label, org)
                                    


                    with col3:
                        with st.container(key ="white_container_3"):
                            all_recs = get_org_records(st.session_state.org_input, sf, ASSESSMENTS[assessment], assessment, st.session_state.is_admin, st.session_state.access, st.session_state.user_email)
                            cdf = pd.DataFrame.from_dict(all_recs["records"])
                            if "Contact_Name__c" in cdf.columns:
                
                                original_names = cdf.dropna(subset=["Contact_Name__c"])["Contact_Name__c"]
                                normalized_map = {name.strip().lower(): name for name in original_names.unique()}
                                cdf["__normalized_contact__"] = cdf["Contact_Name__c"].astype(str).str.strip().str.lower()

                                contacts_to_show = list(normalized_map.keys())
                                staff_scores_num = {}
                                
                                for contact_norm in contacts_to_show:
                                    contact_display = normalized_map[contact_norm]
        
                                    contact_df = cdf[cdf["__normalized_contact__"] == contact_norm]
                                    if contact_df.empty:
                                        continue

                                    series = contact_df["Overall_Score__c"]
                                    series = pd.to_numeric(series, errors="coerce")
                                    avg = series.mean()
                                    if pd.notna(avg):
                                        staff_scores_num[contact_display] = avg
                                st.plotly_chart(staff_bar(staff_scores_num), width='stretch')
                                st.write(f"This chart shows the overall score for {assessment} for each staff member.")
                                for contact_norm in contacts_to_show:
                                    contact_display = normalized_map[contact_norm]
        
                                    contact_df = cdf[cdf["__normalized_contact__"] == contact_norm]
                                    if contact_df.empty:
                                        continue
                                    with st.expander(f"**{contact_display}'s Results**"):
                                        for column in contact_df.columns:
                                            series = contact_df[column]#.replace('%', '', regex=True)
                                            series = pd.to_numeric(series, errors="coerce")
                                            avg = series.mean()
                                            if pd.notna(avg):
                                                normed_col = norm_col(column)
                                            
                                                if "Overall_Score__c" in column:
                                                    that_prefix = str(uuid.uuid4())
                                                    la = "teal_container_" + that_prefix
                                                    st.html(f"""<style>.st-key-{la}{{background-color: #084C61; border-radius: 20px; padding: 5%;}}</style>""")
                                                    with st.container(key = la):
                                                       st.plotly_chart(draw_score_dial(avg, "Overall Score"), width='stretch')
                                                    
                                                    continue
                                                
                                                elif "Standard" or "Indicator" or "Percent" in column:
                                                    
                                                    render_score_card(avg, normed_col, contact_display)
                                                    if ("Indicator" in column and avg < 3.0) or ("Percent_Complete" in column and avg<75.0) or ("Percent_in" in column and avg>50.0):
                                                        if not st.session_state.access:
                                                            st.markdown(f"**{ind_col(column)} INSIGHT:** " + recs["records"][0][column].replace("{YOUR PROGRAM NAME}", org_input))
                                                        else:
                                                            st.markdown(f"**{ind_col(column)} INSIGHT:** " + recs["records"][0][column].replace("{YOUR PROGRAM NAME}", contact_display))
                                                    else:
                                                        st.markdown(f"**{normed_col}:** " + desc["records"][0][column])

                                       
        else:
            email = st.session_state.user_email
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
                    
                    standard_scores = {}
                    desc_table = {}
                    with col1:
                        
                               # if overall_score_cols:
                        with st.container(key ="white_container_1"):
                            with st.container(key ="teal_container"):
                                st.plotly_chart(draw_score_dial(overall_score), width='stretch')
                            with st.expander("**Score by Standards and Indicators**"):
                                for column in df.columns:
                                
                                    series = df[column]
                                    series = pd.to_numeric(series, errors="coerce")
                                    av = series.mean()

                                    if pd.notna(av):
                                        normed_col = norm_col(column)
                                        if "Overall_Score__c" in column:
                                            continue
                                    
                                        if "Standard" or "Indicator" or "Percent" in column:
                                            standard_scores[normed_col] = av
                                            render_score_card(av, normed_col)
                                            st.markdown(f"**{normed_col}:** " + desc["records"][0][column])
                                            desc_table[normed_col] = f"**{normed_col}:** " + desc["records"][0][column]
                                    

                        # with st.container(key ="white_container_1"):
                            # with st.container(key ="teal_container"):
                            #     st.plotly_chart(draw_score_dial(overall_score), use_container_width=True)
                            # with st.expander("**Score by Standards and Indicators**"):
                                        # for label in standard_scores:
                                        #     score = standard_scores[label]
                                        #     if pd.isna(score):
                                        #         continue
                                        #     # st.plotly_chart(draw_standards(), use_container_width=True)
                                        #     # render_score_card(sheet3_data, sheet2_data, score, label)    
                                        #     render_score_card(desc_map, score, label)
                    
                    with col2:
                        with st.container(key = "white_container_3"):
                            st.plotly_chart(reg_staff_bar(standard_scores), width='stretch')
                            st.write(f"This chart shows your score for each Standard and Indicator in {assessment}.")
                            with st.expander("**Category Descriptions**"):
                                # for label in standard_scores:
                                for label in desc_table.values(): 
                                    # desc(sheet3_data, label)
                                    st.write(label)

                            
                    with col3:
                        with st.container(key ="white_container_2"):
                            timestamp_score_triples = []
               
                            
                            for index, d in df.iterrows():
                                if d["Timestamp__c"] is not None:
                                    ts = pd.to_datetime(d["Timestamp__c"], errors='coerce')
                                    label = ts.strftime("%B %d, %Y").replace(" 0", " ")
                                    score = d["Overall_Score__c"]
                                    timestamp_score_triples.append((label, score, st.session_state.org_input))
                            
                            # org_name = st.session_state.get("org_input", "Unknown Org")
                            # subms = {}
                            # # for i, score in enumerate(score_series):
                            # #     if not pd.isna(score):
                            # #         ts = timestamp_series.iloc[i]
                            # #         if pd.notna(ts):
                            # #             timestamp_score_triples.append((ts, score, org_name))
                            # for key in submissions:
                            #     timestamp_score_triples.append((key, submissions[key], org_name))
                            fig = score_trend(timestamp_score_triples)
                            st.plotly_chart(fig, width='stretch')
                            st.write(f"This chart shows your overall score(s) for {assessment} over time.")
                            with st.expander("**Overall Score Over Time**"):
                                # for label, score in submissions.items():
                                for label, score, org in timestamp_score_triples:
                                    # if pd.isna(score):
                                    #     continue
                                    # render_score_card(sheet3_data, sheet2_data, score, label)
                                    render_score_card(score, label)
