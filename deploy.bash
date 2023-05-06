#!/bin/bash

source_dir="/data/"

docker compose -f /data/docker-compose.yml up -d && \
cd $source_dir && \
git fetch && git pull && \
pip install -r python_requirements.txt && \
alembic upgrade head && \
pm2 kill && \
pm2 start pm2.config.js
