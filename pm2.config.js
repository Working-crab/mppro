'use strict';

module.exports = {
  apps: [
    {
      name: 'mpProUITest',
      script: '/data/src/ui_backend/main.py',
      args: [''],
      wait_ready: true,
      autorestart: true,
      max_restarts: 0,
      interpreter : '/data/venv/bin/python',
      // interpreter_args: '-m ui_backend.main',
      cwd: '/data/',
      env: {
        PYTHONPATH: '/data/'
      }
    },
    {
      name: 'mpProWebTest',
      script: '/data/src/web_test_frontend/index.js',
      args: [''],
      wait_ready: true,
      autorestart: true,
      max_restarts: 0,
      cwd: '/data/',
      env: {
        NODE_ENV: '/data/'
      }
    }
  ]
}