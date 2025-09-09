import os
import time
import requests
from bs4 import BeautifulSoup

# ========================
# 設定
# ========================
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")  # Renderの環境変数で設定
URLS_FILE = "urls.txt"
CHECK_INTERVAL = 60  # 秒ごと（毎分チェック）

# ========================
# 通知用関数
# ========================
def send_discord_message(message: str):
    if WEBHOOK_URL:
        try:
            requests.post(WEBHOOK_URL, json={"content": message}, timeout=10)
        except Exception as e:
            print(f"通知エラー: {e}")

# ========================
# 在庫チェック関数
# ========================
def check_stock(url: str):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 商品名（titleタグから取得）
        title = soup.title.string.strip() if soup.title else "商品名不明"

        # ボタンのテキストを確認
        button = soup.find("button", {"class": "add-to-cart-btn"})
        if button:
            text = button.get_text(strip=True)
            in_stock = text not in ["再入荷を通知", "Sold Out", "SOLD OUT"]
        else:
            in_stock = False

        return title, in_stock
    except Exception as e:
        print(f"エラー: {url} → {e}")
        return "取得失敗", False

# ========================
# メイン処理
# ========================
def main():
    # 起動通知
    send_discord_message("✅ Popmart在庫監視Botを起動しました！")

    # 監視ループ
    while True:
        try:
            with open(URLS_FILE, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("urls.txt が見つかりません")
            time.sleep(CHECK_INTERVAL)
            continue

        for url in urls:
            title, in_stock = check_stock(url)
            status = "🟢 在庫あり！" if in_stock else "⚪️ 在庫なし"
            message = f"{status}\n**{title}**\n{url}"
            print(message)  # Renderのログに出す
            if in_stock:
                send_discord_message(message)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
