'use strict';

module.exports = {
  apps: [
    {
      name: 'mp_pro_ui_test',
      script: '/data/src/ui_backend/main.py',
      args: [''],
      wait_ready: true,
      autorestart: true,
      max_restarts: 0,
      // instances : 2,
      // exec_mode : "cluster",
      out_file: "/data/logs/mp_pro_ui_test.log",
      error_file: "/data/logs/mp_pro_ui_test_error.log",
      interpreter : '/data/venv/bin/python',
      // interpreter_args: '-m ui_backend.main',
      cwd: '/data/',
      env: {
        PYTHONPATH: '/data/'
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