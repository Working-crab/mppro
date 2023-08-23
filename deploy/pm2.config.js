'use strict';

const path = require('path');
const dir = path.normalize(path.join(path.dirname(module.filename), '..'));

const defaults = {
  name: 'SET ME UP',
  script: 'SET ME UP',
  wait_ready: true, 
  autorestart: false,
  kill_timeout: 10000,
  instances : 1,
  max_restarts: 0,
  interpreter : 'venv/bin/python3',
  log_file: 'logs/pm2/default.log',
  cwd: '',
  env: {
    PYTHONPATH: 'src/',
    MONITORING_INITIATOR: 'default',
  },
}

module.exports = {
  apps: [
    {
      ...defaults,
      autorestart: true,
      cron_restart: '*/5 * * * *',
      name: 'ui_backend',
      script: 'venv/bin/python3 -m uvicorn ui_backend.main:app --port 8000',
      log_file: 'logs/pm2/ui_backend.log',
      interpreter: undefined,
      env: {
        PYTHONPATH: 'src/',
        MONITORING_INITIATOR: 'ui_backend',
      },
    },
    // {
    //   ...defaults,
    //   autorestart: true,
    //   name: 'mp_pro_ui_telega_2',
    //   script: '/data/venv/bin/python -m uvicorn ui_backend.main:app --reload',
    //   log_file: '/data/logs/pm2/mp_pro_ui_telega_2.log',
    //   interpreter: undefined,
    // },
    {
      ...defaults,
      name: 'bot_message_sender',
      script: 'src/ui_backend/bot_message_sender/bot_message_sender.py',
      log_file: 'logs/pm2/bot_message_sender.log',
      env: {
        PYTHONPATH: 'src/',
        MONITORING_INITIATOR: 'bot_message_sender',
      },
    },
    {
      ...defaults,
      name: 'wb_routines', // setups wb categories to caches daily
      script: 'src/wb_routines/main.py',
      log_file: 'logs/pm2/wb_routines.log',
      cron_restart: '0 0 * * *', // once per day
      env: {
        PYTHONPATH: 'src/',
        MONITORING_INITIATOR: 'wb_routines',
      },
    },
    {
      ...defaults,
      name: 'user_automation',
      script: 'src/user_automation/main.py',
      log_file: 'logs/pm2/user_automation.log',
      cron_restart: '*/3 * * * *', // once per 3 minutes
      env: {
        PYTHONPATH: 'src/',
        MONITORING_INITIATOR: 'user_automation',
      },
    },

    // admin_dashboard_monitoring
    {
      name: 'admin_dashboard_monitoring_frontend',
      script: 'serve',
      exec_mode: 'cluster',
      instances: 2,
      wait_ready: true,
      kill_timeout: 120000,
      watch: false,
      cwd: dir,
      env: {
        NODE_PATH: path.join(dir, 'src/admin_dashboard/frontend/analytics-service'),
        PM2_SERVE_PATH: path.join(dir, 'src/admin_dashboard/frontend/analytics-service/dist/'),
        PM2_SERVE_PORT: 3002,
        PM2_SERVE_SPA: 'true',
        PM2_SERVE_HOMEPAGE: '/index.html'
      },
    },
    {
      ...defaults,
      name: 'admin_dashboard_monitoring_backend',
      script: 'venv/bin/python3 -m uvicorn admin_dashboard.backend.main:app --port 8001',
      log_file: 'logs/pm2/admin_dashboard_monitoring_backend.log',
      interpreter: undefined,
      env: {
        PYTHONPATH: 'src/',
        MONITORING_INITIATOR: 'admin_dashboard_monitoring_backend',
      },
    },

    // wb_scraper_api
    {
      ...defaults,
      name: 'wb_scraper_api',
      autorestart: true,
      script: 'venv/bin/python3 -m uvicorn wb_scraper_api.main:app --port 8002', 
      log_file: 'logs/pm2/wb_scraper_api.log',
      cron_restart: '0 0 * * *', // once per day
      interpreter: undefined,
      env: {
        PYTHONPATH: 'src/',
        MONITORING_INITIATOR: 'wb_scraper_api',
      },
    },

    // wb_scraper
    {
      ...defaults,
      name: 'wb_scraper', // scraps wb for stats
      script: 'venv/bin/python3 src/wb_scraper/main.py search_word 0 20000',
      log_file: 'logs/pm2/wb_scraper.log',
      cron_restart: '0 0 * * *', // once per day
      interpreter : undefined,
      env: {
        PYTHONPATH: 'src/',
        MONITORING_INITIATOR: 'wb_scraper',
      },
    },
    
  ]
}