import os
import json
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets APIの認証情報
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = os.environ.get("GOOGLE_CREDENTIALS")
creds_dict = json.loads(creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
worksheet = client.open("LINE Bot User IDs").sheet1

# LINE Bot API
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

# 在庫チェック対象のURLをリストで定義
URLS_TO_MONITOR = [
    "https://www.popmart.com/jp/products/3889/THE-MONSTERS-%E3%82%B3%E3%82%AB%E3%83%BB%E3%82%B3%E3%83%BC%E3%83%A9-%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA-%E3%81%AC%E3%81%84%E3%81%90%E3%82%8B%E3%81%BF",
    "https://www.popmart.com/jp/products/3891/THE-MONSTERS-Have-a-Seat-%E3%81%AC%E3%81%84%E3%81%90%E3%82%8B%E3%81%BF-%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA",
    "https://www.popmart.com/jp/products/4469/THE-MONSTERS-ANGEL-IN-CLOUDS-%E3%81%AC%E3%81%84%E3%81%90%E3%82%8B%E3%81%BF",
    "https://www.popmart.com/jp/products/5251/THE-MONSTERS-FALL-IN-WILD-%E3%81%AC%E3%81%84%E3%81%90%E3%82%8B%E3%81%BF%E3%83%9A%E3%83%B3%E3%83%80%E3%83%B3%E3%83%88",
    "https://www.popmart.com/jp/products/3884",
    "https://www.popmart.com/jp/products/6935",
    "https://www.popmart.com/jp/products/4572/CRYBABY-Crying-for-Love-Series-Plush-Gift-Box"
]

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
        user_ids = worksheet.col_values(1)
        print(f"ユーザーIDを読み込みました: {user_ids}")
    except Exception as e:
        print(f"[Error] スプレッドシートの読み込みに失敗しました: {e}")
        return

    # 在庫が見つかった商品を格納するリスト
    found_products = []

    for url in URLS_TO_MONITOR:
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 商品名を取得（タイトルタグから）
            title_tag = soup.find('title')
            if title_tag:
                full_title = title_tag.get_text(strip=True)
                product_name = full_title.split('|')[0].strip()
            else:
                product_name = "商品名不明"

            # 在庫判定ロジック
            add_to_cart_button = soup.find('button', class_='add-to-cart-button')
            in_stock = add_to_cart_button is not None

            if in_stock:
                print(f"✅ 在庫が見つかりました: {url}")
                # 入荷した商品をリストに追加
                found_products.append(f"・{product_name}\n{url}")
            else:
                print(f"現在、在庫はありません: {url}")

        except requests.exceptions.RequestException as e:
            print(f"[Request Error] {url} - {e}")
        except Exception as e:
            print(f"[Error] {url} - {e}")

    # 在庫が見つかった商品がある場合のみ、メッセージをまとめて送信
    if found_products:
        message_text = "✅【入荷通知】以下の商品が入荷しました！\n\n" + "\n\n".join(found_products)
        for user_id in user_ids:
            send_line_message(user_id, message_text)

if __name__ == "__main__":
    check_stock()
