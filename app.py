import streamlit as st 
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from urllib.parse import urlparse, parse_qs
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
import gspread
from pages.google_auth import login, fetch_token, get_user_info




# -------- PAGE SETUP --------
st.set_page_config(page_title="INSIGHT", layout="wide")
# st.title("INSIGHT")
st.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }
    </style>"""
    "<h1 style='text-align: center; font-size: 65px; font-weight: 900; font-family: Poppins; margin-bottom: 0px'>INSIGHT</h1>"
)


st.set_option("client.showSidebarNavigation", False)


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

def google_login():
    # Initialize session state
    st.session_state.setdefault("oauth_state", None)

    # Check for OAuth redirect
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        token = fetch_token(code)
        if token:
            st.success("Login successful! Redirecting to Home Page...")
            st.query_params  # Clear code from URL
            st.switch_page("pages/homePage.py")
            user_info = get_user_info(token)
            st.write("User Info:")
            st.json(user_info)
        else:
            st.warning("Token fetch failed. Please try logging in again.")
    else:
        st.switch_page("pages/google_auth.py")
        st.login()


def start_page():
    if "org" not in st.session_state:
        org_input = st.text_input("Type the Name of Your Organization")
        site_input = st.text_input("Type the Name of Your Site, or N/A if Your Program Only Has One Site")
        if st.button("Continue"):
            set_org(org_input, site_input)

try:
#         # Authorize and load the sheet
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    def set_org(org_input, site_input):
        tally = 0
        for assessment in ASSESSMENTS:
            sheet = client.open(ASSESSMENTS[assessment]["sheet_name"]).sheet1
            column_values = sheet.col_values(6)
            if org_input.lower() in [val.lower() for val in column_values]:
                st.session_state.org = org_input
                st.session_state.site = site_input
                break
            else:
                tally = tally + 1
        if tally != 6:
            google_login()
            st.rerun()
        else:
            selection = st.selectbox("INSIGHT could not find results with that organization's name. Would you like to create a new organization portal or enter a different organization name?", ["Create New Organization Portal", "Re-Enter Name"])
            if st.button("Continue"):
                if selection == "Create New Organization Portal":
                    google_login()
                    st.rerun()
                else:
                    start_page()
except Exception as e:
    st.error(f"Error accessing or visualizing data: {e}")

start_page()







# # -------- SIDEBAR NAVIGATION --------
# assessment = st.sidebar.selectbox("Choose an Assessment", list(ASSESSMENTS.keys()))
# mode = st.sidebar.radio("Mode", ["📝 Self-Assess", "📈 View Results"])

# # -------- SELF-ASSESSMENT MODE --------
# if mode == "📝 Self-Assess":
#     st.subheader(f"{assessment} – Self-Assessment Form")
#     st.components.v1.iframe(ASSESSMENTS[assessment]["form_url"], height=800, scrolling=True)

# # -------- VIEW RESULTS MODE --------
# elif mode == "📈 View Results":
#     st.subheader(f"{assessment} – Results Dashboard")

#     try:
#         # Authorize and load the sheet
#         scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#         creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
#         client = gspread.authorize(creds)
#         sheet = client.open(ASSESSMENTS[assessment]["sheet_name"]).sheet1

#         # Load raw data and headers
#         raw_data = sheet.get_all_values()
#         headers = raw_data[0]

#         # Make headers unique to avoid duplicate error
#         seen = {}
#         unique_headers = []
#         for h in headers:
#             if h in seen:
#                 seen[h] += 1
#                 unique_headers.append(f"{h} ({seen[h]})")
#             else:
#                 seen[h] = 0
#                 unique_headers.append(h)

#         # Create DataFrame
#         df = pd.DataFrame(raw_data[1:], columns=unique_headers)

#         # Try converting all columns to numeric
#         converted_df = df.copy()
#         for col in converted_df.columns:
#             converted_df[col] = pd.to_numeric(converted_df[col], errors="coerce")

#         # Keep only mostly-numeric columns (60%+ numeric values)
#         # Exclude columns containing any of these substrings (case-insensitive)
#         EXCLUDED_SUBSTRINGS = ["How many students", "Timestamp"]

#         numeric_cols = [
#             col for col in converted_df.columns
#             if converted_df[col].notna().mean() >= 0.6 and not any(sub.lower() in col.lower() for sub in EXCLUDED_SUBSTRINGS)
#         ]

#         filtered_df = converted_df[numeric_cols].dropna(axis=1, how="all")

#         # Show full raw data
#         st.subheader("📋 Full Response Table")
#         st.dataframe(df)

#         with st.expander("📊 Visualize Columns with Mostly Numeric Data"):
#             if not filtered_df.empty:
#                 selected_col = st.selectbox("Choose a column to chart", filtered_df.columns)

#                 chart_type = st.radio("Select chart type", ["Bar Chart", "Line Chart", "Histogram", "Box Plot"])
#                 data_series = filtered_df[selected_col].dropna()

#                 if chart_type == "Bar Chart":
#                     st.bar_chart(data_series.value_counts().sort_index())

#                 elif chart_type == "Line Chart":
#                     st.line_chart(data_series.reset_index(drop=True))

#                 elif chart_type == "Histogram":
#                     import matplotlib.pyplot as plt
#                     fig, ax = plt.subplots()
#                     ax.hist(data_series, bins=10)
#                     ax.set_title(f"Histogram of {selected_col}")
#                     ax.set_xlabel(selected_col)
#                     ax.set_ylabel("Frequency")
#                     st.pyplot(fig)

#                 elif chart_type == "Box Plot":
#                     import matplotlib.pyplot as plt
#                     fig, ax = plt.subplots()
#                     ax.boxplot(data_series)
#                     ax.set_title(f"Box Plot of {selected_col}")
#                     ax.set_ylabel(selected_col)
#                     st.pyplot(fig)

#                 # Summary stats
#                 st.markdown("### 📈 Summary Statistics")
#                 st.write(data_series.describe())

#                 # Optional: multi-column line chart
#                 st.markdown("### 📊 Multi-Column Line Chart")
#                 multi_cols = st.multiselect("Select multiple numeric columns", filtered_df.columns)
#                 if multi_cols:
#                     st.line_chart(filtered_df[multi_cols])

#             else:
#                 st.warning("No mostly-numeric columns found.")

#     except Exception as e:
#         st.error(f"Error accessing or visualizing data: {e}")


