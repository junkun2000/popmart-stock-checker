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

def get_product_name(soup):
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        return og_title["content"].strip()
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    title_tag = soup.find("title")
    if title_tag:
        return title_tag.get_text(strip=True)
    return "商品名不明"

def check_stock(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        title = get_product_name(soup)

        # 再入荷通知系の文言を探して、すぐに在庫なし判定
        restock_notify = soup.find(string=lambda t: t and (
            "再入荷通知" in t or "再入荷を通知" in t or "Notify me when restocked" in t
        ))
        if restock_notify:
            print(f"❌ {title} : 再入荷通知あり → 在庫なし", flush=True)
            return False, title

        # カート系のボタンを探して、有効性をチェック
        btn = soup.find("button", string=lambda t: t and (
            "カート" in t or "Add to cart" in t or "購入" in t
        ))
        if btn:
            btn_text = btn.get_text(strip=True)
            btn_disabled = btn.has_attr("disabled")
            btn_classes = btn.get("class", [])

            sold_out_indicators = ["sold-out", "disabled", "notify-restock", "soldout"]
            if btn_disabled or any(c in sold_out_indicators for c in btn_classes) or "SOLD OUT" in btn_text:
                print(f"❌ {title} : ボタン無効化検出 (text={btn_text}, classes={btn_classes}, disabled={btn_disabled}) → 在庫なし", flush=True)
                return False, title

            print(f"✅ {title} : ボタン有効 (text={btn_text}, classes={btn_classes}) → 在庫あり", flush=True)
            return True, title

        # 上記どれにも当てはまらなければ在庫なしにフォールバック
        print(f"❌ {title} : 再入荷通知もボタンもなし → 在庫なし", flush=True)
        return False, title

    except Exception as e:
        print(f"エラー: {url} - {e}", flush=True)
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
