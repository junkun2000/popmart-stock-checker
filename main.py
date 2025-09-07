from flask import Flask, request, abort
import json
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

USER_ID_FILE = "user_ids.json"
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
URL = "https://www.popmart.com/jp/products/3889/THE-MONSTERS-%E3%82%B3%E3%82%AB%E3%83%BB%E3%82%B3%E3%83%BC%E3%83%A9-%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA-%E3%81%AC%E3%81%84%E3%81%90%E3%82%8B%E3%81%BF"

def save_user_id(user_id):
    user_ids = []
    if os.path.exists(USER_ID_FILE):
        with open(USER_ID_FILE, "r") as f:
            user_ids = json.load(f)
    if user_id not in user_ids:
        user_ids.append(user_id)
        with open(USER_ID_FILE, "w") as f:
            json.dump(user_ids, f)
        print(f"[INFO] New user registered: {user_id}")

def send_line_message(user_id, text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "to": user_id,
        "messages": [{"type": "text", "text": text}]
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"[Notification sent] {response.status_code}: {response.text}")

def check_stock():
    try:
        # 在庫チェックをせず、常にTrueにして通知を送る
        in_stock = True  # ← ここを追加しました

        if in_stock:   # ← ここで常に通知を送るように条件を変更
            if os.path.exists(USER_ID_FILE):
                with open(USER_ID_FILE, "r") as f:
                    user_ids = json.load(f)
                for user_id in user_ids:
                    send_line_message(user_id, f"✅【テスト通知】入荷通知が正常に届いています！\n{URL}")
            else:
                print("[Warning] user_ids.json not found.")
        else:
            print("[Check] No stock.")
    except Exception as e:
        print(f"[Error] {e}")

@app.route("/callback", methods=["POST"])
def callback():
    body = request.get_json()
    try:
        for event in body["events"]:
            if event["type"] == "message" and event["message"]["type"] == "text":
                user_id = event["source"]["userId"]
                save_user_id(user_id)
        return "OK"
    except Exception as e:
        print(f"[Error] {e}")
        abort(400)

if __name__ == "__main__":
    import threading
    import time

    # 在庫チェックをバックグラウンドで定期実行する関数
    def periodic_check():
        while True:
            check_stock()
            time.sleep(60)  # 1分毎にチェック

    # バックグラウンドスレッドで監視開始
    threading.Thread(target=periodic_check, daemon=True).start()

    # Flaskアプリ起動（Renderの$PORTを利用）
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
