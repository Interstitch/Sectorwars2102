module.exports = {
  apps: [
    {
      name: 'simple-test-server',
      cwd: './services/gameserver',
      script: './simple_server.py',
      env: {
        PYTHONUNBUFFERED: 1,
        PATH: process.env.PATH || '',
        // Use absolute paths for PYTHONPATH to ensure module imports work
        PYTHONPATH: '/home/runner/.local/lib/python3.10/site-packages:/home/runner/Sectorwars2102/services/gameserver',
        ENVIRONMENT: 'replit',
        DATABASE_URL: process.env.DATABASE_URL || 'postgresql://postgres:postgres@db.example.com:5432/sectorwars',
      },
      watch: false,
      autorestart: true,
      max_restarts: 10,
      interpreter: '/usr/bin/env',
      interpreter_args: 'python3',
    },
    {
      name: 'game-api-server',
      cwd: './services/gameserver',
      script: './src/main.py',
      env: {
        PYTHONUNBUFFERED: 1,
        PATH: process.env.PATH || '',
        // Use absolute paths for PYTHONPATH to ensure module imports work
        PYTHONPATH: '/home/runner/.local/lib/python3.10/site-packages:/home/runner/Sectorwars2102/services/gameserver',
        ENVIRONMENT: 'replit',
        DATABASE_URL: process.env.DATABASE_URL || 'postgresql://postgres:postgres@db.example.com:5432/sectorwars',
      },
      watch: false,
      autorestart: true,
      max_restarts: 5,
      interpreter: 'python3',
      // Disable until simple-test-server confirms Python environment is working
      env: {
        PM2_USAGE: 'disabled',
      },
    },
    {
      name: 'player-client',
      cwd: './services/player-client',
      script: 'npm',
      args: 'run dev -- --host 0.0.0.0 --port 3000',
      env: {
        API_URL: 'http://localhost:8080',
        NODE_ENV: process.env.NODE_ENV || 'development',
      },
      autorestart: true,
      max_restarts: 5,
    },
    {
      name: 'admin-ui',
      cwd: './services/admin-ui',
      script: 'npm',
      args: 'run dev -- --host 0.0.0.0 --port 3001',
      env: {
        API_URL: 'http://localhost:8080',
        NODE_ENV: process.env.NODE_ENV || 'development',
      },
      autorestart: true,
      max_restarts: 5,
    },
  ],
};