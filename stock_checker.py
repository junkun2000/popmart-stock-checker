import os
import discord
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    
    # ブラウザオプションを設定
    chrome_options = Options()
    # ユーザーエージェントを偽装
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    # ボットと認識されにくいように、ヘッドレスモードを無効化
    # Render環境では通常有効にしますが、今回はボット対策を徹底するために無効化します
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        for product_name, product_url in POP_MART_PRODUCTS.items():
            print(f"'{product_name}'の在庫を確認中...")
            driver.get(product_url)
            
            is_in_stock = False
            
            try:
                # 明示的な待機: 「カートに追加する」ボタンが表示されるまで最大20秒待つ
                wait = WebDriverWait(driver, 20)
                add_to_cart_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[contains(@class, "add_to_cart")]')))
                
                # ボタンのテキストを再確認
                if "カートに追加する" in add_to_cart_button.text:
                    is_in_stock = True
                    print(f"'{product_name}'の在庫が確認できました。（「カートに追加する」ボタンによる判定）")

            except (TimeoutException, NoSuchElementException):
                # ボタンが見つからなかった場合、在庫切れと判定
                print(f"'{product_name}'は在庫切れでした。（「カートに追加する」ボタンが見つからなかったため）")
                is_in_stock = False
            
            if is_in_stock:
                in_stock_products.append({"name": product_name, "url": product_url})

    except WebDriverException as e:
        print(f"WebDriverエラーが発生しました: {e}")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
    finally:
        if driver:
            driver.quit()
    
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
