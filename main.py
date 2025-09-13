from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# ChromeとChromeDriverのパス（render-build.shでインストールされる場所）
CHROME_PATH = "/opt/render/project/.render/chrome/opt/google/chrome/chrome"
CHROMEDRIVER_PATH = "/opt/render/project/.render/chrome/chromedriver"

# Chromeの起動オプション
options = Options()
options.binary_location = CHROME_PATH
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# ChromeDriverのサービスを指定して起動
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# 商品ページにアクセスしてセッションを確立
driver.get("https://www.popmart.com/jp/products/5771/DIMOO-Shapes-in-Nature")
time.sleep(5)

# APIを直接叩いてレスポンスを取得
driver.get("https://prod-intl-api.popmart.com/shop/v1/shop/productDetails?spuId=5771&s=99a6cc23dec9e1785bddc9f5e9f5e4e3&t=1757719240")
time.sleep(3)

# レスポンス内容を表示
print(driver.page_source)

driver.quit()
