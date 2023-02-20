'use strict';

module.exports = {
  apps: [
    {
      name: 'mp_pro_ui_telega',
      script: '/data/venv/bin/python -m uvicorn ui_backend.main:app --reload',
      wait_ready: false, 
      autorestart: false,
      kill_timeout: 10000,
      instances : 1,
      max_restarts: 0,
      log_file: "/data/logs/pm2/mp_pro_ui_telega.log",
      // interpreter : '/data/venv/bin/python',
      cwd: '/data/',
      env: {
        PYTHONPATH: '/data/src/'
      }
    },
    {
      name: 'bot_message_sender',
      script: '/data/src/ui_backend/bot_message_sender/bot_message_sender.py',
      wait_ready: false, 
      autorestart: false,
      kill_timeout: 10000,
      instances : 1,
      max_restarts: 0,
      log_file: "/data/logs/pm2/bot_message_sender.log",
      interpreter : '/data/venv/bin/python',
      cwd: '/data/',
      env: {
        PYTHONPATH: '/data/src/'
      }
    },
    // {
    //   name: 'mp_pro_user_automation',
    //   script: '/data/src/user_automation/main.py',
    //   args: [''],
    //   wait_ready: true,
    //   autorestart: false,
    //   cron_restart: '*/10 * * * *', // once per 10 minutes
    //   log_file: "/data/logs/pm2/user_automation.log",
    //   interpreter : '/data/venv/bin/python',
    //   cwd: '/data/',
    //   env: {
    //     PYTHONPATH: '/data/src/'
    //   }
    // },
    // {
    //   name: 'mp_pro_web_test',
    //   script: '/data/src/web_test_frontend/index.js',
    //   args: [''],
    //   wait_ready: true,
    //   autorestart: true,
    //   max_restarts: 0,
    //   instances : 2,
    //   exec_mode : "cluster",
    //   log_file: "/data/logs/pm2/mp_pro_web_test.log",
    //   cwd: '/data/',
    //   env: {
    //     NODE_ENV: '/data/'
    //   }
    // }
  ]
}