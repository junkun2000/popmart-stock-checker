import os
import time
import requests
from bs4 import BeautifulSoup

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

def check_stock(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # 商品名の取得（metaタグ or title）
        name = "商品名不明"
        if og := soup.find("meta", property="og:title"):
            name = og.get("content", name)
        elif title := soup.find("title"):
            name = title.text.strip()

        # 在庫なし判定：「再入荷を通知」ボタンがある
        if soup.find("div", string=lambda s: s and "再入荷を通知" in s):
            print(f"❌ {name}：再入荷通知ボタンあり → 在庫なし", flush=True)
            return False, name

        # 在庫あり判定：「カートに追加する」または「今すぐ購入」ボタンがある
        if soup.find("div", string=lambda s: s and ("カートに追加する" in s or "今すぐ購入" in s)):
            print(f"✅ {name}：購入ボタンあり → 在庫あり", flush=True)
            return True, name

        # 判定不能 → 在庫なしとみなす
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

    while True:
        for url in urls:
            in_stock, product_name = check_stock(url)
            if in_stock:
                notify_discord(f"✅ **{product_name}** が在庫あり！\n{url}")
        time.sleep(60)
