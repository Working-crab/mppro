'use strict';

module.exports = {
  apps: [{
      name: 'mpProUITest',
      script: '/data/leva_popa.py',
      args: [''],
      wait_ready: true,
      autorestart: false,
      max_restarts: 5,
      interpreter : './venv/bin/python',
      // interpreter_args: 'run python3'
  }]
}