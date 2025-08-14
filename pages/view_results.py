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
    st.session_state["is_admin"] = cookies.get("admin_input", "").strip().lower() == "true"

if "access" not in st.session_state:
    st.session_state["access"] = cookies.get("access_level", "").strip().lower() == "true"

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
# --- Put this near the top of your file (once) ---
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
  -webkit-line-clamp: 4;     /* show up to 2 lines */
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

def render_all_scores(ASSESSMENTS):
    # --- Auth ---
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
    client = gspread.authorize(creds)

    # --- Helpers ---
    def norm(s):
        return str(s).strip().lower()

    def split_orgs(val):
        # handle single or multi-org entries (comma/semicolon/newline separated)
        if pd.isna(val): 
            return []
        parts = re.split(r"[;,/\n]+", str(val))
        return [p.strip() for p in parts if p and p.strip()]
    

    cols = st.columns(6)

    for i, (assessment, cfg) in enumerate(ASSESSMENTS.items()):
        with cols[i % 6]:
            # --- Load sheet ---
            try:
                sheet = client.open(cfg["sheet_name"]).sheet1
                raw_data = sheet.get_all_values()
            except Exception as e:
                st.error(f"Could not open sheet for {assessment}: {e}")
                continue
            
            if not raw_data or len(raw_data) < 2:
                st.html(f"""<style>.st-key-white_container_small_{assessment}_{i}_{i}{{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 1%;}}</style>""")
                with st.container(key=f"white_container_small_{assessment}_{i}_{i}"):
                    st.write(f"**No {assessment} results were found.**")
                continue

            headers = raw_data[0]

            # Make headers unique
            seen, unique_headers = {}, []
            for h in headers:
                c = seen.get(h, 0)
                unique_headers.append(h if c == 0 else f"{h} ({c})")
                seen[h] = c + 1

            df = pd.DataFrame(raw_data[1:], columns=unique_headers)

            # --- Detect Program/Org Name column ---
            candidate_keywords = [
                "organization name",
                "program name",
                "your org",
                "site or organization",
                "please enter the organization name you logged in with",
            ]
            Program_Name = None
            for col in df.columns:
                if any(k in col.strip().lower() for k in candidate_keywords):
                    Program_Name = col
                    break

            if not Program_Name:
                st.error("Could not find the column with organization/program name. Please check your form question titles.")
                continue

            # --- Find Overall Score columns (case-insensitive) ---
            overall_score_cols = [c for c in df.columns if "overall score" in c.strip().lower()]
            if not overall_score_cols:
                st.write(f"**No Overall Score columns found for {assessment}.**")
                continue

            # Convert candidate columns to numeric now (avoid repetition)
            for c in overall_score_cols:
                df[c] = pd.to_numeric(df[c], errors="coerce")


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
                        standard_scores_org = {}
                        for col in torg_df.columns:
                            if "Overall Score" in col and (("Standard" not in col) or ("-" in col)):
                                continue
                            series = pd.to_numeric(torg_df[col].replace('%', '', regex=True), errors="coerce")
                            avg = series.mean()
                            if pd.notna(avg) and ("Standard" in col or "Indicator" in col):
                                standard_scores_org[col] = avg

                        # --- Display White Container per Org ---
                        w_prefix = str(uuid.uuid4())
                        wa = f"white_container_{w_prefix}"
                        st.html(f"""<style>.st-key-{wa}{{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}}</style>""")
                        st.html(f"""<style>.st-key-teal_container_{w_prefix}{{background-color: #084C61; border-radius: 20px; padding: 5%;}}</style>""")
                        if org_avg_score is not None:
                            with st.container(key=wa):
                                render_overall_score(f"{org} — {assessment}", org_avg_score, key_suffix=f"{assessment}_{org}_{i}")
                                with st.container(key=f"teal_container_{w_prefix}"):
                                    st.plotly_chart(draw_score_dial(org_avg_score, "Overall Score"), use_container_width=True)

            else:
                org_input = st.session_state.get("org_input", "")

                org_clean = org_input.strip().lower()
                # Regular view for non-admins
                if not is_admin:
                    # Determine the email to match from session
                    user_email = norm(st.session_state.get("user_email", ""))

                    # Ensure the "Contact Email" column exists
                    contact_email_col = None
                    for col in df.columns:
                        if "contact email" in col.strip().lower():
                            contact_email_col = col
                            break

                    if not contact_email_col:
                        st.error("Could not find the Contact Email column in the sheet.")
                        continue

                    # Clean and filter based on Contact Email
                    df["__email_clean__"] = df[contact_email_col].astype(str).apply(norm)
                    matched = df[df["__email_clean__"] == user_email].copy()

                else:
                    # Regular org view: filter to the user's org and show a single average
                    df["__org_clean__"] = df[Program_Name].astype(str).apply(norm)
                    org_clean = norm(org_input)
                    matched = df[df["__org_clean__"] == org_clean].copy()

                    # Also try multi-org rows if direct match yielded nothing
                    if matched.empty:
                        df["__orgs__"] = df[Program_Name].apply(split_orgs)
                        matched = df[df["__orgs__"].apply(lambda lst: any(norm(x) == org_clean for x in lst))]

                # Show no-results message if still no match
                if matched.empty:
                    st.html(f"""
                        <div class="score-card">
                            <div class="score-card__title">
                                <span class="clamp">No {assessment} results were found.</span>
                            </div>
                        </div>
                    """)
                    continue

                # Gather all numeric overall scores across all rows/cols
                vals = []
                for c in overall_score_cols:
                    vals.extend(pd.to_numeric(matched[c], errors="coerce").dropna().astype(float).tolist())

                if not vals:
                    st.html(f"""
                        <div class="score-card">
                            <div class="score-card__title">
                                <span class="clamp">No {assessment} results were found.</span>
                            </div>
                        </div>
                    """)
                    continue

                avg = sum(vals) / len(vals)
                w_prefix = str(uuid.uuid4())
                wa = f"white_container_{w_prefix}"
                st.html(f"""<style>.st-key-{wa}{{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}}</style>""")
                st.html(f"""<style>.st-key-teal_container_{w_prefix}{{background-color: #084C61; border-radius: 20px; padding: 5%;}}</style>""")
                with st.container(key=wa):
                    render_overall_score(f"Average Overall Score for {assessment}", avg, key_suffix=f"{assessment}_{i}")

                    with st.container(key=f"teal_container_{w_prefix}"):
                        st.plotly_chart(draw_score_dial(avg), use_container_width=True)
             


