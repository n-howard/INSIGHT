import streamlit as st 
st.set_page_config(page_title="INSIGHT", layout="wide", page_icon="./oask_short_logo.png", initial_sidebar_state="collapsed" )
from streamlit_navigation_bar import st_navbar
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from pages.google_auth import login, fetch_token, get_user_info
from urllib.parse import urlparse, parse_qs
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
import numpy as np
import random
from tkinter import * 
from tkinter.ttk import *
from pages.menu import menu_with_redirect
import plotly.express as px
import os

logo = st.logo("./oask_light_mode_tagline.png", size="large", link="https://oregonask.org/")

# pages = ["Home", "Self-Assess", "View Results", "Select Form"]
# styles = {
#     "nav": {
#         "background-color": "#56a3a6",
#         "height": "7vh"
#     }
# }


# page = st_navbar(pages, styles=styles)

with open("./styles.css") as f:
    css = f.read()

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


# # -------- BUTTON-BASED NAVIGATION --------

# # Initialize session state for assessment and mode
# if "selected_assessment" not in st.session_state:
#     st.session_state.selected_assessment = None

# if "selected_mode" not in st.session_state:
#     st.session_state.selected_mode = None



# # mode = st.session_state.selected_mode #initializing mode as a global variable
# # assessment = st.session_state.selected_assessment


# def choose_assess(assessment_name):
#     st.session_state.selected_assessment = assessment_name
#     global assessment
#     assessment = st.session_state.selected_assessment
#     return assessment



# def choose_mode(this_mode):
#     st.session_state.selected_mode = this_mode
#     global mode
#     mode = st.session_state.selected_mode
#     return mode

# chosen = False
# # st.markdown(f"## {st.session_state.selected_assessment}")
# st.markdown("## Choose a Mode")


# st.html(f"""
#     <style>{css}</style>
#     <div class="row">
#         <div class="column"><button class="button" onclick={choose_mode("Self-Assess")}>Self-Assess</button></div>
#         <div class="column"><button class="button" onclick={choose_mode("View Results")}>View Results</button></div>
#     </div>
# """)


    


# if mode!= None: 
#         st.markdown("## Choose an Assessment")
#         assess_list = []
#         for i, (assessment_name, details) in enumerate(ASSESSMENTS.items()):
#             assess_list.append(assessment_name)
#         for i in range(3):
#             curr_assess = assess_list[i]
#             next_assess = assess_list[i+3]
#             st.html(f"""
#                 <style>{css}</style>
#                 <div class="row">
#                     <div class="column"><button class="button" onclick={choose_assess(curr_assess)}>{curr_assess}</button></div>
#                     <div class="column"><button class="button" onclick={choose_assess(next_assess)}>{next_assess}</button></div>
#                 </div>
#             """)    

# # Show buttons only if no assessment is selected
# # if mode != None and (st.session_state.selected_assessment == None or st.button("Select Form", use_container_width=True)):
# #     st.session_state.selected_assessment = None

# #     st.markdown("## Choose an Assessment")
# #     cols = st.columns(2)
# #     for i, (assessment_name, details) in enumerate(ASSESSMENTS.items()):
# #         with cols[i % 2]:
# #             if st.button(assessment_name, use_container_width=True):
# #                 st.session_state.selected_assessment = assessment_name
# #                 st.rerun()



# # if st.session_state.selected_assessment and not st.session_state.selected_mode:
# #     # st.markdown(f"## {st.session_state.selected_assessment}")
# #     mode = st.selectbox("Choose mode", ("Self-Assess", "View Results"))
    




# Initialize session state for assessment and mode
if "selected_assessment" not in st.session_state:
    st.session_state.selected_assessment = None

if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = None

mode = st.session_state.selected_mode #initializing mode as a global variable

# cols = st.columns(2)
# mode_opts = ["Self-Assess", "View Results"]
# for i in range(2):
#     this_mode = mode_opts[i]
#     with cols[i%2]:
#         if st.button(this_mode, use_container_width=True):
#             st.session_state.selected_mode = this_mode

#     #    st.session_state.selected_mode = st.selectbox("Choose mode", ("Self-Assess", "View Results"))
# mode = st.session_state.selected_mode


