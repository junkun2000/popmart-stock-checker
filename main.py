import requests
from bs4 import BeautifulSoup
import os
import time
import json  # ★ 追加

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
# TO_USER_ID = os.environ.get("TO_USER_ID")  # ★ 削除（単一ユーザーIDは使わない）
URL = "https://www.popmart.com/jp/products/3889/THE-MONSTERS-%E3%82%B3%E3%82%AB%E3%83%BB%E3%82%B3%E3%83%BC%E3%83%A9-%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA-%E3%81%AC%E3%81%84%E3%81%90%E3%82%8B%E3%81%BF"
USER_ID_FILE = "user_ids.json"  # ★ 追加

def send_line_message(to_user_id, text):  # ★ 引数に to_user_id を追加
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "to": to_user_id,  # ★ 単一ユーザーID→引数で渡す形に変更
        "messages": [{"type": "text", "text": text}]
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"[通知送信] {response.status_code}: {response.text}")

def check_stock():
    try:
        res = requests.get(URL)
        soup = BeautifulSoup(res.text, "html.parser")
        if "カートに追加する" in soup.text or "今すぐ購入" in soup.text:
            # ★ 複数ユーザーIDを読み込んでループ送信
            if os.path.exists(USER_ID_FILE):
                with open(USER_ID_FILE, "r") as f:
                    user_ids = json.load(f)  # ★
                for uid in user_ids:  # ★
                    send_line_message(uid, f"✅【在庫あり】コーララブブぬいぐるみが入荷しました！\n{URL}")  # ★
            else:
                print("[警告] user_ids.json が見つかりません")
        else:
            print("[監視] 在庫なし")
    except Exception as e:
        print(f"[エラー] {e}")

# 毎分チェック
while True:
    check_stock()
    time.sleep(60)
