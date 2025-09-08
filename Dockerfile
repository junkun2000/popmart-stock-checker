# Pythonの公式イメージを使用
FROM python:3.9-slim

# アプリケーションコードをコンテナにコピー
WORKDIR /usr/src/app
COPY . .

# ChromeとChromeDriverをインストール
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# スクリプトを実行するコマンドを定義
CMD ["python", "stock_checker.py"]