# Show buttons only if no assessment is selected
if st.session_state.selected_assessment == None or st.button("Select a Form", use_container_width=True):
    st.session_state.selected_mode = None
    st.session_state.selected_assessment = None
    mode = None

    st.markdown("## Choose an Assessment")
    cols = st.columns(2)
    for i, (assessment_name, details) in enumerate(ASSESSMENTS.items()):
        with cols[i % 2]:
            if st.button(assessment_name, use_container_width=True):
                st.session_state.selected_assessment = assessment_name
                st.rerun()

assessment = st.session_state.selected_assessment

if assessment != None:
    if st.session_state.selected_mode==None:
        st.session_state.selected_mode = "Self-Assess"
    cols = st.columns(2)
    mode_opts = ["Self-Assess", "View Results"]
    for i in range(2):
        this_mode = mode_opts[i]
        with cols[i%2]:
            if st.button(this_mode, use_container_width=True):
                st.session_state.selected_mode = this_mode

    #    st.session_state.selected_mode = st.selectbox("Choose mode", ("Self-Assess", "View Results"))
mode = st.session_state.selected_mode










# if st.session_state.selected_assessment and not st.session_state.selected_mode:
#     # st.markdown(f"## {st.session_state.selected_assessment}")
#     mode = st.selectbox("Choose mode", ("Self-Assess", "View Results"))
    




# -------- SELF-ASSESSMENT MODE --------

if (mode == "Self-Assess") and assessment != None:
    # st.subheader(f"{assessment} Self-Assessment")
    selfSes = assessment + " Self-Assessment"
    thisStyle = f"""<h3 style='text-align: center; font-size: 35px; font-weight: 600; font-family: Poppins;'>{selfSes}</h3>"""
    st.html(
        thisStyle
        # "<h3 style='text-align: center; font-size: 40px; font-weight: 500; font-family: Poppins;'>{selfSes}</h3>"
    )
    st.components.v1.iframe(ASSESSMENTS[assessment]["form_url"], height=800, scrolling=True)


