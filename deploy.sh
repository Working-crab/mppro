#!/bin/bash

source_dir="/data/"

docker compose -f /data/docker-compose.yml up -d && \
cd $source_dir && \
git fetch && git pull && \
pip install -r python_requirements.txt && \
pm2 start pm2.config.js
