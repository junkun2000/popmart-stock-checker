import os
import requests

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SPU_ID = "5771"

def check_stock(spu_id):
    url = f"https://prod-intl-api.popmart.com/shop/v1/shop/productDetails?spuId={spu_id}&s=99a6cc23dec9e1785bddc9f5e9f5e4e3&t=1757719240"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.popmart.com/",
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",  # ← ここに有効なトークンを入れる
        "Cookie": "__cf_bm=bz6oTGUUXSP4wzXRFhHYWp_Zld0N.l9L1lXzquXlPEI-1757719242-1.0.1.1-cx9GkCoga_AgjhWFisI.KmxtLHK8gyxZuJO6Wt7AzKxQHISXMU01HUvyFG3Cq4l33qu4Xiqu1fky9c1vvBOAppJebqrJGZB9HPrFilN5HZs"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 商品名と在庫状態の抽出（構造はレスポンスに応じて調整）
        name = data.get("data", {}).get("spu", {}).get("name", "商品名不明")
        stock_status = data.get("data", {}).get("spu", {}).get("stockStatus", "unknown")

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
    in_stock, product_name = check_stock(SPU_ID)
    if in_stock:
        notify_discord(f"✅ **{product_name}** が在庫あり！\nhttps://www.popmart.com/jp/products/{SPU_ID}")
