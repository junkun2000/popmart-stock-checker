import requests
import time
from bs4 import BeautifulSoup
import os

# 環境変数からWebhook URLを取得
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# 固定の商品URLリスト（必要に応じてここに追加）
TARGET_URLS = [
    "https://www.popmart.com/collections/xxxxxx",
    "https://www.popmart.com/collections/yyyyyy",
    "https://www.popmart.com/collections/zzzzzz",
]

# 通知済み商品を記録
notified_products = set()

def check_stock(url: str) -> bool:
    """商品ページを取得して在庫を確認"""
    res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")

    # HTML構造に応じて修正
    if "Sold Out" not in soup.text:
        return True
    return False

def notify_discord(message: str):
    """Discordに通知"""
    if not DISCORD_WEBHOOK_URL:
        print("Webhook未設定")
        return
    data = {"content": message}
    requests.post(DISCORD_WEBHOOK_URL, json=data)

if __name__ == "__main__":
    while True:
        try:
            for url in TARGET_URLS:
                if check_stock(url):
                    if url not in notified_products:
                        notify_discord(f"✅ 在庫あり！ {url}")
                        notified_products.add(url)
                else:
                    if url in notified_products:
                        # 在庫がなくなったらリセット
                        notified_products.remove(url)
        except Exception as e:
            print("エラー:", e)
        time.sleep(60)  # 1分ごとにチェック
