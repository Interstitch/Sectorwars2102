module.exports = {
  apps: [
    {
      name: 'game-api-server',
      cwd: './services/gameserver',
      script: 'python3',
      args: '-m uvicorn src.main:app --host 0.0.0.0 --port 5000 --reload',
      env: {
        PYTHONUNBUFFERED: 1,
        PATH: process.env.PATH || '',
        PYTHONPATH: './services/gameserver',
        DATABASE_URL: process.env.DATABASE_URL || 'postgresql://postgres:postgres@db.example.com:5432/sectorwars',
      },
      watch: false,  // Disable watching to prevent conflicts
      autorestart: true,
      max_restarts: 5,
      interpreter: 'python3',  // Explicitly use python3
    },
    {
      name: 'player-client',
      cwd: './services/player-client',
      script: 'npm',
      args: 'run dev -- --host 0.0.0.0 --port 3000',
      env: {
        API_URL: 'http://localhost:5000',
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
        API_URL: 'http://localhost:5000',
        NODE_ENV: process.env.NODE_ENV || 'development',
      },
      autorestart: true,
      max_restarts: 5,
    },
  ],
};