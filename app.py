import os
import json
from flask import Flask, request, abort
from linebot import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# 環境変数を設定
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
GOOGLE_CREDENTIALS = os.environ.get('GOOGLE_CREDENTIALS')
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')

# JSON認証情報をファイルに書き込み
creds_file_path = 'creds.json'
with open(creds_file_path, 'w') as f:
    f.write(GOOGLE_CREDENTIALS)

# Googleスプレッドシートに接続
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file_path, scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)
worksheet = spreadsheet.get_worksheet(0) # 1番目のシート

# WebhookHandlerのインスタンスを生成
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ユーザーIDがスプレッドシートに存在するか確認する関数
def is_user_id_exists(user_id):
    try:
        list_of_ids = worksheet.col_values(1)
        return user_id in list_of_ids
    except Exception as e:
        print(f"スプレッドシートの読み込み中にエラーが発生しました: {e}")
        return False

# LINEからのメッセージを処理するウェブフック
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# メッセージ受信時のイベントハンドラ
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    
    if not is_user_id_exists(user_id):
        try:
            worksheet.append_row([user_id])
            print(f"新しいユーザーIDを追加しました: {user_id}")
        except Exception as e:
            print(f"スプレッドシートへの書き込み中にエラーが発生しました: {e}")

# アプリケーションの起動
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ.get("PORT", 5000))
