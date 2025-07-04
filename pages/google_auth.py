import os
import streamlit as st
from urllib.parse import urlencode
from requests_oauthlib import OAuth2Session
from requests import get
from streamlit_cookies_manager import EncryptedCookieManager
import json


# # --- OAuth2 Configuration ---
# CLIENT_ID = st.secrets["googleClientID"]
# CLIENT_SECRET = st.secrets["googleClientSecret"]
# REDIRECT_URI = "https://getinsights.streamlit.app/auth/callback" 
# SCOPE = [
#     "https://www.googleapis.com/auth/userinfo.email",
#     "https://www.googleapis.com/auth/userinfo.profile",
#     "openid"
# ]
# AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
# TOKEN_URL = "https://oauth2.googleapis.com/token"
# USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"



client_id = st.secrets["auth"]["auth0"]["client_id"]
client_secret = st.secrets["auth"]["auth0"]["client_secret"]
auth0_domain = st.secrets["auth"]["auth0"]["domain"]
server_metadata_url = st.secrets["auth"]["auth0"]["server_metadata_url"]
redirect_uri = st.secrets["redirect_uri"]
# Derived Auth0 endpoints
token_url = f"https://{auth0_domain}/oauth/token"
userinfo_url = f"https://{auth0_domain}/userinfo"

scope = ["openid", "profile", "email"]


def login():
    cookies = st.session_state.get("cookies")
    if cookies is None:
        st.error("Cookies not initialized.")
        st.stop()

    # Proceed to use `cookies` safely

    auth0 = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)

    authorization_url, state = auth0.authorization_url(
        f"https://{auth0_domain}/authorize",
        audience=f"https://{auth0_domain}/userinfo",
        prompt="login"
    )



    cookies["oauth_state"] = state
    cookies.save()


    # Render login button with HTML + CSS
    st.html(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;900&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Poppins', sans-serif;
        }}

        .container {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 80vh;
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

        .auth0-button img {{
            cursor: pointer;
            width: 250px;
            max-width: 80vw;
        }}

        @media (max-width: 768px) {{
            .card {{
                flex-direction: column;
            }}

            .left-panel, .right-panel {{
                width: 100%;
            }}

            .auth0-button img {{
                width: 220px;
            }}
        }}
        </style>

        <div class="container">
            <div class="card">
                <div class="left-panel">
                    <h1>Welcome to INSIGHT!</h1>
                    <p>Sign in with your Auth0 account to access your dashboard.</p>
                </div>
                <div class="right-panel">
                    <a href="{authorization_url}" target="_blank">
                         <img src="https://i.imgur.com/HpRK4Jv.png"
                           alt="Sign in with Auth0"/>
                    </a>
                </div>
            </div>
        </div>
    """)


def fetch_token(code):
    cookies = st.session_state.get("cookies")
    if cookies is None:
        st.error("Cookies not initialized.")
        st.stop()
    try:

        oauth_state = cookies.get("oauth_state")
        if not oauth_state:
            st.warning("OAuth state is missing. Please try logging in again.")
            return None

        auth0 = OAuth2Session(client_id, redirect_uri=redirect_uri, state=oauth_state)
        token = auth0.fetch_token(
            token_url,
            client_secret=client_secret,
            code=code
        )
        return token
    except Exception as e:
        st.error("Failed to fetch token from Auth0.")
        st.exception(e)
        return None



def get_user_info(token):
    try:
        auth0 = OAuth2Session(client_id, token=token)
        response = auth0.get(userinfo_url)
        return response.json()
    except Exception as e:
        st.error("Failed to fetch user info.")
        st.exception(e)
        return {}



# def login():


#     try:
#         oauth = OAuth2Session(
#             CLIENT_ID,
#             scope=SCOPE,
#             redirect_uri=REDIRECT_URI
#         )
#         auth_url, state = oauth.authorization_url(
#             AUTHORIZATION_BASE_URL, 
#             access_type="offline", 
#             prompt="consent" 
#         )

#         st.session_state.oauth_state = state
        
#         st.html(f"""
#         <style>
#         @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;900&display=swap');

#         html, body, [class*="css"] {{
#             font-family: 'Poppins', sans-serif;
#             margin: 0;
#             padding: 0;
#         }}

#         .container {{
#             display: flex;
#             justify-content: center;
#             align-items: center;
#             box-sizing: border-box;
#             padding: 2vh 2vw;
#         }}

#         .card {{
#             display: flex;
#             flex-direction: row;
#             width: 100%;
#             max-width: 900px;
#             background: white;
#             border-radius: 20px;
#             overflow: hidden;
#             box-shadow: 0 4px 15px rgba(0,0,0,0.2);
#         }}

#         .left-panel {{
#             width: 50%;
#             background: linear-gradient(120deg, #084c61, #4f6d7a, #56a3a6);
#             color: white;
#             padding: 5vh 5vw;
#             display: flex;
#             flex-direction: column;
#             justify-content: center;
#         }}

#         .left-panel h1 {{
#             font-size: 2.5em;
#             font-weight: 900;
#             margin-bottom: 0.3em;
#         }}

#         .left-panel p {{
#             font-size: 1.1em;
#         }}

#         .right-panel {{
#             width: 50%;
#             background: white;
#             padding: 5vh 5vw;
#             display: flex;
#             justify-content: center;
#             align-items: center;
#         }}

#         .google-button img {{
#             cursor: pointer;
#             width: 250px;
#             max-width: 80vw;
#         }}

#         @media (max-width: 768px) {{
#             .card {{
#                 flex-direction: column;
#                 border-radius: 20px;
#             }}

#             .left-panel, .right-panel {{
#                 width: 100%;
#                 padding: 6vh 6vw;
#             }}

#             .left-panel {{
#                 border-top-left-radius: 20px;
#                 border-top-right-radius: 20px;
#             }}

#             .right-panel {{
#                 border-bottom-left-radius: 20px;
#                 border-bottom-right-radius: 20px;
#             }}

#             .left-panel h1 {{
#                 font-size: 2em;
#             }}

#             .google-button img {{
#                 width: 220px;
#             }}
#         }}
#         </style>

#         <div class="container">
#             <div class="card">
#                 <div class="left-panel">
#                     <h1>Welcome to INSIGHT!</h1>
#                     <p>You can sign in using your Google account.</p>
#                 </div>
#                 <div class="right-panel">
#                     <div class="google-button">
#                         <a href="{auth_url}">
#                             <img src="https://developers.google.com/static/identity/images/branding_guideline_sample_lt_rd_lg.svg"
#                                 alt="Sign in with Google"/>
#                         </a>
#                     </div>
#                 </div>
#             </div>
#         </div>
#         """)

#     except Exception as e:
#         st.error("Google OAuth failed:")
#         st.exception(e)

# # --- Exchange Code for Token ---
# def fetch_token(code):
#     try:
#         oauth = OAuth2Session(
#             CLIENT_ID,
#             redirect_uri=REDIRECT_URI
#         )
#         token = oauth.fetch_token(
#             TOKEN_URL,
#             client_secret=CLIENT_SECRET,
#             code=code
#         )
#         st.session_state.token = token  # Store in session state
#         return token
#     except Exception as e:
#         st.error(f"Failed to fetch token: {e}")
#         return None

# # --- Get User Info from Google ---
# def get_user_info(token):
#     try:
#         resp = get(USER_INFO_URL, headers={"Authorization": f"Bearer {token['access_token']}"})
#         return resp.json()
#     except Exception as e:
#         st.error("Failed to fetch user info")
#         st.exception(e)
#         return {}
