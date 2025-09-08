import requests
from bs4 import BeautifulSoup
import os
import discord
import asyncio

# 環境変数を設定
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID'))

# 監視したい商品のURLと商品名を辞書形式で定義
POP_MART_PRODUCTS = {
    "CRYBABY-Crying-for-Love-Series-Plush-Gift-Box": "https://www.popmart.com/jp/products/4572/CRYBABY-Crying-for-Love-Series-Plush-Gift-Box",
    # 監視対象を増やす場合はここに追加
}

def check_stock():
    in_stock_products = []
    for product_name, product_url in POP_MART_PRODUCTS.items():
        try:
            response = requests.get(product_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 修正した部分: 共通のクラス名で要素を検索し、テキストで在庫を判断
            buy_button = soup.find('div', class_='index_euBtn__7NmZ6')

            if buy_button and "今すぐ購入" in buy_button.text:
                in_stock_products.append({"name": product_name, "url": product_url})
                print(f"'{product_name}'の在庫が確認できました。")
            else:
                print(f"'{product_name}'は在庫切れです。")

        except requests.exceptions.RequestException as e:
            print(f"HTTPリクエストエラー: {e} ({product_name})")
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e} ({product_name})")
    
    return in_stock_products

async def send_discord_notification(products):
    if not products:
        print("在庫ありの商品はありませんでした。")
        return

    message = "【POP MART 入荷通知】\n\n以下の商品が入荷しました！\n\n"
    for product in products:
        message += f"・{product['name']}\n{product['url']}\n\n"
