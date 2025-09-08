import os
import discord
import asyncio
import requests
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
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    print("スクリプトの実行を開始します。")

    for product_name, product_url in POP_MART_PRODUCTS.items():
        try:
            response = requests.get(product_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 在庫状況を示すデータ属性を持つ要素を検索
            stock_status_div = soup.find('div', class_='goods-info-right')
            
            if stock_status_div and '再入荷を通知' not in stock_status_div.get_text():
                # '再入荷を通知'というテキストが含まれていない場合は在庫ありと判定
                in_stock_products.append({"name": product_name, "url": product_url})
                print(f"'{product_name}'の在庫が確認できました。（テキストによる判定）")
            else:
                # '再入荷を通知'というテキストが含まれている場合は在庫切れと判定
                print(f"'{product_name}'は在庫切れでした。（テキストによる判定）")

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
