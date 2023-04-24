
Requirements:
Python 3.8.10
Docker version 20.10.22, build 3a2c30b
Node 16.19.0
npm 9.2.0
pm2 5.2.2

# admp.pro
## Setting Up on local machine

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
docker-compose up -d
```

5. migrate db: 
```bash
???
```

&emsp;&emsp;6.1 if use ubuntu. Install "libffi-dev"
```bash
sudo apt-get install libffi-dev
```

&emsp;&emsp;6.2 you need install python 3.8.10.
```bash
curl https://pyenv.run | bash
```


&emsp;&emsp;6.3 insert this in end ~/.bashrc and reload bash
```bash
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```


&emsp;&emsp;6.4 use
```bash
pyenv install 3.8.10
```


&emsp;&emsp;6.5 cd in project dir and use
```bash
pyenv local 3.8.10
```


&emsp;&emsp;6.6 in project dir use 
```bash
python3 -m pip install virtualenv
```


&emsp;&emsp;6.7 in project dir use
```bash
python3 -m virtualenv -p python3.8.10 venv
```


&emsp;&emsp;6.8 activate venv
```bash
source venv/bin/activate
```


&emsp;&emsp;6.9 update pip
```bash
python3 -m pip install --upgrade pip
```


7. install python req: 
```bash
pip install -r python_requirements.txt
```
8. install Node, for example with help brew:
macOS
```bash
brew install Node@16.19.0
```
9. install pm2: 
```bash
npm install pm2@5.2.2 -g
```
10. install ngrok for example with help brew: 
```bash
macOS
brew install ngrok
```
11. start ngrok server: 
```bash
ngrok http 8000
```
12. create from "pm2.config.js" your pm2_local.config.js:


13. Create config file in src/ui_backend, from template(config_template) and rename to **config_local.py**
    - WEB_HOOK_URL get from ngrok
    - TOKEN get from BotFather in telegram
14. After all of this, start pm2: 
```bash
pm2 start pm2_local.config.js
```
15. you can work :)

&emsp; You can use debug with VS code(example config in ${workspaceFolder}/ launch_example.json) 
