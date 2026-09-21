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


    with tab_expenses:
        st.header("Expenses")

        cat_data, cat_status = api_client.get_categories(st.session_state["token"])
        categories = cat_data.get("data", []) if cat_status == 200 else []

        if not categories:
            st.warning("No categories available. Please create a category first.")
        else:
            category_map = {cat["name"]: cat["id"] for cat in categories}

            with st.expander("Add New Expense"):
                with st.form("add_expense_form", clear_on_submit=True):
                    col_t, col_a = st.columns([2, 1])

                    with col_t:
                        title = st.text_input("Expense Title", placeholder="e.g. Groceries")

                    with col_a:
                        amount = st.number_input("Amount", min_value=0.01, step=1.00, format="%.2f")

                    col_c, col_d = st.columns([1, 1])

                    with col_c:
                        selected_cat_name = st.selectbox("Category", options=list(category_map.keys()))

                    with col_d:
                        expense_date = st.date_input("Date")

                    description = st.text_area("Description (Optional)", placeholder="Add extra notes here...")

                    expense_submitted = st.form_submit_button("Save Expense")

                    if expense_submitted:
                        if not title.strip():
                            st.warning("Expense title cannot be empty.")
                        else:
                            payload = {
                                "title": title,
                                "amount": amount,
                                "category_id": category_map[selected_cat_name],
                                "date": str(expense_date),
                                "description": description.strip() if description.strip() else None
                            }

                            data, status = api_client.create_expense(st.session_state["token"], payload)
                            if status == 201:
                                st.success(f"Expense added successfully!")
                                st.rerun()
                            else:
                                st.error(data.get("message", "Failed to add expense."))
        st.divider()


        st.subheader("Your Expenses")
        col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
        with col_f1:
            filter_cat_options = ["All"] + list(category_map.keys()) if categories else ["All"]
            filter_cat = st.selectbox("Filter by Category", options=filter_cat_options)
        with col_f2:
            min_amt = st.number_input("Min Amount", min_value=0.0, step=10.0, value=0.0)
        with col_f3:
            sort_order = st.selectbox("Order by Date", ["Newest First (desc)", "Oldest First (asc)"])

        params = {
            "order": "desc" if "desc" in sort_order else "asc"
        }
        if filter_cat != "All":
            params["category_id"] = category_map[filter_cat]
        if min_amt > 0:
            params["min_amount"] = min_amt

        exp_data, exp_status = api_client.get_expenses(st.session_state["token"], params=params)

        if exp_status == 200:
            expenses = exp_data.get("data", [])
            if not expenses:
                st.info("No expenses found matching the criteria.")
            else:
                table_rows = []
                for e in expenses:
                    cat_name = next((c["name"] for c in categories if c["id"] == e.get("category_id")), "Unknown")
                    table_rows.append({
                        "Title": e.get("title"),
                        "Amount": f"${e.get('amount'):,.2f}",
                        "Category": cat_name,
                        "Date": e.get("date"),
                        "Description": e.get("description") or "-"
                    })

                st.table(table_rows)

                with st.expander("Delete an Expense"):
                    expense_options = {f"{e['title']} (${e['amount']}) - {e['date']}": e["id"] for e in expenses}
                    selected_to_delete = st.selectbox("Select Expense to Delete", options=list(expense_options.keys()))
                    if st.button("Confirm Delete Expense"):
                        del_id = expense_options[selected_to_delete]
                        d_data, d_status = api_client.delete_expense(st.session_state["token"], del_id)
                        if d_status == 200:
                            st.success("Expense deleted successfully!")
                            st.rerun()
                        else:
                            st.error(d_data.get("message", "Failed to delete expense."))
        else:
            st.error("Failed to load expenses.")


    with tab_dashboard:
        st.header("Financial Dashboard & Analytics")

        summary_res, summary_status = api_client.get_summary(st.session_state["token"], include_ai=False)

        if summary_status == 200:
            summary = summary_res.get("data", {})
            total_spent = summary.get("total_spending", 0.0)
            month_spent = summary.get("current_month_spending", 0.0)
            by_category = summary.get("by_category", [])

            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Total Spending", f"${total_spent:,.2f}")
            with col_m2:
                st.metric("This Month's Spending", f"${month_spent:,.2f}")
            with col_m3:
                st.metric("Active Categories", len(by_category))

            st.divider()

            st.subheader("Spending by Category")

            if not by_category:
                st.info("No expenses logged yet. Add some expenses to see visual analytics!")
            else:
                chart_data = {item["category_name"]: item["total_amount"] for item in by_category}
                st.bar_chart(chart_data)

            st.divider()

            st.subheader("AI Financial Advisor")
            st.caption("Powered by local Ollama LLM (llama3.2)")

            if not by_category:
                st.info("Log some expenses first so the AI has data to analyze.")
            else:
                if st.button("Generate AI Financial Insights"):
                    with st.spinner("Analyzing your spending habits with Ollama..."):
                        ai_res, ai_status = api_client.get_summary(st.session_state["token"], include_ai=True)

                        if ai_status == 200:
                            ai_data = ai_res.get("data", {}).get("ai_insight")
                            if ai_data:
                                st.success("Analysis Complete!")
                                st.write(f"**Executive Summary:** {ai_data.get('summary')}")

                                st.write("**Actionable Saving Tips:**")
                                for tip in ai_data.get("tips", []):
                                    st.write(f"- {tip}")
                            else:
                                st.warning("AI did not return any insights.")
                        else:
                            st.error("Failed to generate AI insights. Make sure your local Ollama instance is running!")
        else:
            st.error("Failed to load dashboard summary data.")