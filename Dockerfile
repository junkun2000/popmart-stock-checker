# Use a Python base image with Alpine for a smaller footprint
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install dependencies for Chrome and the Chrome driver
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get install -y \
    google-chrome-stable \
    # The following packages are required for a headless browser environment
    libnss3-dev \
    libgconf-2-4 \
    libxi6 \
    libxcursor1 \
    libxcomposite1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    # Clean up APT cache to reduce image size
    && rm -rf /var/lib/apt/lists/*

# Install Chrome driver using Selenium's built-in manager
# The Selenium library will automatically handle the driver installation
# during the initial run of the script
RUN pip install --upgrade pip

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the application code into the container
COPY . .

# Set the command to run the script
CMD ["python", "stock_checker.py"]