# -------- VIEW RESULTS MODE --------
elif (mode == "View Results") and assessment != None:
    st.subheader(f"{assessment} Results Dashboard")
    

    try:
        # Authorize and load the sheet
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open(ASSESSMENTS[assessment]["sheet_name"]).sheet1


        # Access the value stored in session state
        org_input = st.session_state.get("org_input", "")
        admin_input = st.session_state.get("admin_input", "")

        if not org_input:
            st.warning("Please enter your organization name on the main page.")
            menu_with_redirect()  # Ask for org name again if reloaded
    
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
            st.error("Column 'Program Name' not found in the data.")
            st.stop()

        # Clean both Program Name column and org_input for flexible comparison
        df["Program Name_clean"] = df["Program Name"].str.strip().str.lower()
        org_clean = org_input.strip().lower()

        # Filter the DataFrame to just this org
        df = df[df["Program Name_clean"] == org_clean]

        org_df = df.copy()

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
        
        # Step 1: Confirm login and fetch user email
        if "token" in st.session_state:
            user_info = get_user_info(st.session_state.token)
            email = user_info.get("email", None)
        else:
            email = None

        # Step 2: Display latest submission
        if st.button("View My Most Recent Submission", use_container_width=True) and email:
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
            user_submissions = df[df["Contact Email"] == email]

            if not user_submissions.empty:
                latest = user_submissions.sort_values("Timestamp", ascending=False).iloc[0]
                st.markdown("### Your Most Recent Submission")
                st.markdown(f"**Submitted on:** {latest['Timestamp'].strftime('%B %d, %Y at %I:%M %p')}")

                st.markdown("---")
                st.markdown("#### Your Scores:")
                for col in latest.index:
                    if any(keyword in col for keyword in ["Score", "Standard", "Indicator"]):
                        score = latest[col]
                        # Display as percent if it's a percent string
                        if isinstance(score, str) and "%" in score:
                            st.markdown(f"- **{col}**: {score}")
                        else:
                            try:
                                num = float(score)
                                if "percent" in col.lower():
                                    st.markdown(f"- **{col}**: {num:.0f}%")
                                else:
                                    st.markdown(f"- **{col}**: {num:.2f}")
                            except:
                                st.markdown(f"- **{col}**: {score}")
            else:
                st.info("You haven't submitted a form yet.")

        elif not email:
            st.warning("Please log in with Google to view your submission.")
            menu_with_redirect()

        colors=["#cee4e4","#edd268","#b7cbd0","#f6e9b6","#87bdc0","#8499a2", 
            "#4f6d7a", "#db504a", "#abd1d1", "#ddeced", "#7a919c", "#e88f8c", "#80babd", "#457887", "#ffc757",
            "#ffd98f", "#f2bab8"]

        if not filtered_df.empty:
            # multi column chart with multiple types of charting
            st.markdown("#### Score Chart")
            multi_cols = st.multiselect("Select at least one score type to chart", filtered_df.columns)

            if multi_cols:
                data_series = filtered_df[multi_cols].dropna().reset_index(drop=True)
                types = []
                if len(data_series.index)==1:
                    types = ["Bar Chart", "Scatter Plot"]
                else:
                    types = ["Bar Chart", "Line Chart", "Area"]
                chart_type = st.selectbox("Select chart type", types)
                if chart_type == "Bar Chart":
                    # colors=["#cee4e4","#edd268","#b7cbd0","#f6e9b6","#87bdc0","#8499a2", "#4f6d7a", "#db504a", "#89a436", "#e3b505", "#ba29a7", "#f76649", "#fec841"]
                    if len(multi_cols) == 1:
                        onecolor = random.sample(colors, k=1)
                        col = multi_cols[0]
                        value_counts = data_series[col].value_counts().sort_index()
                        st.bar_chart(value_counts, color=onecolor)
                    else:
                        if len(multi_cols) > len(colors):
                            colorlist = random.choices(colors, k=len(multi_cols))
                            st.bar_chart(filtered_df[multi_cols].mean().to_frame().T, color=colorlist, stack = False)
                        else:
                            colorlist = random.sample(colors, k=len(multi_cols))
                            st.bar_chart(filtered_df[multi_cols].mean().to_frame().T, color=colorlist, stack = False)
                        # colorlist = random.choices(colors, k=len(multi_cols))
                        # st.bar_chart(filtered_df[multi_cols].mean().to_frame().T, color=colorlist, stack = False)

                elif chart_type == "Line Chart" or chart_type == "Scatter Plot":
                    # colors=["#cee4e4","#edd268","#b7cbd0","#f6e9b6","#87bdc0","#8499a2", "#4f6d7a", "#db504a", "#ffffff", "#e3b505"]
                    # colorlist = random.sample(colors, k=len(multi_cols))
                    if len(multi_cols) > len(colors):
                        colorlist = random.choices(colors, k=len(multi_cols))
                        if len(data_series.index)==1:
                            st.scatter_chart(data_series, color=colorlist)
                        else:
                            st.line_chart(data_series, color=colorlist)

                    else:
                        colorlist = random.sample(colors, k=len(multi_cols))
                        if len(data_series.index)==1:
                            st.scatter_chart(data_series, color=colorlist)
                        else:
                            st.line_chart(data_series, color=colorlist)
                    # if len(data_series.index)==1:
                    #     st.scatter_chart(data_series, color=colorlist)
                    # else:
                    #     st.line_chart(data_series, color=colorlist)

                # elif chart_type == "Histogram":
                #     fig, ax = plt.subplots()
                #     ax.hist(data_series.values, bins=10, label=multi_cols)
                #     ax.set_title("Histogram")
                #     ax.set_xlabel("Value")
                #     ax.set_ylabel("Frequency")
                #     ax.legend()
                #     st.pyplot(fig)

                elif chart_type == "Area":
                    # colors=["#cee4e4","#edd268","#b7cbd0","#f6e9b6","#87bdc0","#8499a2", "#4f6d7a", "#db504a", "#ffffff", "#e3b505"]
                    # colorlist = random.sample(colors, k=len(multi_cols))
                    if len(multi_cols) > len(colors):
                        colorlist = random.choices(colors, k=len(multi_cols))
                        st.area_chart(data_series, color=colorlist)
                    else:
                        colorlist = random.sample(colors, k=len(multi_cols))
                        st.area_chart(data_series, color=colorlist)
                    # st.area_chart(data_series, color=colorlist)

                # st.markdown("### Your Scores")
                # st.write(data_series)

                
                    

            else:
                st.warning("Please select at least one column to display the chart.")

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
                overall_av = sum(all_scores) / len(all_scores)
            else:
                overall_av = 0  # fallback value or message
