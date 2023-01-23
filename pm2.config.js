'use strict';

module.exports = {
  apps: [
    {
      name: 'mp_pro_ui_telega',
      script: '/data/src/ui_backend/main.py',
      args: [''],
      wait_ready: true,
      autorestart: true,
      max_restarts: 0,
      out_file: "/data/logs/mp_pro_ui_telega.log",
      error_file: "/data/logs/mp_pro_ui_telega_error.log",
      interpreter : '/data/venv/bin/python',
      // interpreter_args: '-m ui_backend.main',
      cwd: '/data/',
      env: {
        PYTHONPATH: '/data/src/'
      }
    },
    {
      name: 'mp_pro_user_automation',
      script: '/data/src/user_automation/main.py',
      args: [''],
      wait_ready: true,
      autorestart: false,
      cron_restart: '*/2 * * * *', // once per 2 minutes
      out_file: "/data/logs/user_automation.log",
      error_file: "/data/logs/user_automation_error.log",
      interpreter : '/data/venv/bin/python',
      cwd: '/data/',
      env: {
        PYTHONPATH: '/data/src/'
      }
    },
    {
      name: 'mp_pro_web_test',
      script: '/data/src/web_test_frontend/index.js',
      args: [''],
      wait_ready: true,
      autorestart: true,
      max_restarts: 0,
      instances : 2,
      exec_mode : "cluster",
      out_file: "/data/logs/mp_pro_web_test.log",
      error_file: "/data/logs/mp_pro_web_test_error.log",
      cwd: '/data/',
      env: {
        NODE_ENV: '/data/'
      }
    }
  ]
}