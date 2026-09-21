import streamlit as st
import api_client

st.set_page_config(page_title="Expense Tracker", layout="wide")

if "token" not in st.session_state:
    st.session_state["token"] = None

if "user" not in st.session_state:
    st.session_state["user"] = None


if st.session_state["token"] is None:
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In")

            if submitted:
                data, status = api_client.auth_login(username, password)
                
                if status == 200:
                    st.session_state["token"] = data["access_token"]
                    user_data, _ = api_client.get_current_user(data["access_token"])
                    st.session_state["user"] = user_data.get("data")
                    st.rerun()
                else:
                    st.error(data.get("message", "Login failed"))

    with tab_register:
        with st.form("register_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Register")

            if submitted:
                data, status = api_client.auth_register(username, email, password)
                if status == 201:
                    st.success("Account created successfully! You can now log in.")
                else:
                    st.error(data.get("message", "Registration failed"))
else:
    with st.sidebar:
        username = st.session_state["user"].get("username", "User") if st.session_state["user"] else "User"

        st.subheader(f"Welcome, {username}!")
        if st.button("Log Out"):
            st.session_state["token"] = None
            st.session_state["user"] = None
            st.rerun()

    st.title("Expense Tracker")
    st.write("Logged in successfully!")