# 
   
            # Build the staff-specific average score (one number)
            staff_scores = []

            if selected_contacts:
                for contact in selected_contacts:
                    contact_df = org_df[org_df["Contact Name"] == contact]
                    if contact_df.empty:
                        continue

                    overall_score_cols = [col for col in contact_df.columns if "Overall Score" in col]

                    for col in overall_score_cols:
                        # Add all numeric values from this staff’s column to the total list
                        series = pd.to_numeric(contact_df[col], errors="coerce").dropna()
                        staff_scores.extend(series.tolist())

            if staff_scores:
                staff_overall_avg = sum(staff_scores) / len(staff_scores)
                staff_score_html = f"<h1>{staff_overall_avg: .2f}</h1>"
            else:
                staff_score_html = f"<h1>{overall_av: .2f}</h1>"




            text_var = ""
            for column in org_df:
                if "Overall Score" in column:
                    continue

                # Clean and convert
                series = org_df[column].replace('%', '', regex=True)
                series = pd.to_numeric(series, errors="coerce")
                av = series.mean()
                name = ""
                if pd.notna(av):
                    if "Standard" in column:
                        if "percent" in column.lower() or "%" in column:
                            name = f"<div class='p2' style='font-weight: 600;'>Organization Average {column}: {av:.0f}%</div><br><br>"
                        elif 0 < av < 1:
                            name = f"<div class='p2' style='font-weight: 600;'>Organization Average {column}: {av * 100:.0f}%</div><br><br>"
                        else:
                            name = f"<div class='p2' style='font-weight: 600;'>Organization Average {column}: {av:.2f}</div><br><br>"
                    elif "Indicator" in column:
                        name = f"<div class='p3'>Organization Average {column}: {av:.2f}</div><br><br>"

                    text_var += name

                elif "Indicator" in column:
                    name = f"<div class='p3'>Organization Average {column}: {av: .2f}</div><br><br>"
                    text_var += name

            # Step 1: Group by Contact Name
            staff_summaries = ""
            if "Contact Name" in org_df.columns:
                for contact in org_df["Contact Name"].dropna().unique():
                    contact_df = filtered_df[org_df["Contact Name"] == contact]
                    if contact_df.empty:
                        continue
                    # staff_text = f"<div style='font-size: 24px; font-weight: 800; margin-bottom: 10px;'>{contact}</div>"
                    staff_text = ""
                    for column in contact_df.columns:
                        avg = pd.to_numeric(contact_df[column], errors="coerce").mean()
                        if "Overall Score" in column:
                            staff_text += f"<div class='p1' style='font-weight: 700;'>{contact}'s Average {column}: {avg: .2f}</div><br>"
                        if "Standard" in column:
                            staff_text += f"<div class='p2' style='font-weight: 600;'>{contact}'s Average {column}: {avg: .2f}</div><br>"
                        elif "Indicator" in column:
                            staff_text += f"<div class='p3'>{contact}'s Average {column}: {avg: .2f}</div><br>"
                    staff_summaries += f"<div>{staff_text}</div>"
            else:
                staff_summaries = "<div class='p1' style='margin-bottom: 2vw;'>No contact data available.</div>"


            st.html(f"""
                <style>
                    @media screen and (min-width: 768px) {{
                        .responsive-container {{
                            display: grid;
                            grid-template-columns: 1fr 1fr;
                            gap: 20px;
                        }}
                        .org-group, .staff-group {{
                            display: flex;
                            flex-direction: column;
                            gap: 20px;
                        }}
                        .equal-box {{
                            height: 500px; /* Ensures equal height */
                        }}
                        .equal-box h1 {{
                            font-size: 7rem;
                            color: black;
                            font-weight: 900;
                        }}
                        .equal-box h3 {{
                            font-size: 1.5rem;
                        }}
                        .p1 {{
                            font-size: 1.4rem;
                        }}
                        .p2 {{
                            font-size: 1.2rem;
                        }}
                        .p3 {{
                            font-size: 1.1rem;
                        }}

                    }}

                    @media screen and (max-width: 768px) {{
                        .responsive-container {{
                            display: flex;
                            flex-direction: column;
                            gap: 20px;
                        }}
                        .responsive-box {{
                            width: 100% !important;
                            gap: 20px;
                        }}
                        .org-group, .staff-group {{
                            display: flex;
                            flex-direction: column;
                            gap: 20px;
                        }}
                        .equal-box h1 {{
                            font-size: 4rem;
                            color: black;
                            font-weight: 900;
                        }}
                        .equal-box h3 {{
                            font-size: 1.2rem;
                        }}
                        .p1 {{
                            font-size: 1.1rem;
                        }}
                        .p2 {{
                            font-size: 1rem;
                        }}
                        .p3 {{
                            font-size: 0.9rem;
                        }}
                    }}
                </style>

                <div class="responsive-container">

                    <!-- Organization Section -->
                    <div class="org-group">
                        <div class="responsive-box equal-box" style="border-radius: 15px; background-color: white; color: #084c61; text-align: center;
                                display: flex; flex-direction: column; justify-content: center; filter: drop-shadow(3px 3px 5px rgba(0,0,0,0.15));
                                padding: 15px; box-sizing: border-box;">
                            <h3>Organization Average Overall Score</h3>
                            <h1>{overall_av:.2f}</h1>
                        </div>

                        <div class="responsive-box" style="border-radius: 15px; background-color: white; color: #084c61; text-align: center;
                                filter: drop-shadow(3px 3px 5px rgba(0,0,0,0.15)); padding: 15px; box-sizing: border-box;">
                            {text_var}
                        </div>
                    </div>

                    <!-- Staff Section -->
                    <div class="staff-group">
                        <div class="responsive-box equal-box" style="border-radius: 15px; background-color: white; color: #084c61; text-align: center;
                            display: flex; flex-direction: column; justify-content: center; filter: drop-shadow(3px 3px 5px rgba(0,0,0,0.15));
                            padding: 15px; box-sizing: border-box;">
                        <h3>Average Scores for Selected Staff</h3>
                        <div style="word-wrap: break-word; overflow-wrap: break-word; white-space: normal; max-width: 100%; text-align: center;">
                            {staff_score_html}
                        </div>
                    </div>


                        <div class="responsive-box" style="border-radius: 15px; background-color: white; color: #084c61; text-align: center;
                                filter: drop-shadow(3px 3px 5px rgba(0,0,0,0.15)); padding: 15px; box-sizing: border-box;">
                            {staff_summaries}
                        </div>
                    </div>

                </div>
            """)

            import streamlit.components.v1 as components

