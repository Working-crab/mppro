'use strict';

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
      script: 'venv/bin/python3 -m uvicorn ui_backend.main:app --reload',
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
      cron_restart: '*/10 * * * *', // once per 10 minutes
      env: {
        PYTHONPATH: 'src/',
        MONITORING_INITIATOR: 'user_automation',
      },
    },
    // { TODO: Refactor
    //   ...defaults,
    //   name: 'mq_campaign_info_consumer',
    //   script: 'src/ui_backend/mq_campaign_info.py',
    //   log_file: 'logs/pm2/campaign_info_consumer.log',
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