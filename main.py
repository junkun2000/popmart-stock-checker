import os
import time
import requests
from bs4 import BeautifulSoup

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
URLS_FILE = "urls.txt"

def load_urls():
    try:
        with open(URLS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("⚠️ urls.txt が見つかりません", flush=True)
        return []

def check_stock(url):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        title = soup.find("title").get_text(strip=True)

        # 在庫判定（例: ボタンのテキストを確認）
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
        requests.post(WEBHOOK_URL, json={"content": message}, timeout=10)
    except Exception as e:
        print(f"Discord通知失敗: {e}", flush=True)

if __name__ == "__main__":
    urls = load_urls()
    if not urls:
        print("監視対象URLなし。終了します。", flush=True)
        exit(1)

    while True:
        try:
            for url in urls:
                name = check_stock(url)
                if name:
                    notify_discord(f"✅ {name}\n{url}")
            time.sleep(60)
        except Exception as e:
            print(f"ループ内でエラー発生: {e}", flush=True)
