# Use the official Selenium image with Chrome
FROM selenium/standalone-chrome

# Switch to the root user for installation if needed (though selenium/standalone-chrome usually handles this)
USER root

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Seleniumサーバーが起動するように、ベースイメージのENTRYPOINTを呼び出しつつ、
# その後にPythonスクリプトを実行するようにCMDを修正します。
# これにより、Seleniumサーバーがバックグラウンドで起動し、Pythonスクリプトがそれを利用できます。
CMD ["/opt/bin/entry_point.sh", "python", "stock_checker.py"]
