import os
import time
import requests
from bs4 import BeautifulSoup

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
URLS_FILE = "urls.txt"
CHECK_INTERVAL = 60  # 秒

def send_discord_message(message: str):
    if WEBHOOK_URL:
        try:
            requests.post(WEBHOOK_URL, json={"content": message}, timeout=10)
        except Exception as e:
            print(f"通知エラー: {e}", flush=True)

def check_stock(url: str):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "商品名不明"

        button = soup.find("button", {"class": "add-to-cart-btn"})
        if button:
            text = button.get_text(strip=True)
            in_stock = text not in ["再入荷を通知", "Sold Out", "SOLD OUT"]
        else:
            in_stock = False

        return title, in_stock
    except Exception as e:
        print(f"エラー: {url} → {e}", flush=True)
