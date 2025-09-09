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

        # 商品名の取得（優先順：og:title → h1 → title）
        name = "商品名不明"
        if og := soup.find("meta", property="og:title"):
            name = og.get("content", name)
        elif h1 := soup.find("h1"):
            name = h1.text.strip()
        elif title := soup.find("title"):
            name = title.text.strip()

        # 在庫なしを示すキーワード
        sold_out_keywords = [
            "再入荷通知", "sold out", "SOLD OUT", "sold-out",
            "notify-restock", "在庫なし", "品切れ", "disabled"
        ]

        # ページ内に在庫なしキーワードが含まれているか
        page_text = soup.get_text().lower()
        if any(keyword.lower() in page_text for keyword in sold_out_keywords):
            print(f"❌ {name}：在庫なし", flush=True)
            return False, name

        # 「カートに追加」ボタンの存在と有効性を確認
        cart_btn = soup.find("button", string=lambda s: s and ("カート" in s or "add to cart" in s.lower()))
        if cart_btn and not cart_btn.has_attr("disabled"):
            print(f"✅ {name}：在庫あり", flush=True)
            return True, name

        # それ以外は在庫なしと判定
        print(f"❌ {name}：再入荷通知ボタンもなし　在庫なし", flush=True)
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
