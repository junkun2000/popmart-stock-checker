import os
import json
import requests
from bs4 import BeautifulSoup

USER_ID_FILE = "user_ids.json"
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
# 在庫チェック対象のURLを更新
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
        # HTTPステータスコードが成功でない場合はエラーを出力
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 「再入荷を通知」というテキストが存在するかを探す
        notify_text_button = soup.find(string="再入荷を通知")
        
        # 「再入荷を通知」テキストが見つからなければ「在庫あり」と判定
        in_stock = notify_text_button is None

        if in_stock:
            print("✅ 在庫が見つかりました！")
            if os.path.exists(USER_ID_FILE):
                with open(USER_ID_FILE, "r") as f:
                    user_ids = json.load(f)
                for user_id in user_ids:
                    send_line_message(user_id, f"✅【入荷通知】商品が入荷しました！\n{URL}")
            else:
                print("[Warning] user_ids.jsonが見つかりません。")
        else:
            print("現在、在庫はありません。")

    except requests.exceptions.RequestException as e:
        print(f"[Request Error] {e}")
    except Exception as e:
        print(f"[Error] {e}")

if __name__ == "__main__":
    check_stock()
