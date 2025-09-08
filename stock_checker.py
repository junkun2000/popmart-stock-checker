def check_stock():
    in_stock_products = []
    for product_name, product_url in POP_MART_PRODUCTS.items():
        try:
            response = requests.get(product_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 修正した部分
            buy_button = soup.find('div', class_='index_euBtn__7NmZ6')

            if buy_button and "今すぐ購入" in buy_button.text:
                in_stock_products.append({"name": product_name, "url": product_url})
                print(f"'{product_name}'の在庫が確認できました。")
            else:
                print(f"'{product_name}'は在庫切れです。")

        except requests.exceptions.RequestException as e:
            print(f"HTTPリクエストエラー: {e} ({product_name})")
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e} ({product_name})")
    
    return in_stock_products
