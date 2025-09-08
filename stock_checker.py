import os
import discord
import asyncio
import requests

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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    print("スクリプトの実行を開始します。")

    for product_name, product_url in POP_MART_PRODUCTS.items():
        try:
            # ページを直接リクエスト
            response = requests.get(product_url, headers=headers)
            response.raise_for_status()  # ステータスコードがエラーの場合は例外を発生させる

            # レスポンスのHTMLに「在庫切れ」というテキストが含まれているかをチェック
            if "在庫なし" in response.text or "売り切れ" in response.text or "再入荷を通知" in response.text:
                print(f"'{product_name}'は在庫切れです。")
            else:
                # 在庫切れを示すテキストがなければ、在庫ありと判定
                in_stock_products.append({"name": product_name, "url": product_url})
                print(f"'{product_name}'の在庫が確認できました。")

        except requests.exceptions.RequestException as e:
            print(f"リクエスト中にエラーが発生しました: {e} ({product_name})")
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e} ({product_name})")

    return in_stock_products

async def send_discord_notification(products):
    if not products:
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
    if stocked_items:
        asyncio.run(send_discord_notification(stocked_items))
    else:
        print("在庫ありの商品はありませんでした。Discordへの通知はスキップします。")
    print("スクリプトの実行を終了しました。")
