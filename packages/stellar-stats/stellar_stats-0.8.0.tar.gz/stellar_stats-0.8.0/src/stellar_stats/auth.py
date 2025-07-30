import extra_streamlit_components as stx
import streamlit as st


def setup_authentication(cfg):
    """Setup authentication for the app using session state and cookies."""
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # Check cookie
    cookie_manager = stx.CookieManager()
    auth_cookie = cookie_manager.get("auth_cookie")
    if auth_cookie == "authenticated":
        st.session_state.authenticated = True

    # Need authentication and not authenticated yet
    if cfg and cfg["general"]["auth"] and not st.session_state.authenticated:
        st.markdown("### Login")
        passcode = st.text_input("Enter Passcode", type="password")

        if passcode:
            if passcode == cfg["general"]["passcode"]:
                st.session_state.authenticated = True
                cookie_manager.set(
                    "auth_cookie", "authenticated", max_age=30 * 24 * 60 * 60
                )
                st.rerun()
            else:
                st.error("Invalid passcode")
                st.session_state.authenticated = False

        # Stop execution if not authenticated
        if not st.session_state.authenticated:
            st.stop()
