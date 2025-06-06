import streamlit as st


def authenticated_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("app.py", label="Switch accounts")
    st.sidebar.page_link("pages/homePage.py", label="Home")

def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("app.py", label="Log In")

def menu():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu
    if "org" not in st.session_state:
        unauthenticated_menu()
        return
    authenticated_menu()

def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to
    # render the navigation menu
    if "org" not in st.session_state:
        st.switch_page("app.py")
    menu()