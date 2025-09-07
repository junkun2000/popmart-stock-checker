import requests
from bs4 import BeautifulSoup
import os
import time

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
TO_USER_ID = os.environ.get("TO_USER_ID")
URL = "https://www.popmart.com/jp/products/3889/THE-MONSTERS-%E3%82%B3%E3%82%AB%E3%83%BB%E3%82%B3%E3%83%BC%E3%83%A9-%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA-%E3%81%AC%E3%81%84%E3%81%90%E3%82%8B%E3%81%BF"

def send_line_message(text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "to": TO_USER_ID,
        "messages": [{"type": "text", "text": text}]
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"[通知送信] {response.status_code}: {response.text}")

def check_stock():
    try:
        res = requests.get(URL)
        soup = BeautifulSoup(res.text, "html.parser")
        if "カートに追加する" in soup.text or "今すぐ購入" in soup.text:
            send_line_message(f"✅【在庫あり】コーララブブぬいぐるみが入荷しました！\n{URL}")
        else:
            print("[監視] 在庫なし")
    except Exception as e:
        print(f"[エラー] {e}")

# 毎分チェック
while True:
    check_stock()
    time.sleep(60)
