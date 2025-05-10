module.exports = {
  apps: [
    {
      name: 'game-api-server',
      cwd: './services/gameserver',
      script: 'python3',
      args: '-m uvicorn src.main:app --host 0.0.0.0 --port 5000 --reload',
      env: {
        PYTHONUNBUFFERED: 1,
        DATABASE_URL: process.env.DATABASE_URL || 'postgresql://postgres:postgres@db.example.com:5432/sectorwars',
      },
      watch: process.env.ENVIRONMENT === 'development' ? ['src'] : false,
      autorestart: true,
      max_restarts: 5,
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