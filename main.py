import requests
from bs4 import BeautifulSoup
from typing import Tuple

def check_stock_requests(url: str) -> Tuple[bool, str]:
    """requestsベースでまず判定。True=在庫あり, False=在庫なし"""
    res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    text = res.text
    soup = BeautifulSoup(text, "html.parser")

    # 商品名（meta og:title優先）
    meta_title = soup.find("meta", property="og:title")
    title = meta_title["content"].strip() if meta_title and meta_title.get("content") else (soup.title.string.strip() if soup.title else "商品名不明")

    # 再入荷通知系の文字列があれば在庫なし
    if ("再入荷を通知" in text) or ("再入荷通知" in text) or ("再入荷をお知らせ" in text):
        return False, title

    # 「カートに入れる」「購入する」等があれば在庫あり
    if ("カートに入れる" in text) or ("カートに追加" in text) or ("購入する" in text) or ("Add to cart" in text):
        return True, title

    # フォールバック（英語や別表記が混在する場合の保険）
    if "Sold Out" in text or "売り切れ" in text:
        return False, title

    # 決め手が無ければ None 相当（ここでは False を返すか、上位ロジックで Playwright を呼ぶ）
    return None, title
