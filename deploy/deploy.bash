#!/bin/bash

# start from /deploy
cd .. && \
mainWorkDirectory=`pwd` && \

# docker
docker compose -f data/docker-compose.yml up -d && \

# node
cd src/admin_dashboard/frontend/analytics-service && \
npm ci && \
npm run build && \
cd $mainWorkDirectory && \

# python
source venv/bin/activate && \
pip install -r python_requirements.txt && \
alembic upgrade head && \

# other
nginx -t && \
service nginx restart && \

pm2 kill && \
pm2 start deploy/pm2.config.js && \
pm2 save && \

echo "Complete!"
