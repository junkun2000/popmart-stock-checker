import os
import discord
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 環境変数を設定
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID'))

# 監視したい商品のURLと商品名を辞書形式で定義
POP_MART_PRODUCTS = {
    "CRYBABY-Crying-for-Love-Series-Plush-Gift-Box": "https://www.popmart.com/jp/products/4572/CRYBABY-Crying-for-Love-Series-Plush-Gift-Box",
}

def check_stock():
    in_stock_products = []
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        for product_name, product_url in POP_MART_PRODUCTS.items():
            driver.get(product_url)
            
            is_in_stock = False

            try:
                # ページの表示をより確実にするため、少し待つ
                time.sleep(5)
                
                # 1. 「カートに追加する」ボタンの存在を待つ（XPATH）
                # テキストベースのXPATHは最も確実な方法の一つです
                wait = WebDriverWait(driver, 20)
                add_to_cart_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "カートに追加する")]')))
                
                if add_to_cart_button:
                    is_in_stock = True
                    print(f"'{product_name}'の在庫が確認できました。（「カートに追加する」ボタンによる判定）")

            except (TimeoutException, NoSuchElementException):
                # 2. ボタンが見つからなかった場合、在庫なしを示すテキストを探す
                print(f"「カートに追加する」ボタンが見つかりませんでした。在庫なしの可能性をチェックします。")
                try:
                    # 「再入荷を通知」ボタンの存在をチェック
                    restock_notify_button = driver.find_element(By.XPATH, '//*[contains(text(), "再入荷を通知")]')
                    if restock_notify_button:
                        is_in_stock = False
                        print(f"'{product_name}'は在庫切れです。（「再入荷を通知」ボタンによる判定）")
                except NoSuchElementException:
                    # どちらのボタンも見つからない場合は在庫ありの可能性
                    # 例外処理を通過した場合、次のステップで在庫ありと見なす
                    is_in_stock = True


            if is_in_stock:
                in_stock_products.append({"name": product_name, "url": product_url})
            
            print("---")
            if is_in_stock:
                print(f"'{product_name}'の在庫が確認できました。")
            else:
                print(f"'{product_name}'は在庫切れです。")

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
    print("スクリプトの実行を開始します。")
    stocked_items = check_stock()
    if stocked_items:
        asyncio.run(send_discord_notification(stocked_items))
    else:
        print("在庫ありの商品はありませんでした。Discordへの通知はスキップします。")
    print("スクリプトの実行を終了しました。")
