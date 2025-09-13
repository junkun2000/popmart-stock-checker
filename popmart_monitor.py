import cloudscraper
from bs4 import BeautifulSoup
import requests
import os
import pathlib
import time
import random
from datetime import datetime

# 監視対象URLリスト
PRODUCT_URLS = [
    "https://www.popmart.com/jp/products/3889/THE-MONSTERS-%E3%82%B3%E3%82%AB%E3%83%BB%E3%82%B3%E3%83%BC%E3%83%A9-%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA-%E3%81%AC%E3%81%84%E3%81%90%E3%82%8B%E3%81%BF",
    "https://www.popmart.com/jp/products/5771/DIMOO-Shapes-in-Nature-%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA"
]

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
STATUS_DIR = "statuses"
pathlib.Path(STATUS_DIR).mkdir(exist_ok=True)

def fetch_page(url):
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
        "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    res = scraper.get(url, headers=headers)
    return res.text

def check_stock_and_image_and_name(html):
    soup = BeautifulSoup(html, "html.parser")
    
    # 在庫判定
    text = soup.get_text()
    if "カートに追加する" in text or "今すぐ購入" in text:
        status = "in_stock"
    elif "再入荷を通知する" in text:
        status = "out_of_stock"
    else:
        status = "unknown"

    # 商品画像
    og_img = soup.find("meta", property="og:image")
    image_url = og_img["content"] if og_img else None

    # 商品名（OGタイトル→h1タグ→不明）
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        product_name = og_title["content"]
    else:
        h1_title = soup.find("h1")
        product_name = h1_title.get_text(strip=True) if h1_title else "不明な商品"

    return status, image_url, product_name

def load_last_status(product_name):
    file_path = pathlib.Path(STATUS_DIR) / f"{product_name}.txt"
    if file_path.exists():
        return file_path.read_text().strip()
    return "unknown"

def save_last_status(product_name, status):
    file_path = pathlib.Path(STATUS_DIR) / f"{product_name}.txt"
    file_path.write_text(status)

def notify_discord(product_name, status, url, image_url=None):
    color = 0x00ff00 if status == "in_stock" else 0xff0000
    status_text = "✅ 在庫あり" if status == "in_stock" else "❌ 在庫なし"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    embed = {
        "title": f"{product_name} 在庫変化検知",
        "description": f"{status_text}\n[商品ページはこちら]({url})\n🕒 {timestamp}",
        "color": color
    }
    if image_url:
        embed["thumbnail"] = {"url": image_url}

    payload = {"embeds": [embed]}
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ Discord通知送信エラー: {e}")

def main():
    print("🚀 POPMART監視スクリプトを起動しました")
    while True:
        for url in PRODUCT_URLS:
            try:
                html = fetch_page(url)
                current_status, image_url, product_name = check_stock_and_image_and_name(html)
            except Exception as e:
                print(f"❌ {url} の取得でエラー: {e}")
                continue

            last_status = load_last_status(product_name)

            # 初回判定や在庫変化時は通知
            if last_status == "unknown" or (current_status != last_status and current_status != "unknown"):
                notify_discord(product_name, current_status, url, image_url)
                save_last_status(product_name, current_status)
                print(f"🔔 {product_name} 在庫変化: {last_status} → {current_status}")
            else:
                print(f"{product_name} の在庫変化なし ({current_status})")

        # ランダムスリープ 25〜45秒
        sleep_time = random.randint(25, 45)
        print(f"次のチェックまで {sleep_time} 秒待機...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ スクリプト起動エラー: {e}")
