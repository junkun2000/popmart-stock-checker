import os
import discord
import asyncio
import requests
import json
import re
from bs4 import BeautifulSoup

# 環境変数を設定
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID'))

# 監視したい商品のURLと商品名を辞書形式で定義
POP_MART_PRODUCTS = {
    "CRYBABY-Crying-for-Love-Series-Plush-Gift-Box": "https://www.popmart.com/jp/products/4572/CRYBABY-Crying-for-Love-Series-Plush-Gift-Box",
    "Crybaby-Crying-in-the-Wood-Series": "https://www.popmart.com/jp/products/4582/-Crybaby-Crying-in-the-Wood-Series"
}

def check_stock():
    in_stock_products = []
    
    # Sessionを使用し、クッキーとセッションを維持
    session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.popmart.com/jp/',
        'DNT': '1',  # Do Not Track
        'Connection': 'keep-alive',
    }
    
    print("スクリプトの実行を開始します。")

    for product_name, product_url in POP_MART_PRODUCTS.items():
        try:
            # 1. 最初にWebページにアクセスしてセッションを確立
            response = session.get(product_url, headers=headers)
            response.raise_for_status()
            
            # 2. HTMLから商品IDを抽出
            product_id_match = re.search(r'productId: (\d+),', response.text)
            
            if product_id_match:
                product_id = product_id_match.group(1)
                
                # 3. 確立したセッションでAPIを呼び出す
                api_url = f'https://www.popmart.com/jp/api/product/stock/detail?productId={product_id}'
                api_response = session.get(api_url, headers=headers)
                api_response.raise_for_status()
                stock_data = api_response.json()
                
                is_in_stock = False
                if 'data' in stock_data:
                    for sku in stock_data['data']:
                        if not sku.get('isSoldOut') and sku.get('quantity', 0) > 0:
                            is_in_stock = True
                            break

                if is_in_stock:
                    in_stock_products.append({"name": product_name, "url": product_url})
                    print(f"'{product_name}'の在庫が確認できました。（APIによる判定）")
                else:
                    print(f"'{product_name}'は在庫切れでした。（APIによる判定）")
            else:
                print(f"'{product_name}'の商品IDが見つかりませんでした。HTMLの変更を確認してください。")

        except requests.exceptions.RequestException as e:
            print(f"リクエスト中にエラーが発生しました: {e} ({product_name})")
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e} ({product_name})")
    
    return in_stock_products

async def send_discord_notification(products):
    if not products:
        print("在庫ありの商品はありませんでした。Discordへの通知はスキップします。")
        return
    
    message = "【POP MART 入荷通知】\n\n以下の商品が入荷しました！\n\n"
    for product in products:
        message += f"・{product['name']}\n{product['url']}\n\n"
    
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'Bot {client.user} としてログインしました')
        channel = client.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            await channel.send(message.strip())
            print("Discordに通知を送信しました。")
        else:
            print("指定されたチャンネルIDが見つかりません。")
        await client.close()

    try:
        await client.start(DISCORD_BOT_TOKEN)
    except discord.errors.LoginFailure:
        print("Discord Botトークンが無効です。")
    except Exception as e:
        print(f"Discordへの送信中にエラーが発生しました: {e}")

if __name__ == "__main__":
    stocked_items = check_stock()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_discord_notification(stocked_items))
    print("スクリプトの実行を終了しました。")
