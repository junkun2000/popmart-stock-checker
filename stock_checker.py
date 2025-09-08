import requests
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 環境変数を設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
GOOGLE_CREDENTIALS = os.environ.get('GOOGLE_CREDENTIALS')
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')

# 監視したい商品のURLと商品名を辞書形式で定義
POP_MART_PRODUCTS = {
    "CRYBABY-Crying-for-Love-Series-Plush-Gift-Box": "https://www.popmart.com/jp/products/4572/CRYBABY-Crying-for-Love-Series-Plush-Gift-Box",
    # 他の商品を追加
}

# Googleスプレッドシートに接続
creds_file_path = 'creds.json'
with open(creds_file_path, 'w') as f:
    f.write(GOOGLE_CREDENTIALS)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file_path, scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)
worksheet = spreadsheet.get_worksheet(0)

# LINE Bot APIのインスタンスを生成
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def check_stock_and_notify():
    in_stock_products = []

    for product_name, product_url in POP_MART_PRODUCTS.items():
        try:
            response = requests.get(product_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 在庫ありを示すボタン（例: 「今すぐ購入」ボタン）を探す
            buy_button = soup.find('a', class_='ProductDetails_buyNowButton__xxxxxx') 

            if buy_button:
                in_stock_products.append({"name": product_name, "url": product_url})
        except Exception as e:
            print(f"在庫チェック中にエラーが発生しました: {e} ({product_name})")

    if in_stock_products:
        message = "【POP MART 入荷通知】\n\n以下の商品が入荷しました！\n\n"
        for product in in_stock_products:
            message += f"・{product['name']}\n{product['url']}\n\n"
        
        # スプレッドシートからユーザーIDリストを取得
        user_ids = worksheet.col_values(1)
        
        # 全ユーザーにメッセージを送信
        for user_id in user_ids:
            try:
                line_bot_api.push_message(user_id, TextSendMessage(text=message.strip()))
                print(f"通知をユーザーID {user_id}に送信しました。")
            except Exception as e:
                print(f"ユーザーID {user_id} への送信中にエラーが発生しました: {e}")
    else:
        print("全商品まだ在庫切れです。")

if __name__ == "__main__":
    check_stock_and_notify()
