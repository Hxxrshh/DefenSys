# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for scanners and tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    gnupg \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for Snyk
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install Docker CLI for Trivy container scanning
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update && apt-get install -y docker-ce-cli

# Install Trivy
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Semgrep
RUN pip install semgrep

# Install Snyk CLI
RUN npm install -g snyk

# Install additional security tools
RUN pip install safety gitleaks-python yara-python
RUN curl -L https://github.com/zricethezav/gitleaks/releases/download/v8.16.1/gitleaks_8.16.1_linux_x64.tar.gz | tar -xz -C /usr/local/bin
RUN chmod +x /usr/local/bin/gitleaks

# Install OWASP ZAP (for DAST)
RUN wget -q -O - https://github.com/zaproxy/zaproxy/releases/download/v2.12.0/ZAP_2.12.0_Linux.tar.gz | tar -xz -C /opt
RUN ln -s /opt/ZAP_2.12.0/zap.sh /usr/local/bin/zap.sh

# Install Nuclei
RUN curl -L https://github.com/projectdiscovery/nuclei/releases/download/v2.9.15/nuclei_2.9.15_linux_amd64.zip -o nuclei.zip \
    && unzip nuclei.zip -d /usr/local/bin \
    && rm nuclei.zip \
    && chmod +x /usr/local/bin/nuclei

# Install Nikto
RUN apt-get update && apt-get install -y nikto && rm -rf /var/lib/apt/lists/*

# Install SQLMap
RUN pip install sqlmap

# Install Nmap
RUN apt-get update && apt-get install -y nmap && rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY ./api /app/api
COPY ./scanners /app/scanners

# Create a non-root user for security
RUN useradd -m -u 1000 defensys
RUN chown -R defensys:defensys /app
USER defensys

# Expose the port the app runs on
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
