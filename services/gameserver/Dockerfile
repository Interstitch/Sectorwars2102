FROM python:3.11

WORKDIR /app

# Install Docker CLI for container monitoring
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Configure Poetry: Don't create virtual environment, install dependencies globally
RUN poetry config virtualenvs.create false

# Copy dependency files first for better caching
COPY pyproject.toml poetry.lock* /app/

# Install dependencies (generate lock if missing, but don't update existing)
RUN poetry lock --no-update 2>/dev/null || poetry lock && poetry install --no-root

# Copy the rest of the project
COPY . /app/

# Add executable permission to the scripts
RUN chmod +x /app/start.sh

# Keep the container running with the start script
CMD ["sh", "-c", "echo 'Starting gameserver...' && /app/start.sh"]
