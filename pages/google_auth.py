import os
import streamlit as st
from urllib.parse import urlencode
from requests_oauthlib import OAuth2Session
from requests import get

# --- OAuth2 Configuration ---
CLIENT_ID = st.secrets.googleClientID
CLIENT_SECRET = st.secrets.googleClientSecret
REDIRECT_URI = "http://localhost:8501"  # Adjust this if you rename or relocate your main app
SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]
AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"


def login():
    try:
        oauth = OAuth2Session(
            CLIENT_ID,
            scope=SCOPE,
            redirect_uri=REDIRECT_URI
        )
        auth_url, state = oauth.authorization_url(
            AUTHORIZATION_BASE_URL, 
            access_type="offline", 
            prompt="consent" 
        )
        st.session_state.oauth_state = state
        # st.markdown(f"[Click here to sign in with Google]({auth_url})")
        # st.html(f"""
        #     <style>
        #         .google-login-button {{
        #             text-align: center;
        #             border-radius: 40px;
        #             color: #084c61;
        #             background-color: white;
        #             border: 1px solid #cedbdf;
        #             padding: 15px;
        #             display: block;
        #             margin: 5vh auto 0 auto;
        #             font-size: 2rem;
        #             cursor: pointer;
        #             transition: border-color 0.3s color 0.3s background-color 0.3s;
        #         }}

        #         .google-login-button:hover {{
        #             border-color: #084c61;
        #         }}
        #         .google-login-button:active{{
        #             color: white;
        #             background-color: #084c61;
        #         }}
        #     </style>

        #     <a href="{auth_url}" style="text-decoration: none">
        #         <button type="button" class="google-login-button">Log In With Google</button>
        #     </a>
        # # """)

        # st.html(f"""
        #     <a href="{auth_url}" style="display: flex; justify-content: center;">
        #         <img src="https://developers.google.com/static/identity/images/branding_guideline_sample_lt_rd_lg.svg"
        #             alt="Sign in with Google"
        #             style="cursor: pointer; width: 30vh" />
        #     </a>
        # """)
        # st.html(f"""
        # <style>
        # @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;900&display=swap');

        # html, body, [class*="css"] {{
        #     font-family: 'Poppins', sans-serif;
        #     margin: 0;
        #     padding: 0;
        # }}

        # .container {{
        #     display: flex;
        #     height: 100vh;
        #     width: 100vw;
        #     overflow: hidden;
        # }}

        # .left-panel {{
        #     width: 50%;
        #     background: linear-gradient(120deg, #084c61, #4f6d7a, #56a3a6);
        #     color: white;
        #     padding: 5vh 5vw;
        #     display: flex;
        #     flex-direction: column;
        #     justify-content: center;
        #     border-top-left-radius: 20px;
        #     border-bottom-left-radius: 20px;
        #     position: relative;
        #     filter: drop-shadow(2px 2px 2px grey);
        # }}

        # .left-panel h1 {{
        #     font-size: 3.5em;
        #     font-weight: 900;
        #     margin-bottom: 0.3em;
        # }}

        # .left-panel p {{
        #     font-size: 1.2em;
        # }}

        # .right-panel {{
        #     width: 50%;
        #     background: white;
        #     padding: 5vh 5vw;
        #     display: flex;
        #     justify-content: center;
        #     align-items: center;
        #     border-top-right-radius: 20px;
        #     border-bottom-right-radius: 20px;
        #     position: relative;
        #     filter: drop-shadow(2px 2px 2px grey);
        # }}

        # .google-button img {{
        #     cursor: pointer;
        #     width: 250px;
        # }}
        # </style>

        # <div class="container">
        #     <div class="left-panel">
        #         <h1>Welcome to INSIGHT!</h1>
        #         <p>You can sign in using your Google account.</p>
        #     </div>
        #     <div class="right-panel">
        #         <div class="google-button">
        #             <a href="{auth_url}">
        #                 <img src="https://developers.google.com/static/identity/images/branding_guideline_sample_lt_rd_lg.svg"
        #                     alt="Sign in with Google"/>
        #             </a>
        #         </div>
        #     </div>
        # </div>
        # """)
        st.html(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;900&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 0;
        }}

        .container {{
            display: flex;
            justify-content: center;
            align-items: center;
            box-sizing: border-box;
            padding: 2vh 2vw;
        }}

        .card {{
            display: flex;
            flex-direction: row;
            width: 100%;
            max-width: 900px;
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}

        .left-panel {{
            width: 50%;
            background: linear-gradient(120deg, #084c61, #4f6d7a, #56a3a6);
            color: white;
            padding: 5vh 5vw;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .left-panel h1 {{
            font-size: 2.5em;
            font-weight: 900;
            margin-bottom: 0.3em;
        }}

        .left-panel p {{
            font-size: 1.1em;
        }}

        .right-panel {{
            width: 50%;
            background: white;
            padding: 5vh 5vw;
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        .google-button img {{
            cursor: pointer;
            width: 250px;
            max-width: 80vw;
        }}

        @media (max-width: 768px) {{
            .card {{
                flex-direction: column;
                border-radius: 20px;
            }}

            .left-panel, .right-panel {{
                width: 100%;
                padding: 6vh 6vw;
            }}

            .left-panel {{
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
            }}

            .right-panel {{
                border-bottom-left-radius: 20px;
                border-bottom-right-radius: 20px;
            }}

            .left-panel h1 {{
                font-size: 2em;
            }}

            .google-button img {{
                width: 220px;
            }}
        }}
        </style>

        <div class="container">
            <div class="card">
                <div class="left-panel">
                    <h1>Welcome to INSIGHT!</h1>
                    <p>You can sign in using your Google account.</p>
                </div>
                <div class="right-panel">
                    <div class="google-button">
                        <a href="{auth_url}">
                            <img src="https://developers.google.com/static/identity/images/branding_guideline_sample_lt_rd_lg.svg"
                                alt="Sign in with Google"/>
                        </a>
                    </div>
                </div>
            </div>
        </div>
        """)

    except Exception as e:
        st.error("Google OAuth failed:")
        st.exception(e)

# --- Exchange Code for Token ---
def fetch_token(code):
    try:
        oauth = OAuth2Session(
            CLIENT_ID,
            redirect_uri=REDIRECT_URI
        )
        token = oauth.fetch_token(
            TOKEN_URL,
            client_secret=CLIENT_SECRET,
            code=code
        )
        st.session_state.token = token  # Store in session state
        return token
    except Exception as e:
        st.error(f"Failed to fetch token: {e}")
        return None

# --- Get User Info from Google ---
def get_user_info(token):
    try:
        resp = get(USER_INFO_URL, headers={"Authorization": f"Bearer {token['access_token']}"})
        return resp.json()
    except Exception as e:
        st.error("Failed to fetch user info")
        st.exception(e)
        return {}
