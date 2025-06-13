import streamlit as st 
st.set_page_config(page_title="INSIGHT", layout="wide", page_icon="./oask_short_logo.png")
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
    

        colors=["#cee4e4","#edd268","#b7cbd0","#f6e9b6","#87bdc0","#8499a2", "#4f6d7a", "#db504a", "#89a436", "#e3b505", "#ba29a7", "#f76649", "#fec841"]

        if not filtered_df.empty:
            # multi column chart with multiple types of charting
            st.markdown("Score Chart")
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

                st.markdown("### Your Scores")
                st.write(data_series)

                
                    

            else:
                st.warning("Please select at least one column to display the chart.")
            sum = 0
            
            for col in filtered_df:
                if "Overall Score" in col:
                    for i in filtered_df[col]:
                        sum = sum + i 
            av = sum/len(filtered_df.index)

            st.html(f"""
                <div style="border-radius: 20px; background-color: white; color: #084c61; width: 30vw; text-align: center; display: flex; flex-direction: column; justify-content: center; filter: drop-shadow(6px, 6px, 6px, black)">
                    <h3>Organization Average Overall Score</h3>
                    <h1 style="font-size: 50px">{av}</h1>
                    <div style="background-color: #8398a1"></div> <!--add something like averages for each indicator or list overall score per form fill out-->
                </div>
            """)
            text_var =""
            for column in filtered_df:
                if "Overall Score" in column:
                    continue
                sum = 0
                for i in filtered_df[column]:
                    sum = sum + i 
                av = sum/len(filtered_df.index)
                if "Standard" in column:
                    name = "Organization Average " + column + ": " + str(av)
                    text_var += "\n" + name + "\n"
                elif "Indicator" in column:
                    name = "Organization Average " + column + ": " + str(av)
                    text_var += "\n" + "\t" + name + "\n"
                    
            st.html(f"""
                        <div style="border-radius: 20px; background-color: white; color: #084c61; width: 30vw; text-align: left; display: flex; flex-direction: column; justify-content: center; filter: drop-shadow()">
                            <h3>{text_var}</h3>
                            <div style="background-color: #8398a1"></div>
                        </div>
                    """) 
    except Exception as e:
        st.error(f"Error accessing or visualizing data: {e}")
