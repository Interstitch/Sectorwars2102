FROM node:18 AS node-base

# Install Python 3.11
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install PM2 globally for process management
RUN npm install -g pm2

# Create working directories
WORKDIR /app

# Copy environment files
COPY .env* ./

# Game API Server setup
WORKDIR /app/gameserver
COPY services/gameserver/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY services/gameserver .

# Player Client setup
WORKDIR /app/player-client
COPY services/player-client/package*.json ./
RUN npm install
COPY services/player-client .

# Admin UI setup
WORKDIR /app/admin-ui
COPY services/admin-ui/package*.json ./
RUN npm install
COPY services/admin-ui .

# Setup PM2 configuration
WORKDIR /app
COPY pm2.config.js .

# Expose all required ports
EXPOSE 5000 3000 3001

# Set working directory to app root
WORKDIR /app

# Start all services using PM2
CMD ["pm2-runtime", "start", "pm2.config.js"]