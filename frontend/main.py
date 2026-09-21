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

    tab_dashboard, tab_expenses, tab_categories = st.tabs(["Dashboard", "Expenses", "Categories"])

    with tab_categories:
        st.header("Manage Categories")

        col_add, col_list = st.columns([1, 1])

        with col_add:
            st.subheader("Add New category")
            with st.form("add_category_form", clear_on_submit=True):
                category_name = st.text_input("Category Name", placeholder="e.g. Groceries, Gym, Travel")
                add_submitted = st.form_submit_button("Create Category")

                if add_submitted:
                    if not category_name.strip():
                        st.warning("Category name cannot be empty.")
                    else:
                        data, status = api_client.create_category(st.session_state["token"], category_name)
                        if status == 201:
                            st.success(f"Category '{category_name}' created successfully!")
                            st.rerun()
                        else:
                            st.error(data.get("message", "Failed to create category."))

        with col_list:
            st.subheader("Your Categories")
            data, status = api_client.get_categories(st.session_state["token"])

            if status == 200:
                categories = data.get("data", [])
                if not categories:
                    st.info("No categories created yet. Create your first one on the left!")
                else:
                    for cat in categories:
                        col_name, col_btn = st.columns([3, 1])

                        with col_name:
                            st.write(f"**{cat['name']}**")
                        with col_btn:
                            if st.button("Delete", key=f"del_cat_{cat['id']}"):
                                del_data, del_status = api_client.delete_category(st.session_state["token"], cat["id"])

                                if del_status == 200:
                                    st.success(f"Category '{cat['name']}' deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error(del_data.get("message", "Failed to delete category."))
            else:
                st.error(data.get("message", "Failed to load categories."))