import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
URLS_FILE = "urls.txt"

def load_urls():
    try:
        with open(URLS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("⚠️ urls.txt が見つかりません", flush=True)
        return []

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=chrome_options)

def check_stock(driver, url):
    try:
        driver.get(url)

        # ページ描画完了を待つ（bodyタグが表示されるまで最大10秒）
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        name = driver.title.strip() or "商品名不明"

        # stale対策：body要素の取得をリトライ
        for _ in range(3):
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                page_text = body.text.lower()
                break
            except StaleElementReferenceException:
                time.sleep(1)
        else:
            print(f"⚠️ {name}：body要素の取得に失敗", flush=True)
            return False, name

        # 在庫あり判定
        if "カートに追加する" in page_text or "今すぐ購入" in page_text or "add to cart" in page_text:
            print(f"✅ {name}：購入ボタンあり → 在庫あり", flush=True)
            return True, name

        # 在庫なし判定
        if "再入荷を通知" in page_text or "sold out" in page_text:
            print(f"❌ {name}：再入荷通知あり → 在庫なし", flush=True)
            return False, name

        print(f"❌ {name}：在庫判定できず → 在庫なし", flush=True)
        return False, name

    except Exception as e:
        print(f"⚠️ エラー発生: {e}", flush=True)
        return False, "商品名不明"

def notify_discord(message):
    if not WEBHOOK_URL:
        print("⚠️ Webhook URL が設定されていません", flush=True)
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": message}, timeout=10)
        print("📢 Discord通知を送信しました", flush=True)
    except Exception as e:
        print(f"通知エラー: {e}", flush=True)

if __name__ == "__main__":
    urls = load_urls()
    if not urls:
        print("監視対象URLなし。終了します。", flush=True)
        exit(1)

    driver = create_driver()

    while True:
        for url in urls:
            in_stock, product_name = check_stock(driver, url)
            if in_stock:
                notify_discord(f"✅ **{product_name}** が在庫あり！\n{url}")
        time.sleep(60)