#             st.components.v1.html(f"""
#                 <style>
#                     @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

#                     body, .responsive-box {{
#                         font-family: 'Poppins', sans-serif !important;
#                     }}

#                     .equal-box {{
#                         height: 250px; 
#                         cursor: pointer;
#                     }}
#                     .hidden-section {{
#                         display: none; 
#                         overflow-y: auto;
#                         max-height: 400px;
#                     }}
#                 </style>

#                 <div class="responsive-container">

#                     <div class="responsive-box equal-box" onclick="toggleVisibility('orgDetails')" style="border-radius: 15px; background-color: white; color: #084c61;
#                             text-align: center; display: flex; flex-direction: column; justify-content: center; 
#                             filter: drop-shadow(3px 3px 5px rgba(0,0,0,0.15)); padding: 15px; box-sizing: border-box;">
#                         <h3>Organization Average Overall Score</h3>
#                         <h1>{overall_av:.2f}</h1>
#                         <p style="font-size: 14px; color: gray;">Click to view details</p>
#                     </div>

#                     <div id="orgDetails" class="responsive-box hidden-section" style="border-radius: 15px; background-color: white; color: #084c61;
#                             text-align: center; filter: drop-shadow(3px 3px 5px rgba(0,0,0,0.15)); padding: 15px; box-sizing: border-box; display: none;">
#                         {text_var}
#                     </div>

#                     <div class="responsive-box equal-box" onclick="toggleVisibility('staffDetails')" style="border-radius: 15px; background-color: white; color: #084c61;
#                             text-align: center; display: flex; flex-direction: column; justify-content: center; 
#                             filter: drop-shadow(3px 3px 5px rgba(0,0,0,0.15)); padding: 15px; box-sizing: border-box;">
#                         <h3>Average Scores for Selected Staff</h3>
#                         <h1>{staff_score_html}</h1>
#                         <p style="font-size: 14px; color: gray;">Click to view details</p>
#                     </div>

#                     <div id="staffDetails" class="responsive-box hidden-section" style="border-radius: 15px; background-color: white; color: #084c61;
#                             text-align: center; filter: drop-shadow(3px 3px 5px rgba(0,0,0,0.15)); padding: 15px; box-sizing: border-box; display: none;">
#                         {staff_summaries}
#                     </div>

#                 </div>

#                 <script>
#                     function toggleVisibility(sectionId) {{
#                         var element = document.getElementById(sectionId);
#                         element.style.display = (element.style.display === "none" || element.style.display === "") ? "block" : "none";
#                     }}
#                 </script>
# """, height=600)







    except Exception as e:
        import traceback
        st.error(f"Error accessing or visualizing data: {e}")
        st.write(traceback.format_exc())
 