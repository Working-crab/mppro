
Requirements:
Python 3.8.10
Docker version 20.10.22, build 3a2c30b
Node 16.19.0
npm 9.2.0
pm2 5.2.2

# admp.pro
## Settings Up on local machine

1. clone git repository
2. setting up **docker-compose**
    - if this **not** **needed** - **skip** to 5 point. 
    - else copy file docker-compose.yml and rename for example to docker-compose-local.yml
3. You can change: 
    - Port, rename container_name and etc.
4. start docker-compose-local.yml: 
```bash
docker-compose -f (relative path to docker-compose-local.yml) up -d
```
5. start docker-compose.yml: 
```bash
docker-composer up -d
```
6. download python 3.8.10, create virtualenv by command: 
```bash
python3 -m virtualenv -p python3.8.10 venv
```
7. install python req: 
```bash
pip install -r python_requirements.txt
```
8. install Node, for example with help brew: 
```bash
brew install Node@16.19.0
```
9. install pm2: 
```bash
npm install pm2@5.2.2 -g
```
10. install ngrok for example with help brew: 
```bash
brew install ngrok
```
11. start ngrok server: 
```bash
ngrok http 8000
```
12. change pm2.config.js to this a more working version:

```js
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
    PYTHONPATH: 'src/'
  }
}

module.exports = {
  apps: [
    {
      ...defaults,
      autorestart: true,
      name: 'mp_pro_ui_telega_1',
      script: 'venv/bin/python3 -m uvicorn ui_backend.main:app --reload',
      log_file: 'logs/pm2/mp_pro_ui_telega_1.log',
      interpreter: undefined,
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
      script: 'venv/bin/python3 src/ui_backend/bot_message_sender/bot_message_sender.py',
      log_file: 'logs/pm2/bot_message_sender.log',
    },
    {
      ...defaults,
      name: 'wb_routines', // setups wb categories to caches daily
      script: 'src/wb_routines/main.py',
      log_file: 'logs/pm2/wb_routines.log',
      cron_restart: '0 0 * * *', // once per day
    },
    {
      ...defaults,
      name: 'mp_pro_user_automation',
      script: 'src/user_automation/main.py',
      log_file: 'logs/pm2/user_automation.log',
      cron_restart: '*/10 * * * *', // once per 10 minutes
    },
    {
      ...defaults,
      name: 'mq_campaign_info_consumer',
      script: 'src/ui_backend/mq_campaign_info.py',
      log_file: 'logs/pm2/campaign_info_consumer.log',
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
```
13. change in src/common/appLogger 
```
handler = logging.FileHandler(f'/data/logs/{name}.log')
```
to
```
handler = logging.FileHandler(f'logs/{name}.log')*  
```
14. Create config file in src/ui_backend, by template(config_template) and rename to **config_local.py**
15. After all of this, start pm2: 
```bash
pm2 start pm2.config.js
```
16. you can work :)
