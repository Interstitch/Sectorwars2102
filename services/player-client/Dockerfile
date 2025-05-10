FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies (using npm install instead of npm ci for first build)
RUN npm install

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 3000

# Start the application in development mode with hot reloading
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]