# Use the official Selenium image with Chrome
FROM selenium/standalone-chrome

# Create a non-root user
RUN groupadd -r chrome && useradd -r -g chrome -G audio,video chrome \
    && mkdir -p /app && chown chrome:chrome /app

# Set the working directory
WORKDIR /app

# Switch to the non-root user
USER chrome

# Copy the requirements file into the container
COPY --chown=chrome:chrome requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY --chown=chrome:chrome . .

# Set the command to run the script
CMD ["python", "stock_checker.py"]
