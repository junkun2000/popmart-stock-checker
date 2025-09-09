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

        # HTML保存（ローカル確認用）
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(res.text)

        soup = BeautifulSoup(res.text, "html.parser")

        # 商品名取得（title → h1 → meta）
        name = "商品名不明"
        if title := soup.find("title"):
            name = title.text.strip()
        elif h1 := soup.find("h1"):
            name = h1.text.strip()
        elif og := soup.find("meta", property="og:title"):
            name = og.get("content", name).strip()

        # 在庫あり判定（タグベース）
        if soup.find("div", string=lambda s: s and ("カートに追加する" in s or "今すぐ購入" in s)):
            print(f"✅ {name}：購入ボタンあり → 在庫あり", flush=True)
            return True, name

        # 在庫なし判定
        if soup.find("div", string=lambda s: s and "再入荷を通知" in s):
            print(f"❌ {name}：再入荷通知あり → 在庫なし", flush=True)
            return False, name

        # 判定不能
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
