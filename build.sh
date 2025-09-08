#!/usr/bin/env bash

# Install Google Chrome
curl -fsSL https://www.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install -y google-chrome-stable

# Install ChromeDriver
CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}')
CHROME_VERSION_MAJOR=$(echo $CHROME_VERSION | cut -d'.' -f1)
LATEST_CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION_MAJOR}")
curl -sS "https://chromedriver.storage.googleapis.com/${LATEST_CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" -o chromedriver.zip
unzip chromedriver.zip
mv chromedriver /usr/local/bin/

# Make the driver executable
chmod +x /usr/local/bin/chromedriver

# Continue with the original build command
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
python check_and_notify.py
