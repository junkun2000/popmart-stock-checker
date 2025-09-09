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
    # og:title があれば優先
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        return og_title["content"]

    # title タグ fallback
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

        # 「再入荷を通知」がある＝売り切れ
        soldout = soup.find(string=lambda text: text and "再入荷を通知" in text)
        if soldout:
            print(f"❌ {title} : SOLD OUT", flush=True)
            return None
        else:
            print(f"✅ {title} : 在庫あり！", flush=True)
            return title
    except Exception as e:
        print(f"エラー: {url} - {e}", flush=True)
        return None

def notify_discord(message):
    if not WEBHOOK_URL:
        print("⚠️ Webhook URL が設定されていません", flush=True)
        return
    try:
        request
