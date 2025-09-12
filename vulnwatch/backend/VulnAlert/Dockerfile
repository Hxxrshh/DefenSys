# Use Python slim image for better compatibility with CLI tools
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for npm-audit (needed for dependency scanning)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set environment variables
ENV FLASK_APP=src/enhanced_server.py
ENV PYTHONPATH=/app

# Make the initialization script executable
RUN chmod +x src/init_enhanced_db.py

# Expose Flask server port
EXPOSE 5000

# Initialize database and start server
CMD ["sh", "-c", "python src/simple_server.py"]
