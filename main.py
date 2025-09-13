import os
import requests

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  # Authorizationトークンを環境変数で管理
URLS_FILE = "urls.txt"

def load_urls():
    try:
        with open(URLS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("⚠️ urls.txt が見つかりません", flush=True)
        return []

def extract_spu_id(url):
    parts = url.split("/")
    for part in parts:
        if part.isdigit():
            return part
    return None

def check_stock(spu_id):
    # API URL（s と t は固定値で動作する場合があるが、必要なら更新）
    api_url = f"https://prod-intl-api.popmart.com/shop/v1/shop/productDetails?spuId={spu_id}&s=99a6cc23dec9e1785bddc9f5e9f5e4e3&t=1757719240"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.popmart.com/",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Cookie": "__cf_bm=bz6oTGUUXSP4wzXRFhHYWp_Zld0N.l9L1lXzquXlPEI-1757719242-1.0.1.1-cx9GkCoga_AgjhWFisI.KmxtLHK8gyxZuJO6Wt7AzKxQHISXMU01HUvyFG3Cq4l33qu4Xiqu1fky9c1vvBOAppJebqrJGZB9HPrFilN5HZs"
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 商品名と在庫状態の抽出（レスポンス構造に応じて調整）
        name = data.get("data", {}).get("spu", {}).get("name", "商品名不明")
        stock_status = data.get("data", {}).get("spu", {}).get("stockStatus", "UNKNOWN")

        if stock_status == "IN_STOCK":
            print(f"✅ {name}：在庫あり", flush=True)
            return True, name
        else:
            print(f"❌ {name}：在庫なし", flush=True)
            return False, name

    except Exception as e:
        print(f"⚠️ API取得エラー: {e}", flush=True)
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
        print("監視対象URLがありません。終了します。", flush=True)
        exit(1)

    for url in urls:
        spu_id = extract_spu_id(url)
        if not spu_id:
            print(f"⚠️ URLから商品IDを抽出できません: {url}", flush=True)
            continue

        in_stock, product_name = check_stock(spu_id)
        if in_stock:
            notify_discord(f"✅ **{product_name}** が在庫あり！\n{url}")
