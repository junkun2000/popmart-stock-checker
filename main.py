from flask import Flask, request, abort
import json
import os
import requests

app = Flask(__name__)

USER_ID_FILE = "user_ids.json"
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

def save_user_id(user_id):
    """
    ユーザーIDをuser_ids.jsonに保存する関数
    """
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
    """
    LINEへメッセージを送信する関数（登録完了通知用）
    """
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

@app.route("/callback", methods=["POST"])
def callback():
    """
    LINEプラットフォームからのメッセージ受信・ユーザーID登録
    """
    body = request.get_json()
    try:
        for event in body["events"]:
            if event["type"] == "message" and event["message"]["type"] == "text":
                user_id = event["source"]["userId"]
                save_user_id(user_id)
                send_line_message(user_id, "✅登録が完了しました！入荷通知をお待ちください。")
        return "OK"
    except Exception as e:
        print(f"[Error] {e}")
        abort(400)

if __name__ == "__main__":
    # Flaskアプリ起動（Renderの$PORTを利用）
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
