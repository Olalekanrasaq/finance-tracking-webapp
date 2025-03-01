import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from numerize.numerize import numerize

if "user" not in st.session_state:
    st.session_state["user"] = None

st.set_page_config(
    page_title="Finance Tracker",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    menu_items={
        'Get Help': 'mailto:olalekanrasaq1331@gmail.com',
        'Report a bug': "mailto:olalekanrasaq1331@gmail.com",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

from finance_func import *
conn = st.connection("gsheets", type=GSheetsConnection)

sel = st.sidebar.selectbox("Manage your Finance", 
                       ["Log In", "Sign up", "Dashboard", "Add Income", "Add Expenses", "Manage Budget"])

if sel == "Sign up":
    st.title("Finance Tracking App")
    st.markdown("---")
    st.subheader("Sign up as a new user")
    username = st.text_input("Enter a unique username")
    password = st.text_input("Provide a valid password")
    occupation = st.text_input("Occupation")
    gender = st.selectbox("Gender",["-", "Male", "Female"])

    if st.button("Sign up"):
        if username and password:
            register_user(username, password, gender, occupation)
        else:
            st.error("Username and Password fields must be filled!")

elif sel == "Log In":
    st.title("Finance Tracking App")
    st.markdown("---")
    st.subheader("Log in as an existing user")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        if username and password:
            user = login(username, password)
            st.session_state["user"] = user
        else:
            st.error("Username and Password fields must be filled!")

elif sel == "Add Income":
    st.title("Finance Tracking App")
    st.markdown("---")
    st.subheader("Manage your income")
    amount = st.text_input("Amount Received", value="0")
    amount = int(amount.replace(",", ""))
    date = st.date_input("Date of Income", format= "DD/MM/YYYY")
    category = st.selectbox("Category of Income", 
                            ["-", "Salary", "Gift", "Freelance Jobs", 
                             "Allowance", "Contributions", "Others"])
    description = st.text_area("Description of the Income")

    if st.button("Add Income"):
        if st.session_state:
            if (amount > 0) and (category != "-"):
                add_income(amount, date, category, description, st.session_state["user"])
            else:
                st.error("Amount received and category must be provided")
        else:
            st.error("You must be logged in to use app!")

elif sel == "Add Expenses":
    st.title("Finance Tracking App")
    st.markdown("---")
    st.subheader("Manage your spending")
    amount = st.text_input("Amount Spent", value="0")
    amount = int(amount.replace(",", ""))
    date = st.date_input("Date", format= "DD/MM/YYYY")
    category = st.selectbox("Category of Expenses", 
                            ["-", "Foodstuff items", "Gift", "Family", "Feeding",
                             "Personal Care", "Home care", "Contributions", "Others"])
    description = st.text_area("Description of the Expense")

    if st.button("Add Expense"):
        if st.session_state:
            if (amount > 0) and (category != "-"):
                add_expense(amount, date, category, description, st.session_state["user"])
            else:
                st.error("Amount spent and category must be provided")
        else:
            st.error("You must be logged in to use app!")


elif sel == "Dashboard":
    st.markdown("### Dashboard")
    start_date = st.sidebar.date_input("Start Date", value=None)
    end_date = st.sidebar.date_input("End Date", value=None)
    filter_date = st.sidebar.button("Filter by date")

    if st.session_state["user"] is None:
        st.error("You are not logged in!")
    else:
        exp_df = conn.read(worksheet="expenses", ttl=5)
        userExp_df = exp_df[exp_df["Username"] == st.session_state["user"].Username]
        userExp_df["Date"] = pd.to_datetime(userExp_df["Date"]).dt.strftime("%d-%m-%Y")
        userExp_df = userExp_df.sort_index(ascending=False)
        userExpDate_df = userExp_df.set_index(["Date"])
        userExpDate_df = userExpDate_df.drop("Username", axis=1)
        
        inc_df = conn.read(worksheet="income", ttl=5)
        userInc_df = inc_df[inc_df["Username"] == st.session_state["user"].Username]
        userInc_df["Date"] = pd.to_datetime(userInc_df["Date"]).dt.strftime("%d-%m-%Y")
        userInc_df = userInc_df.sort_index(ascending=False)
        userIncDate_df = userInc_df.set_index(["Date"])
        userIncDate_df = userIncDate_df.drop("Username", axis=1)
        

        col1, col2, col3 = st.columns(3, gap="medium")
        with col1:
            with st.container(border=True):
                if not filter_date:
                    income = userInc_df["Amount"].sum()
                else:
                    if start_date is not None and end_date is not None:
                        start_date = start_date.strftime("%d-%m-%Y")
                        end_date = end_date.strftime("%d-%m-%Y")
                        userInc_filtered = userIncDate_df.loc[end_date:start_date]
                        income = userInc_filtered["Amount"].sum()
                st.metric(":moneybag: **Income (NGN)**", value=numerize(income, decimals=2))

        with col2:
            with st.container(border=True):
                if not filter_date:
                    expense = userExp_df["Amount"].sum()
                else:
                    if start_date is not None and end_date is not None:
                        userExp_filtered = userExpDate_df.loc[end_date:start_date]
                        expense = userExp_filtered["Amount"].sum()
                st.metric(":moneybag: **Expenses (NGN)**", value=numerize(expense, decimals=2))
        with col3:
            with st.container(border=True):
                balance = income - expense
                st.metric(":moneybag: **Balance (NGN)**", value=numerize(balance, decimals=2))

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            with st.container():
                st.caption("**Income by Category**")
                if not filter_date:
                    by_IncCat = userInc_df.groupby(userInc_df.Category)["Amount"].sum()
                    st.bar_chart(by_IncCat, x_label="Category", color="#8bfb9a", horizontal=True)
                else:
                    if start_date is not None and end_date is not None:
                        userInc_filtered = userIncDate_df.loc[end_date:start_date]
                        by_IncCat = userInc_filtered.groupby(userInc_filtered.Category)["Amount"].sum()
                        st.bar_chart(by_IncCat, x_label="Category", color="#8bfb9a", horizontal=True)
        with chart_col2:
            with st.container():
                st.caption("**Expenses by Category**")
                if not filter_date:
                    by_ExpCat = userExp_df.groupby(userExp_df.Category)["Amount"].sum()
                    st.bar_chart(by_ExpCat, x_label="Category", color="#fb1779", horizontal=True)
                else:
                    if start_date is not None and end_date is not None:
                        userExp_filtered = userExpDate_df.loc[end_date:start_date]
                        by_ExpCat = userExp_filtered.groupby(userExp_filtered.Category)["Amount"].sum()
                        st.bar_chart(by_ExpCat, x_label="Category", color="#fb1779", horizontal=True)

        chart2_col1, chart2_col2 = st.columns(2)
        with chart2_col1:
            with st.container():
                if not filter_date:
                    temp_Inc = userInc_df.copy().head(7)
                    temp_Inc["Date"] = pd.to_datetime(temp_Inc["Date"])
                    by_Incdate = temp_Inc.groupby(temp_Inc.Date)["Amount"].sum()
                else:
                    if start_date is not None and end_date is not None:
                        userInc_filtered = userIncDate_df.loc[end_date:start_date]
                        by_Incdate = userInc_filtered.groupby(userInc_filtered.index)["Amount"].sum()
                st.caption("**Trend of Income**")
                st.line_chart(by_Incdate)
        with chart2_col2:
            with st.container():
                if not filter_date:
                    temp_Exp = userExp_df.copy().head(7)
                    temp_Exp["Date"] = pd.to_datetime(temp_Exp["Date"])
                    by_Expdate = temp_Exp.groupby(temp_Exp.Date)["Amount"].sum()
                else:
                    if start_date is not None and end_date is not None:
                        userExp_filtered = userExpDate_df.loc[end_date:start_date]
                        by_Expdate = userExp_filtered.groupby(userExp_filtered.index)["Amount"].sum()
                st.caption("**Trend of Expenses**")
                st.line_chart(by_Expdate, color="#b23d82")
        
        df_col1, df_col2 = st.columns(2)
        with df_col1:
            with st.expander("View Income Data"):
                st.dataframe(userIncDate_df)
        with df_col2:
            with st.expander("View Expenses Data"):
                st.dataframe(userExpDate_df)