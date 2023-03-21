'use strict';

const defaults = {
  name: 'SET ME UP',
  script: 'SET ME UP',
  wait_ready: true, 
  autorestart: false,
  kill_timeout: 10000,
  instances : 1,
  max_restarts: 0,
  interpreter : '/data/venv/bin/python',
  log_file: '/data/logs/pm2/default.log',
  cwd: '/data/',
  env: {
    PYTHONPATH: '/data/src/'
  }
}

module.exports = {
  apps: [
    {
      ...defaults,
      autorestart: true,
      name: 'mp_pro_ui_telega_1',
      script: '/data/venv/bin/python -m uvicorn ui_backend.main:app --reload',
      log_file: '/data/logs/pm2/mp_pro_ui_telega_1.log',
      interpreter: undefined,
    },
    {
      ...defaults,
      autorestart: true,
      name: 'mp_pro_ui_telega_2',
      script: '/data/venv/bin/python -m uvicorn ui_backend.main:app --reload',
      log_file: '/data/logs/pm2/mp_pro_ui_telega_2.log',
      interpreter: undefined,
    },
    {
      ...defaults,
      name: 'bot_message_sender',
      script: '/data/src/ui_backend/bot_message_sender/bot_message_sender.py',
      log_file: '/data/logs/pm2/bot_message_sender.log',
    },
    {
      ...defaults,
      name: 'wb_routines', // setups wb categories to caches daily
      script: '/data/src/wb_routines/main.py',
      log_file: '/data/logs/pm2/wb_routines.log',
      cron_restart: '0 0 * * *', // once per day
    },
    {
      ...defaults,
      name: 'mp_pro_user_automation',
      script: '/data/src/user_automation/main.py',
      log_file: '/data/logs/pm2/user_automation.log',
      cron_restart: '*/10 * * * *', // once per 10 minutes
    },
    {
      ...defaults,
      name: 'mq_campaign_info_consumer',
      script: '/data/src/ui_backend/campaign_info/mq_campaign_info_consumer.py',
      log_file: '/data/logs/pm2/campaign_info_consumer.log',
    },

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
