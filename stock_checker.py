import requests
from bs4 import BeautifulSoup
import os
import discord

# 環境変数を設定
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID'))

# 監視したい商品のURLと商品名を辞書形式で定義
POP_MART_PRODUCTS = {
    "CRYBABY-Crying-for-Love-Series-Plush-Gift-Box": "https://www.popmart.com/jp/products/4572/CRYBABY-Crying-for-Love-Series-Plush-Gift-Box",
    # 他の商品を追加
}

def check_stock():
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
    
    return in_stock_products

async def send_discord_notification(products):
    if not products:
        print("在庫切れの商品はありませんでした。")
        return

    message = "【POP MART 入荷通知】\n\n以下の商品が入荷しました！\n\n"
    for product in products:
        message += f"・{product['name']}\n{product['url']}\n\n"
    
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user}としてログインしました')
        channel = client.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            await channel.send(message.strip())
        else:
            print("指定されたチャンネルが見つかりません。")
        await client.close()

    await client.start(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    stocked_items = check_stock()
    if stocked_items:
        import asyncio
        asyncio.run(send_discord_notification(stocked_items))
