import streamlit as st
import streamlit_authenticator as stauth

def st_login():
    authenticator = stauth.Authenticate(
        dict(st.secrets['credentials']),
        st.secrets['cookie']['name'],
        st.secrets['cookie']['key'],
        st.secrets['cookie']['expiry_days']
    )
    if st.button("Sign Up"):
        try:
            user_email, user_username, user_name = authenticator.register_user(
                fields={'Form name':'Sign Up for INSIGHT', 'Email':'Email', 'Password': 'Password', 'Repeat Password':'Reenter Password', 'Captcha':'Enter CAPTCHA', 'Register':'Sign Up'}, 
                merge_username_email=True, password_hint=False)
            if user_email: 
                st.success('Account created successfully.')
        except Exception as e:
            st.error(e)
    if st.button("Log In"):
        try:
            authenticator.login()
            # if st.button("Forgot Password"):
            #     try:
            #         username_of_forgotten_password, \
            #         email_of_forgotten_password, \
            #         new_random_password = authenticator.forgot_password()
            #         if username_of_forgotten_password:
            #             st.success('A new password will be sent securely.')
            #             # To securely transfer the new password to the user please see step 8.
            #         elif username_of_forgotten_password == False:
            #             st.error('Username not found')
            #     except Exception as e:
            #         st.error(e)
        except Exception as e:
            st.error(e)


    if st.session_state.get('authentication_status') is False:
        st.error('Username/password is incorrect')
    elif st.session_state.get('authentication_status') is None:
        st.warning('Please enter your username and password')