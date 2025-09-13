from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome/chrome"

driver = webdriver.Chrome(options=options)

# 商品ページを開いてセッションを確立
driver.get("https://www.popmart.com/jp/products/5771/DIMOO-Shapes-in-Nature")
time.sleep(5)

# APIを直接叩く
driver.get("https://prod-intl-api.popmart.com/shop/v1/shop/productDetails?spuId=5771&s=99a6cc23dec9e1785bddc9f5e9f5e4e3&t=1757719240")
time.sleep(3)

print(driver.page_source)

driver.quit()
