#!/bin/bash
set -e

APP_DIR="/var/www/analiyx"
BRANCH="${1:-main}"

echo "================================"
echo "  Analiyx Deploy Script"
echo "  Branch: $BRANCH"
echo "================================"

cd "$APP_DIR"

echo ""
echo ">>> Pulling latest from $BRANCH..."
git pull origin "$BRANCH"

echo ""
echo ">>> Updating backend dependencies..."
cd "$APP_DIR/backend"
source venv/bin/activate
pip install -r requirements.txt --quiet

echo ""
echo ">>> Restarting backend..."
pm2 restart analiyx-backend

echo ""
echo ">>> Installing frontend dependencies..."
cd "$APP_DIR/frontend"
yarn install --frozen-lockfile 2>/dev/null || yarn install

echo ""
echo ">>> Building frontend..."
yarn build

echo ""
echo ">>> Reloading nginx..."
sudo nginx -t && sudo systemctl reload nginx

echo ""
echo "================================"
echo "  Deploy complete!"
echo "  Check: pm2 status"
echo "================================"
