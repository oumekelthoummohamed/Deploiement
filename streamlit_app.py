import os
import requests
import streamlit as st

st.set_page_config(page_title="Bank Churn API", page_icon="??", layout="centered")

st.title("Bank Churn Prediction")

api_url = st.text_input("API URL", value=os.getenv("API_URL", "http://localhost:8000"))

with st.form("predict-form"):
    credit_score = st.number_input("CreditScore", min_value=300, max_value=850, value=650)
    age = st.number_input("Age", min_value=18, max_value=100, value=35)
    tenure = st.number_input("Tenure", min_value=0, max_value=10, value=5)
    balance = st.number_input("Balance", min_value=0.0, value=50000.0)
    num_products = st.number_input("NumOfProducts", min_value=1, max_value=4, value=2)
    has_cr_card = st.selectbox("HasCrCard", options=[0, 1], index=1)
    is_active = st.selectbox("IsActiveMember", options=[0, 1], index=1)
    estimated_salary = st.number_input("EstimatedSalary", min_value=0.0, value=75000.0)
    geo_germany = st.selectbox("Geography_Germany", options=[0, 1], index=0)
    geo_spain = st.selectbox("Geography_Spain", options=[0, 1], index=1)

    submitted = st.form_submit_button("Predict")

if st.button("Health Check"):
    try:
        resp = requests.get(f"{api_url}/health", timeout=10)
        st.write(resp.status_code, resp.json())
    except Exception as exc:
        st.error(f"Health check failed: {exc}")

if submitted:
    payload = {
        "CreditScore": int(credit_score),
        "Age": int(age),
        "Tenure": int(tenure),
        "Balance": float(balance),
        "NumOfProducts": int(num_products),
        "HasCrCard": int(has_cr_card),
        "IsActiveMember": int(is_active),
        "EstimatedSalary": float(estimated_salary),
        "Geography_Germany": int(geo_germany),
        "Geography_Spain": int(geo_spain),
    }

    try:
        resp = requests.post(f"{api_url}/predict", json=payload, timeout=10)
        st.write(resp.status_code, resp.json())
    except Exception as exc:
        st.error(f"Prediction failed: {exc}")
