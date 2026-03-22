# stock_utils.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

def get_stock(symbol):
    if not ALPHAVANTAGE_API_KEY:
        raise ValueError("Missing ALPHAVANTAGE_API_KEY")

    url = (
        f"https://www.alphavantage.co/query?"
        f"function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
    )

    try:
        response = requests.get(url)
        data = response.json().get("Global Quote", {})

        if not data or "05. price" not in data:
            return None

        price = float(data["05. price"])
        change = float(data["09. change"])
        change_percent = float(data["10. change percent"].strip('%'))

        status = (
            "up" if change > 0 else
            "down" if change < 0 else "unchanged"
        )

        return {
            "symbol": symbol.upper(),
            "price": round(price, 2),
            "change": round(change, 2),
            "pct": round(change_percent, 2),
            "status": status
        }

    except Exception as e:
        print("Stock Error:", e)
        return None

def get_stock_nlg(stock):
    """Generate AI-like summary for stock"""
    direction = "up" if stock["change"] > 0 else "down" if stock["change"] < 0 else "unchanged"
    return (
        f"{stock['symbol']} is {direction} by {abs(stock['pct']):.2f}% "
        f"({stock['change']:+.2f}) today."
    )
