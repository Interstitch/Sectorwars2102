module.exports = {
  apps: [
    {
      name: 'game-api-server',
      cwd: '/app/gameserver',
      script: 'uvicorn',
      args: 'src.main:app --host 0.0.0.0 --port 5000 --reload',
      interpreter: 'python3',
      env: {
        PYTHONUNBUFFERED: 1,
      },
      watch: process.env.ENVIRONMENT === 'development' ? ['src'] : false,
      autorestart: true,
    },
    {
      name: 'player-client',
      cwd: '/app/player-client',
      script: 'npm',
      args: 'run dev -- --host 0.0.0.0 --port 3000',
      env: {
        API_URL: process.env.ENVIRONMENT === 'replit' 
          ? 'http://localhost:5000' 
          : 'http://localhost:5000',
      },
      autorestart: true,
    },
    {
      name: 'admin-ui',
      cwd: '/app/admin-ui',
      script: 'npm',
      args: 'run dev -- --host 0.0.0.0 --port 3001',
      env: {
        API_URL: process.env.ENVIRONMENT === 'replit' 
          ? 'http://localhost:5000' 
          : 'http://localhost:5000',
      },
      autorestart: true,
    },
  ],
};