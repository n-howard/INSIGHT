import streamlit as st 
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from pages.google_auth import login, fetch_token, get_user_info
from urllib.parse import urlparse, parse_qs
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
import numpy as np
# -------- CONFIGURATION --------

st.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }
    </style>"""
    "<h1 style='text-align: center; font-size: 65px; font-weight: 900; font-family: Poppins; margin-bottom: 0px'>INSIGHT</h1>"
)


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
mode = st.sidebar.radio("Mode", ["Self-Assess", "View Results"])

# -------- SELF-ASSESSMENT MODE --------
if mode == "Self-Assess":
    # st.subheader(f"{assessment} Self-Assessment")
    selfSes = assessment + " Self-Assessment"
    thisStyle = f"""<h3 style='text-align: center; font-size: 35px; font-weight: 600; font-family: Poppins;'>{selfSes}</h3>"""
    st.html(
        thisStyle
        # "<h3 style='text-align: center; font-size: 40px; font-weight: 500; font-family: Poppins;'>{selfSes}</h3>"
    )
    st.components.v1.iframe(ASSESSMENTS[assessment]["form_url"], height=800, scrolling=True)

# -------- VIEW RESULTS MODE --------
elif mode == "View Results":
    st.subheader(f"{assessment} Results Dashboard")
    

    try:
        # Authorize and load the sheet
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open(ASSESSMENTS[assessment]["sheet_name"]).sheet1


        # Access the value stored in session state
        org_input = st.session_state.get("org_input", "")

        if not org_input:
            st.warning("Please enter your organization name on the main page.")
            st.stop()  # Stop execution if no org name
    
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

        if "Program Name" not in df.columns:
            st.error("❌ Column 'Program Name' not found in the data.")
            st.stop()

        # Clean both Program Name column and org_input for flexible comparison
        df["Program Name_clean"] = df["Program Name"].str.strip().str.lower()
        org_clean = org_input.strip().lower()

        # Filter the DataFrame to just this org
        df = df[df["Program Name_clean"] == org_clean]

        # Drop the temporary clean column
        df = df.drop(columns=["Program Name_clean"])

       # --- MULTI-FILTER CONTROLS ---
        # Normalize Site Name
        if "Site Name" in df.columns:
            df["Site Name"] = df["Site Name"].fillna("").astype(str).str.strip()
        else:
            df["Site Name"] = ""  # Add a blank column if missing

        # Get site name from session (if any)
        site_input = st.session_state.get("site_input", "").strip()

        # Let user choose to see overall or just their site
        site_filter_option = st.radio(
            "View data for:",
            ["Overall", "This Site Only"],
            index=0 if not site_input else 1
        )

        # Apply site filter only if selected and site_input is available
        if site_filter_option == "This Site Only":
            if site_input:
                df = df[df["Site Name"].str.lower() == site_input.lower()]
            else:
                st.warning("You didn't enter a Site Name at login, so no filter can be applied.")

        contact_options = sorted(df["Contact Name"].dropna().unique())


        selected_contacts = st.multiselect("Filter by Contact Name (optional)", contact_options)

        if selected_contacts:
            df = df[df["Contact Name"].isin(selected_contacts)]

        # Try converting all columns to numeric
        converted_df = df.copy()
        for col in converted_df.columns:
            converted_df[col] = pd.to_numeric(converted_df[col], errors="coerce")

        # Keep only mostly-numeric columns (60%+ numeric values)
        # Exclude columns containing any of these substrings (case-insensitive)
        EXCLUDED_SUBSTRINGS = ["How many students", "Timestamp"]

        def is_numeric_column(series):
            # Must have mostly numeric values and no comma-separated strings
            return (
                series.notna().mean() >= 0.6 and
                series.apply(lambda x: isinstance(x, (int, float)) or (isinstance(x, str) and "," not in x)).all()
            )

        numeric_cols = [
            col for col in converted_df.columns
            if is_numeric_column(converted_df[col]) and not any(sub.lower() in col.lower() for sub in EXCLUDED_SUBSTRINGS)
        ]

        filtered_df = converted_df[numeric_cols].dropna(axis=1, how="all")
    

        
        if not filtered_df.empty:
            # multi column chart with multiple types of charting
            st.markdown("### Multi-Score Chart")
            multi_cols = st.multiselect("Select at least one score type to chart", filtered_df.columns)

            if multi_cols:
                chart_type = st.radio("Select chart type", ["Bar Chart", "Line Chart", "Histogram"])
                data_series = filtered_df[multi_cols].dropna().reset_index(drop=True)

                if chart_type == "Bar Chart":
                    if len(multi_cols) == 1:
                    # --- One column: plot each individual score as a bar ---
                        col = multi_cols[0]
                        data_series = filtered_df[col].dropna()

                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.bar(range(len(data_series)), data_series, width=0.4)
                        ax.set_title(f"{col} Scores", fontsize=14)
                        ax.set_xlabel("Response Index", fontsize=12)
                        ax.set_ylabel("Score", fontsize=12)
                        ax.grid(axis="y", linestyle="--", alpha=0.6)
                        plt.xticks([])  # Hide x-axis tick labels for simplicity

                        for i, v in enumerate(data_series):
                            ax.text(i, v + 0.1, f"{v:.1f}", ha='center', fontsize=8)

                        st.pyplot(fig)

                    else:
                        # --- Multiple columns: show average score for each column ---
                        col_means = filtered_df[multi_cols].mean()

                        fig, ax = plt.subplots(figsize=(10, 5))
                        bars = ax.bar(col_means.index, col_means.values, width=0.5)

                        ax.set_title("Average Score by Category", fontsize=14)
                        ax.set_ylabel("Average Score", fontsize=12)
                        ax.grid(axis="y", linestyle="--", alpha=0.6)
                        plt.xticks(rotation=45, ha="right")

                        for bar in bars:
                            height = bar.get_height()
                            ax.annotate(f'{height:.1f}',
                                        xy=(bar.get_x() + bar.get_width() / 2, height),
                                        xytext=(0, 3),
                                        textcoords="offset points",
                                        ha='center', va='bottom', fontsize=10)

                        st.pyplot(fig)


                elif chart_type == "Line Chart":
                    fig, ax = plt.subplots()
                    for col in filtered_df[multi_cols].columns:
                        ax.plot(filtered_df.index, filtered_df[col], marker='o', label=col)

                    ax.set_title("Line Chart")
                    ax.set_xlabel("Index")
                    ax.set_ylabel("Values")
                    ax.legend()
                    st.pyplot(fig)

                elif chart_type == "Histogram":
                    fig, ax = plt.subplots()
                    ax.hist(data_series.values, bins=10, label=multi_cols)
                    ax.set_title("Histogram")
                    ax.set_xlabel("Value")
                    ax.set_ylabel("Frequency")
                    ax.legend()
                    st.pyplot(fig)

                st.markdown("### Your Score(s)")
                st.write(data_series)

            else:
                st.warning("Please select at least one column to display the chart.")

    except Exception as e:
        st.error(f"Error accessing or visualizing data: {e}")