acol, _, col1, col2, col3, col4 = st.columns([1, 5, 1, 1, 1, 1])


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
        }
        button:focus,
        button:active, 
        button:hover {
            background-color: white !important;
            color: #084C61 !important;
            outline: none;
            box-shadow: none;
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
            st.switch_page("app.py")
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
    if st.button("All Assessments", use_container_width=True):
        st.session_state["variation"] = "all"
    
render_variation_buttons()


assessment = st.session_state.get("variation", None)

if assessment == "all":
    render_all_scores(ASSESSMENTS)
elif assessment:

            # Authorize and load the sheet
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
    client = gspread.authorize(creds)
    sheet = client.open(ASSESSMENTS[assessment]["sheet_name"]).sheet1




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
        if any(keyword.strip().lower() in col_lower for keyword in candidate_keywords):
            Program_Name = col
            break

    # If no matching column found, show error
    if not Program_Name:
        st.error("Could not find the column with organization/program name. Please check your form question titles.")
        st.stop()
    # if access_level is None:
    #     access_level = st.session_state.get("access", False)
    if access_level:
        org_df = df.copy()

        
        if Program_Name in org_df.columns:

            # org_df["Extracted Orgs"] = org_df[Program_Name].fillna("").astype(str).str.strip()
            def normalize_orgs(val):
                if pd.isna(val):
                    return []
                parts = re.split(r"[;,/\n]+", str(val))
                return [p.strip() for p in parts if p and p.strip()]

            org_df["Extracted Orgs"] = org_df[Program_Name].apply(normalize_orgs)

            # Fallback: if all lists are empty, just use raw org names
            if org_df["Extracted Orgs"].apply(len).sum() == 0:
                org_df["Extracted Orgs"] = org_df[Program_Name].apply(lambda x: [x.strip()] if x else [])


            all_orgs = sorted({
                o
                for sublist in org_df["Extracted Orgs"]
                for o in sublist
                if o
            })
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
                        over_scores[org] = 1000
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
        org_input = st.session_state.get("org_input", "")

        org_clean = org_input.strip().lower()

        # Filter the DataFrame to just this org
        df = df[df["Program Name_clean"] == org_clean]

        org_df = df.copy()

        # Drop the temporary clean column
        df = df.drop(columns=["Program Name_clean"])
        
    site_name = "Are you filling out this form for a specific site? If yes, what is the site’s name?"

    if site_name not in org_df.columns:
        site_keywords = ["name of the site", "site", "the site", "which site", "site's name", "Please enter the name of the site and/or program you work at."]
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


    # Apply to org_df only (filtered by org_input earlier)
    org_df["Extracted Sites"] = org_df["Site Name"]


    # Build site dropdown options (only if admin has sites)
    all_sites = sorted(set(site for site in org_df["Extracted Sites"] if site))


    selected_contacts = []
    

    # Try converting all columns to numeric
    converted_df = df.copy()
    # Apply staff and site filters to org_df before generating charts

    chart_df = org_df.copy() 

    if st.session_state.get("user_email")!="":
        email = st.session_state.get("user_email")
    else:
        email = None

    # is_admin = st.session_state.get("is_admin", False)
    if is_admin:
        chart_df = org_df.copy()
    else:
        if email is not None:
            chart_df = reg_df[reg_df["Contact Email"].str.lower().str.strip() == email.strip().lower()]



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
                # for i, score in enumerate(score_series):
                #     if not pd.isna(score):
                #         label = f"Submission {i+1}"
                #         submissions[label] = score
                #         score_over_time.append(score)
                timestamp_col = next((col for col in org_df.columns if "timestamp" in col.lower()), None)

                # Only if timestamp column is found
                if timestamp_col and timestamp_col in org_df.columns:
                    try:
                        # Convert timestamp strings to datetime objects
                        timestamp_series = pd.to_datetime(org_df[timestamp_col], errors='coerce')
                    except Exception:
                        timestamp_series = pd.Series([pd.NaT] * len(org_df))
                else:
                    timestamp_series = pd.Series([pd.NaT] * len(org_df))

                for i, score in enumerate(score_series):
                    if not pd.isna(score):
                        ts = timestamp_series.iloc[i]
                        if pd.notna(ts):

                            label = ts.strftime("%B %d, %Y").replace(" 0", " ")
                            if label in submissions.keys():
                                label = label + f", Submission {i+1}"
                        else:
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
    
                    timestamp_col = next((col for col in torg_df.columns if "timestamp" in col.lower()), None)

                    # Only if timestamp column is found
                    if timestamp_col and timestamp_col in torg_df.columns:
                        try:
                            # Convert timestamp strings to datetime objects
                            timestamp_series = pd.to_datetime(torg_df[timestamp_col], errors='coerce')
                        except Exception:
                            timestamp_series = pd.Series([pd.NaT] * len(torg_df))
                    else:
                        timestamp_series = pd.Series([pd.NaT] * len(torg_df))

                    for i, score in enumerate(score_series):
                        if not pd.isna(score):
                            ts = timestamp_series.iloc[i]
                            if pd.notna(ts):
                                # label = ts.strftime("%B %Y")
                                label = ts.strftime("%B %d, %Y").replace(" 0", " ")
                                if label in submissions.keys():
                                    label = label + f", Submission {i+1}"
                            else:
                                label = f"Submission {i+1}"
                            label = label + f": {display_org}"
                            submissions[label] = score
                            score_over_time.append(score)
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
            

            timestamp_col = next((col for col in edf.columns if "timestamp" in col.lower()), None)

            # Only if timestamp column is found
            if timestamp_col and timestamp_col in edf.columns:
                try:
                    # Convert timestamp strings to datetime objects
                    timestamp_series = pd.to_datetime(edf[timestamp_col], errors='coerce')
                except Exception:
                    timestamp_series = pd.Series([pd.NaT] * len(edf))
            else:
                timestamp_series = pd.Series([pd.NaT] * len(edf))

            for i, score in enumerate(score_series):
                if not pd.isna(score):
                    ts = timestamp_series.iloc[i]
                    if pd.notna(ts):

                        label = ts.strftime("%B %d, %Y").replace(" 0", " ")
                        if label in submissions.keys():
                            label = label + f", Submission {i+1}"
                    else:
                        label = f"Submission {i+1}"
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




    
    def score_trend(timestamp_score_triples):
        import pandas as pd
        import plotly.express as px

        df = pd.DataFrame(timestamp_score_triples, columns=["Timestamp", "Overall Score", "Org Name"])
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        df = df.dropna(subset=["Timestamp", "Overall Score", "Org Name"])

        if df.shape[0] == 1:
            # Only one point: use formatted label as category
            df["Label"] = df["Timestamp"].dt.strftime("%B %d, %Y")
            fig = px.line(df, x="Label", y="Overall Score", markers=True, color_discrete_sequence=[
                    "#084C61", "#0F6B75", "#138D90", "#56A3A6", "#A7D4D5", "#CBE8E8", "#E6F5F5"
                ])
            fig.update_layout(
                xaxis_title="Date",
                height=300,
                margin=dict(l=40, r=40, t=40, b=40),
                paper_bgcolor="rgba(0,0,0,0)",
                title=dict(text="Score Over Time", font=dict(size=24)))
        else:
            fig = px.line(
                df,
                x="Timestamp",
                y="Overall Score",
                color="Org Name" if access_level else None,
                markers=True,
                color_discrete_sequence=[
                    "#084C61", "#0F6B75", "#138D90", "#56A3A6", "#A7D4D5", "#CBE8E8", "#E6F5F5"
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
    
                    
                        if access_level:
                            for org in all_orgs:
                                corg = org.rstrip()
                        
                                def row_has_org(org_list, target):
                                    target = target.strip().lower()
                                    return any(str(o).strip().lower() == target for o in (org_list or []))

                                porg_df = org_df[org_df["Extracted Orgs"].apply(lambda xs: row_has_org(xs, corg))]
                                if porg_df.empty:
                                    continue


                                # --- Display White Container per Org ---
                                w_prefix = str(uuid.uuid4())
                                wa = f"white_container_{w_prefix}"
                                st.html(f"""<style>.st-key-{wa}{{background-color: white; filter:drop-shadow(2px 2px 2px grey); border-radius: 20px; padding: 5%;}}</style>""")
                                st.html(f"""<style>.st-key-teal_container_{w_prefix}{{background-color: #084C61; border-radius: 20px; padding: 5%;}}</style>""")
                                with st.container(key=wa):
                                    st.write(f"#### {corg}'s Scores")

                                    if over_scores[org] is not None:
                                        with st.container(key=f"teal_container_{w_prefix}"):
                                            st.plotly_chart(draw_score_dial(over_scores[org], "Overall Score"), use_container_width=True)

                                    if standard_scores[org]:
                                        with st.expander("**Scores by Standards and Indicators**"):
                                            for label, score in standard_scores[org]:
                                                if pd.isna(score):
                                                    continue 
                                                render_score_card(sheet3_data, sheet2_data, score, label, org_name=corg)

                                    # --- Show Site Scores if Available ---
                                    site_col = None
                                    for col in ["Extracted Sites", "Site Name"]:
                                        if col in porg_df.columns and porg_df[col].dropna().apply(lambda x: isinstance(x, str)).any():
                                            site_col = porg_df[col]
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
                                                site_df = porg_df[site_col.astype(str).str.strip().str.lower() == norm_site]
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
                        
                        timestamp_col = next((col for col in org_df.columns if "timestamp" in col.lower()), None)
                        timestamp_score_pairs = []

                        if timestamp_col:
                            timestamps = pd.to_datetime(org_df[timestamp_col], errors='coerce')

                            # Normalize Extracted Orgs first (if not done already)
                            if "Extracted Orgs" in org_df.columns:
                                org_df["__normalized_extracted_orgs__"] = org_df["Extracted Orgs"].apply(
                                    lambda x: x[0] if isinstance(x, list) and x else str(x)
                                )
                            else:
                                org_df["__normalized_extracted_orgs__"] = st.session_state.get("org_input", "Unknown Org")

                            timestamp_score_triples = []  # (timestamp, score, org_name)

                            for idx, row in org_df.iterrows():
                
                                ts = pd.to_datetime(row[timestamp_col], errors="coerce")
                                if pd.isna(ts):
                                    continue
                                org_name = row["__normalized_extracted_orgs__"]
                                for col in org_df.columns:
                                    if "Overall Score" in col:
                                        score = pd.to_numeric(row[col], errors="coerce")
                                        if pd.notna(score):
                                            timestamp_score_triples.append((ts, score, org_name))

    
                        fig = score_trend(timestamp_score_triples)
                        st.plotly_chart(fig, use_container_width=True)
                        if access_level:
                            st.write(f"This chart shows the overall scores for {assessment} by organization over time.")
                        else:
                            st.write(f"This chart shows {org_input}'s overall scores for {assessment} over time.")
                        with st.expander("**Overall Score Over Time**"):
                            for label, score in submissions.items():
                                if pd.isna(score):
                                    continue
                                render_score_card(sheet3_data, sheet2_data, score, label)


                with col3:
                    with st.container(key ="white_container_3"):
                        st.plotly_chart(staff_bar(staff_scores_num), use_container_width=True)
                        st.write(f"This chart shows the overall score for {assessment} for each staff member.")
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
                        st.write(f"This chart shows your score for each Standard and Indicator in {assessment}.")
                        with st.expander("**Category Descriptions**"):
                            for label in standard_scores:
                                desc(sheet3_data, label)

                        
                with col3:
                    with st.container(key ="white_container_2"):
                        timestamp_score_triples = []
                        org_name = st.session_state.get("org_input", "Unknown Org")
                        subms = {}
                        for i, score in enumerate(score_series):
                            if not pd.isna(score):
                                ts = timestamp_series.iloc[i]
                                if pd.notna(ts):
                                    timestamp_score_triples.append((ts, score, org_name))
                        fig = score_trend(timestamp_score_triples)
                        st.plotly_chart(fig, use_container_width=True)
                        st.write(f"This chart shows your overall score(s) for {assessment} over time.")
                        with st.expander("**Overall Score by Submission**"):
                            for label, score in submissions.items():
                                if pd.isna(score):
                                    continue
                                render_score_card(sheet3_data, sheet2_data, score, label)