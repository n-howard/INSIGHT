import streamlit as st 
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from google_auth import login, fetch_token, get_user_info
from urllib.parse import urlparse, parse_qs


# -------- PAGE SETUP --------
st.set_page_config(page_title="INSIGHT", layout="wide")
st.title("INSIGHT")

# Initialize session state
st.session_state.setdefault("oauth_state", None)

# Check for OAuth redirect
query_params = st.query_params
if "code" in query_params:
    code = query_params["code"]
    token = fetch_token(code)
    if token:
        user_info = get_user_info(token)
        st.write("👤 User Info:")
        st.json(user_info)
    else:
        st.warning("Token fetch failed. Please try logging in again.")
else:
    login()


if "org" not in st.session_state:
    st.session_state.org = st.selectbox("Select your Organization", ["Org A", "Org B", "Org C"])
    st.session_state.site = st.selectbox("Select your Site", ["Main Campus", "North Site", "South Site"])
    if st.button("Continue"):
        st.rerun()
# -------- CONFIGURATION --------
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



# -------- SIDEBAR NAVIGATION --------
assessment = st.sidebar.selectbox("Choose an Assessment", list(ASSESSMENTS.keys()))
mode = st.sidebar.radio("Mode", ["📝 Self-Assess", "📈 View Results"])

# -------- SELF-ASSESSMENT MODE --------
if mode == "📝 Self-Assess":
    st.subheader(f"{assessment} – Self-Assessment Form")
    st.components.v1.iframe(ASSESSMENTS[assessment]["form_url"], height=800, scrolling=True)

# -------- VIEW RESULTS MODE --------
elif mode == "📈 View Results":
    st.subheader(f"{assessment} – Results Dashboard")

    try:
        # Authorize and load the sheet
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open(ASSESSMENTS[assessment]["sheet_name"]).sheet1

        # Load raw data and headers
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

        # Try converting all columns to numeric
        converted_df = df.copy()
        for col in converted_df.columns:
            converted_df[col] = pd.to_numeric(converted_df[col], errors="coerce")

        # Keep only mostly-numeric columns (60%+ numeric values)
        # Exclude columns containing any of these substrings (case-insensitive)
        EXCLUDED_SUBSTRINGS = ["How many students", "Timestamp"]

        numeric_cols = [
            col for col in converted_df.columns
            if converted_df[col].notna().mean() >= 0.6 and not any(sub.lower() in col.lower() for sub in EXCLUDED_SUBSTRINGS)
        ]

        filtered_df = converted_df[numeric_cols].dropna(axis=1, how="all")

        # Show full raw data
        st.subheader("📋 Full Response Table")
        st.dataframe(df)

        with st.expander("📊 Visualize Columns with Mostly Numeric Data"):
            if not filtered_df.empty:
                selected_col = st.selectbox("Choose a column to chart", filtered_df.columns)

                chart_type = st.radio("Select chart type", ["Bar Chart", "Line Chart", "Histogram", "Box Plot"])
                data_series = filtered_df[selected_col].dropna()

                if chart_type == "Bar Chart":
                    st.bar_chart(data_series.value_counts().sort_index())

                elif chart_type == "Line Chart":
                    st.line_chart(data_series.reset_index(drop=True))

                elif chart_type == "Histogram":
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots()
                    ax.hist(data_series, bins=10)
                    ax.set_title(f"Histogram of {selected_col}")
                    ax.set_xlabel(selected_col)
                    ax.set_ylabel("Frequency")
                    st.pyplot(fig)

                elif chart_type == "Box Plot":
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots()
                    ax.boxplot(data_series)
                    ax.set_title(f"Box Plot of {selected_col}")
                    ax.set_ylabel(selected_col)
                    st.pyplot(fig)

                # Summary stats
                st.markdown("### 📈 Summary Statistics")
                st.write(data_series.describe())

                # Optional: multi-column line chart
                st.markdown("### 📊 Multi-Column Line Chart")
                multi_cols = st.multiselect("Select multiple numeric columns", filtered_df.columns)
                if multi_cols:
                    st.line_chart(filtered_df[multi_cols])

            else:
                st.warning("No mostly-numeric columns found.")

    except Exception as e:
        st.error(f"Error accessing or visualizing data: {e}")


