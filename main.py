import os
import time
import requests
from bs4 import BeautifulSoup

# Discord Webhook URL
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# 監視するURLリスト
URLS = [
    "https://www.popmart.com/jp/products/5771/DIMOO-Shapes-in-Nature-%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA",
    "https://www.popmart.com/jp/products/4347/DIMOO-WORLD-%C3%97-DISNEY-Series-Storage-Bag-Blind-Box"
]

def check_stock(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 商品名を取得（metaタグを優先）
        product_name = None
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            product_name = og_title["content"]
        else:
            title_tag = soup.find("title")
            product_name = title_tag.get_text(strip=True) if title_tag else "商品名不明"

        # 在庫判定
        sold_out = soup.find(string="SOLD OUT")
        if sold_out:
            print(f"❌ {product_name} : SOLD OUT")
            return False, product_name
        else:
            print(f"✅ {product_name} : 在庫あり！")
            return True, product_name

    except Exception as e:
        print(f"エラー: {url} - {e}")
        return False, "商品名不明"

def send_discord_notification(product_name, url):
    if not WEBHOOK_URL:
        print("⚠️ Webhook URL が設定されていません")
        return

    data = {
        "content": f"✅ **{product_name}** が在庫あり！\n👉 {url}"
    }
    try:
        requests.post(WEBHOOK_URL, json=data, timeout=10)
        print("📢 Discord通知を送信しました")
    except Exception as e:
        print(f"通知エラー: {e}")

if __name__ == "__main__":
    while True:
        for url in URLS:
            in_stock, product_name = check_stock(url)
            if in_stock:
                send_discord_notification(product_name, url)
        time.sleep(300)  # 5分おきにチェック
