import os
import discord
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Remote

# 環境変数を設定
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID'))

# 監視したい商品のURLと商品名を辞書形式で定義
POP_MART_PRODUCTS = {
    "CRYBABY-Crying-for-Love-Series-Plush-Gift-Box": "https://www.popmart.com/jp/products/4572/CRYBABY-Crying-for-Love-Series-Plush-Gift-Box",
    "Crybaby-Crying-in-the-Wood-Series": "https://www.popmart.com/jp/products/4582/-Crybaby-Crying-in-the-Wood-Series"
}

async def check_and_notify():
    in_stock_products = []
    driver = None
    
    try:
        # ブラウザオプションを設定
        chrome_options = Options()
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # ローカルではなく、リモートのWebDriverに接続
        driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub', options=chrome_options)
        
        for product_name, product_url in POP_MART_PRODUCTS.items():
            print(f"'{product_name}'の在庫を確認中...")
            driver.get(product_url)
            
            is_in_stock = False
            
            try:
                # ページが完全に読み込まれるまで待機 (30秒に延長)
                wait = WebDriverWait(driver, 30)
                
                # 在庫がある場合に表示される「カートに追加する」ボタンの要素を探す
                stock_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'add-to-cart-button')))
                
                # ボタンが表示されていれば在庫あり
                if stock_button.is_displayed():
                    is_in_stock = True
                    print(f"'{product_name}'の在庫が確認できました。（要素の存在による判定）")

            except TimeoutException:
                # ボタンが見つからない場合は在庫切れと判断
                print(f"'{product_name}'は在庫切れでした。（ボタンが見つからなかったため）")
            except NoSuchElementException:
                print(f"'{product_name}'は在庫切れでした。（要素が存在しないため）")
            except Exception as e:
                print(f"予期せぬエラーが発生しました: {e}")
            
            if is_in_stock:
                in_stock_products.append({"name": product_name, "url": product_url})

    except WebDriverException as e:
        print(f"WebDriverエラーが発生しました: {e}")
    finally:
        if driver:
            # 確実にブラウザを終了
            driver.quit()
    
    if in_stock_products:
        message = "【POP MART 入荷通知】\n\n以下の商品が入荷しました！\n\n"
        for product in in_stock_products:
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
    try:
        asyncio.run(check_and_notify())
    finally:
        print("スクリプトの実行を終了しました。")
