module.exports = {
  apps: [
    {
      name: 'analiyx-backend',
      cwd: '/var/www/analiyx/backend',
      script: 'server.py',
      interpreter: 'python3',
      args: '',
      env: {
        NODE_ENV: 'production',
      },
      // Or use uvicorn directly:
      // script: 'uvicorn',
      // args: 'server:app --host 0.0.0.0 --port 8001 --workers 2',
      // interpreter: 'none',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/var/log/analiyx/backend-error.log',
      out_file: '/var/log/analiyx/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    },
  ],
};
