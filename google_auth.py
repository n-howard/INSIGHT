import os
import streamlit as st
from urllib.parse import urlencode
from insight_secret_client import googleclientid, googleclientsecret
from requests_oauthlib import OAuth2Session
from requests import get

# Constants
CLIENT_ID = googleclientid
CLIENT_SECRET = googleclientsecret
REDIRECT_URI = "http://localhost:8501"
SCOPE = ["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "openid"]
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
        st.markdown(f"[Click here to sign in with Google]({auth_url})")
    except Exception as e:
        st.error("Google OAuth failed:")
        st.exception(e)


def fetch_token(code):
    try:
        oauth = OAuth2Session(
            CLIENT_ID,
            state=st.session_state.oauth_state,
            redirect_uri=REDIRECT_URI
        )
        token = oauth.fetch_token(
            TOKEN_URL,
            client_secret=CLIENT_SECRET,
            code=code
        )
        # st.success("✅ Token fetched successfully")
        return token
    except Exception as e:
        st.error(f"❌ Failed to fetch token: {e}")
        return None



def get_user_info(token):
    try:
        resp = get(USER_INFO_URL, headers={"Authorization": f"Bearer {token['access_token']}"})
        return resp.json()
    except Exception as e:
        st.error("Failed to fetch user info")
        st.exception(e)
        return {}
