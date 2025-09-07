import os
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup

# Google Sheets APIの認証情報
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = os.environ.get("GOOGLE_CREDENTIALS")
creds_dict = json.loads(creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
worksheet = client.open("LINE Bot User IDs").sheet1

# LINE Bot API
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

# 在庫チェック対象のURL
URL = "https://www.popmart.com/jp/products/3889/THE-MONSTERS-%E3%82%B3%E3%82%AB%E3%83%BB%E3%82%B3%E3%83%BC%E3%83%A9-%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA-%E3%81%AC%E3%81%84%E3%81%90%E3%82%8B%E3%81%BF"

def send_line_message(user_id, text):
    """LINEへメッセージを送信する関数"""
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
    """在庫チェックと通知を行う関数"""
    print("在庫チェックを開始します...")
    try:
        response = requests.get(URL)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        notify_text_button = soup.find(string="再入荷を通知")
        in_stock = notify_text_button is None

        if in_stock:
            print("✅ 在庫が見つかりました！")
            user_ids = worksheet.col_values(1)
            print(f"ユーザーIDを読み込みました: {user_ids}")
            
            for user_id in user_ids:
                send_line_message(user_id, f"✅【入荷通知】商品が入荷しました！\n{URL}")
        else:
            print("現在、在庫はありません。")

    except requests.exceptions.RequestException as e:
        print(f"[Request Error] {e}")
    except Exception as e:
        print(f"[Error] {e}")

if __name__ == "__main__":
    check_stock()
