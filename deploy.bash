#!/bin/bash


docker compose -f docker-compose.yml up -d && \
source venv/bin/activate && \
pip install -r python_requirements.txt && \
alembic upgrade head && \
pm2 kill && \
pm2 start pm2.config.js
