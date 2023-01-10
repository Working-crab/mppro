'use strict';

module.exports = {
  apps: [{
      name: 'mpProUITest',
      script: '/data/src/ui_backend/main.py',
      args: [''],
      wait_ready: true,
      autorestart: false,
      max_restarts: 5,
      interpreter : '/data/venv/bin/python',
      // interpreter_args: '-m ui_backend.main',
      cwd: '/data/',
      env: {
        PYTHONPATH: '/data/'
      }
  }
]
}