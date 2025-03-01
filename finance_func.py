import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

conn = st.connection("gsheets", type=GSheetsConnection)

def register_user(username, password, gender, occupation="NA"):
    
    users_df = conn.read(worksheet="users", ttl=5)

    if username in list(users_df["Username"]):
        st.error("Username already taken! Try with another username.")
    else: 
        user_dict = {
            "Username": username,
            "Password": password,
            "Occupation": occupation.lower(),
            "Gender": gender
        }

        # Convert the new row into a DataFrame
        new_df = pd.DataFrame([user_dict])
        # append the new user
        users_df = pd.concat([users_df, new_df], ignore_index=True) 
        # Update the spreadsheet or database
        conn.update(worksheet="users", data=users_df)
        st.success("You've been signed up successfully. Proceed to login!!!")

def login(username, password):
    users_df = conn.read(worksheet="users", ttl=5)
    for user in list(users_df.itertuples()):
        if user.Username == username:
            if str(user.Password) == password:
                st.success("Login Successful!!")
                return user
            else:
                st.error("Password Incorrect!")
            
            break
    
    else:
        st.error("Username not found! Kindly sign up.")

def add_income(amount, date, category, description, user):
    
    income_df = conn.read(worksheet="income", ttl=5)
    income_dict = {
            "Date": date,
            "Type": "Income",
            "Amount": amount,
            "Category": category,
            "Description": description,
            "Username": user.Username
        }

    # Convert the new row into a DataFrame
    new_df = pd.DataFrame([income_dict])
    # append the new income
    income_df = pd.concat([income_df, new_df], ignore_index=True) 
    # Update the spreadsheet or database
    conn.update(worksheet="income", data=income_df)
    st.success("Income has been added!")

def add_expense(amount, date, category, description, user):
    
    exp_df = conn.read(worksheet="expenses", ttl=5)
    exp_dict = {
            "Date": date,
            "Type": "Expense",
            "Amount": amount,
            "Category": category,
            "Description": description,
            "Username": user.Username
        }

    # Convert the new row into a DataFrame
    new_df = pd.DataFrame([exp_dict])
    # append the new income
    exp_df = pd.concat([exp_df, new_df], ignore_index=True) 
    # Update the spreadsheet or database
    conn.update(worksheet="expenses", data=exp_df)
    st.success("Expense has been added!")
    
