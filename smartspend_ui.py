import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from alerts import check_budget_exceedance

st.set_page_config(
    page_title="SmartKharch",
    page_icon="💸",  
    layout="centered"
)

# File Paths 
DATA_FILE = "smartspend_data.csv"
BUDGET_FILE = "monthly_budgets.csv"

#Categories 
categories = ['Food', 'Shopping', 'Travel', 'Groceries', 'Bills', 'Others']

#Loading Data
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
else:
    df = pd.DataFrame(columns=["Date", "Amount", "Category", "Note", "Month"])

#App Title
st.title("💸 SmartKharch - Expense Tracker")
st.subheader('Where did my money go?')


#Loading  Budgets 
if os.path.exists(BUDGET_FILE):
    budget_df = pd.read_csv(BUDGET_FILE)
else:
    budget_df = pd.DataFrame(columns=["Month"] + categories)

#Sidebar: Select Month 
st.sidebar.header("📅 Filter by Month")
all_months = sorted(df['Month'].unique(), reverse=True)
selected_month = st.sidebar.selectbox("Select Month", all_months) if all_months else None

# Sidebar: Monthly Budgets 
st.sidebar.header("🧾 Set Budgets for Selected Month")

user_budget = {}
if selected_month:
    existing_budget = budget_df[budget_df["Month"] == selected_month]
    for cat in categories:
        default_val = int(existing_budget[cat].values[0]) if not existing_budget.empty and pd.notna(existing_budget[cat].values[0]) else 0
        budget_val = st.sidebar.number_input(f"{cat} Budget (₹)", min_value=0, value=default_val, step=100, key=f"budget_{selected_month}_{cat}")
        user_budget[cat] = budget_val

    # Save Button
    if st.sidebar.button("💾 Save Budget"):
        new_budget_row = {"Month": selected_month, **user_budget}

        # Remove old entry (if exists)
        budget_df = budget_df[budget_df["Month"] != selected_month]

        # Append updated row
        budget_df = pd.concat([budget_df, pd.DataFrame([new_budget_row])], ignore_index=True)
        budget_df.to_csv(BUDGET_FILE, index=False)

        st.sidebar.success("Budget saved for this month!")


#Add Expense 
st.header('➕ Add Expense')
amount = st.number_input("Amount spent", min_value=0.0, format="%.2f")
category = st.selectbox('Category', categories)
expense_date = st.date_input("Date of Expense", min_value=date.today() - timedelta(days=365), max_value=date.today())
note = st.text_input("Note (optional)")

if st.button('Add Expense'):
    new_data = {
        "Date": pd.to_datetime(expense_date),
        "Amount": amount,
        "Category": category,
        "Note": note,
        "Month": pd.to_datetime(expense_date).to_period('M').strftime('%Y-%m')
    }
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success("Expense added!")

#Expense History
st.header("📜 Expense History")
if not df.empty:
    for i in range(len(df)):
        cols = st.columns([2, 2, 2, 3, 2])
        cols[0].write(df.at[i, "Date"].date())
        cols[1].write(f"₹{df.at[i, 'Amount']}")
        cols[2].write(df.at[i, "Category"])
        cols[3].write(df.at[i, "Note"])

        if cols[4].button("Delete", key=f"del_{i}"):
            df = df.drop(index=i).reset_index(drop=True)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()
else:
    st.info("No expenses yet.")

# Filter Data by Selected Month 
filtered_df = df[df['Month'] == selected_month] if selected_month else df

#Budget Alerts( functions from alerts file)
st.header("⚠️ Budget Alerts")
if selected_month:
    alerts = check_budget_exceedance(filtered_df, user_budget)
    if alerts:
        for alert in alerts:
            st.warning(alert)
    else:
        st.success("You're within budget for all categories! 🎉")

#Spending Insights (graphs)
st.header("📉 Spending Insights")
if not filtered_df.empty:
    # 1. Daily Spending Barplot
    st.subheader("📆 Daily Spending Trend")
    daily_spend = filtered_df.groupby('Date')['Amount'].sum().reset_index()
    plt.figure(figsize=(10, 4))
    sns.barplot(x='Date', y='Amount', data=daily_spend, palette='viridis')
    plt.xticks(rotation=45)
    plt.ylabel('Amount (₹)')
    plt.xlabel('Date')
    plt.title('Daily Spending Trend')
    st.pyplot(plt.gcf())

    # 2. Category-wise Pie Chart
    st.subheader("🥧 Category-wise Spending")
    category_spend = filtered_df.groupby('Category')['Amount'].sum()
    plt.figure(figsize=(6, 6))
    plt.pie(category_spend, labels=category_spend.index, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Spending Distribution by Category')
    st.pyplot(plt.gcf())

    # 3. Top Categories Barplot
    st.subheader("🏆 Top Spending Categories")
    top_cat = category_spend.sort_values(ascending=False)
    plt.figure(figsize=(8, 4))
    sns.barplot(x=top_cat.values, y=top_cat.index, palette='mako')
    plt.xlabel("Total Spent (₹)")
    plt.title("Top Categories")
    st.pyplot(plt.gcf())
else:
    st.info("No data for the selected month.")

#Monthly amount
st.subheader("📊 Monthly Expense Trend")
if not filtered_df.empty:
   monthly_trend = df.groupby('Month')['Amount'].sum().reset_index()
   fig, ax = plt.subplots()
   sns.barplot(data=monthly_trend, x='Month', y='Amount', ax=ax,palette='Paired')
   plt.xticks(rotation=45)
   st.pyplot(fig)

else:
    st.info("Add expenses to view insights.")
