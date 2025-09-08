FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y 
wget 
gnupg 
&& wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - 
&& echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list 
&& apt-get update && apt-get install -y 
google-chrome-stable 
# The following packages are required for a headless browser environment
libnss3-dev 
libgconf-2-4 
libxi6 
libxcursor1 
libxcomposite1 
libxrandr2 
libasound2 
libpangocairo-1.0-0 
libgtk-3-0 
# Clean up APT cache to reduce image size
&& rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "stock_checker.py"]
