import os
import json
import requests
from bs4 import BeautifulSoup

USER_ID_FILE = "user_ids.json"
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
URL = "https://www.popmart.com/jp/products/3889/THE-MONSTERS-%E3%82%B3%E3%82%AB%E3%83%BB%E3%82%B3%E3%83%BC%E3%83%A9-%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA-%E3%81%AC%E3%81%84%E3%81%90%E3%82%8B%E3%81%BF"

def send_line_message(user_id, text):
    # LINEへのメッセージ送信ロジック
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
    print("在庫チェックを開始します...")
    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 在庫状況を判定するロジックをここに書く
        # 例: 「在庫なし」というテキストを探す
        stock_status_div = soup.find("div", class_="product__soldout-text")
        
        if stock_status_div:
            # 在庫なし
            in_stock = False
        else:
            # 在庫あり
            in_stock = True

        if in_stock:
            if os.path.exists(USER_ID_FILE):
                with open(USER_ID_FILE, "r") as f:
                    user_ids = json.load(f)
                for user_id in user_ids:
                    send_line_message(user_id, f"✅【入荷通知】商品が入荷しました！\n{URL}")
            else:
                print("[Warning] user_ids.jsonが見つかりません。")
        else:
            print("現在、在庫はありません。")

    except Exception as e:
        print(f"[Error] {e}")

if __name__ == "__main__":
    check_stock()
