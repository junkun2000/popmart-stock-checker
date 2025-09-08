# Use the official Selenium image with Chrome
FROM selenium/standalone-chrome

# Switch to the non-root user
USER root

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Set the command to run the script
CMD ["python", "stock_checker.py"]
