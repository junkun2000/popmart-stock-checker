import os
import time
import requests
import re

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
URLS_FILE = "urls.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/123.0.0.0 Safari/537.36"
}

def load_urls():
    try:
        with open(URLS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("⚠️ urls.txt が見つかりません", flush=True)
        return []

def extract_product_id(url):
    match = re.search(r'/products/(\d+)/', url)
    return match.group(1) if match else None

def check_stock_via_api(product_id):
    try:
        api_url = f"https://www.popmart.com/api/product/detail?id={product_id}"
        res = requests.get(api_url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json()

        product = data.get("product", {})
        name = product.get("name", "商品名不明")
        in_stock = product.get("stock", False)

        if in_stock:
            print(f"✅ {name} : 在庫あり", flush=True)
            return True, name
        else:
            print(f"❌ {name} : 在庫なし", flush=True)
            return False, name

    except Exception as e:
        print(f"APIエラー: {e}", flush=True)
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

    while True:
        for url in urls:
            product_id = extract_product_id(url)
            if not product_id:
                print(f"⚠️ URLから商品IDを抽出できません: {url}", flush=True)
                continue

            in_stock, product_name = check_stock_via_api(product_id)
            if in_stock:
                notify_discord(f"✅ **{product_name}** が在庫あり！\n{url}")
        time.sleep(60)
