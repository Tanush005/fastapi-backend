import requests
import numpy as np
import time
from fastapi import FastAPI

app = FastAPI()

ETHERSCAN_API_KEY = "YGNICQGMX9DGDDTYC7T3CZRC8UH6HMUVTW"


@app.get("/")
def home():
    return {"message": "Fraud detection API is running!"}

def get_wallet_transactions(wallet):
    """Fetches all transactions of the wallet from Etherscan"""
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet}&startblock=0&endblock=99999999&sort=asc&apikey={YGNICQGMX9DGDDTYC7T3CZRC8UH6HMUVTW}"
    response = requests.get(url).json()

    if response.get("status") == "0":  # If API request fails
        return []  

    return response.get("result", [])

def get_wallet_age(wallet):
    """Calculates wallet age from first transaction"""
    transactions = get_wallet_transactions(wallet)
    if not transactions:  # If no transactions exist
        return 0

    first_tx_time = int(transactions[0]["timeStamp"])
    wallet_age_days = (time.time() - first_tx_time) / (60 * 60 * 24)
    return wallet_age_days

def check_blacklisted(wallet):
    """Checks if wallet is blacklisted using Chainalysis API"""
    url = f"https://api.chainalysis.com/api/v1/address/{wallet}"
    headers = {"Authorization": f"Bearer {CHAINALYSIS_API_KEY}"}

    try:
        response = requests.get(url, headers=headers).json()
        return response.get("risk", "unknown")  
    except Exception as e:
        print(f"Chainalysis API error: {e}")  
        return "unknown"  

def calculate_risk_score(wallet):
    """Calculates a risk score based on various fraud indicators"""
    age = get_wallet_age(wallet)
    transactions = get_wallet_transactions(wallet)
    blacklist_status = check_blacklisted(wallet)

    score = 0
    if age < 30:  
        score += 30
    if 0 < len(transactions) < 5:  
        score += 20
    if blacklist_status == "high-risk":
        score += 50

    return min(100, score)

@app.get("/risk/{wallet}")
def risk_analysis(wallet: str):
    """API endpoint to get fraud risk score"""
    score = calculate_risk_score(wallet)
    return {"wallet": wallet, "risk_score": score}
