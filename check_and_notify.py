import os
import json
import requests
from bs4 import BeautifulSoup

USER_ID_FILE = "user_ids.json"
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
# テスト用の在庫あり商品URLに更新
URL = "https://www.popmart.com/jp/products/3973/THE-MONSTERS-CONSTELLATION-SERIES"

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
        
        # 「カートに追加する」ボタンのテキストをチェック
        add_to_cart_button = soup.find('button', string="カートに追加する")
        
        # ボタンが存在すれば「在庫あり」と判定
        in_stock = add_to_cart_button is not None

        if in_stock:
            print("✅ 在庫が見つかりました！")
            if os.path.exists(USER_ID_FILE):
                with open(USER_ID_FILE, "r") as f:
                    user_ids = json.load(f)
                for user_id in user_ids:
                    send_line_message(user_id, f"✅【テスト通知】在庫ありと検知しました！\n{URL}")
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
