# Use the official Selenium image with Chrome
FROM selenium/standalone-chrome

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Set the command to run the script
CMD ["python", "stock_checker.py"]
