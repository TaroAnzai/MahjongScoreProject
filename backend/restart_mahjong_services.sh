#!/bin/bash
# ============================================
# Mahjong Backend / Celery Services Restart Script
# ============================================

# サービス名を配列で定義
SERVICES=(
  "mahjong_backend"
  "celery-worker-mahjong"
  "celery-beat-mahjong"
)

echo "🔄 Restarting Mahjong services..."

# 各サービスを順に再起動
for SERVICE in "${SERVICES[@]}"; do
  echo "--------------------------------------------"
  echo "Restarting: $SERVICE"
  sudo systemctl daemon-reload
  sudo systemctl restart "$SERVICE"
  STATUS=$?
  if [ $STATUS -eq 0 ]; then
    echo "✅ $SERVICE restarted successfully."
  else
    echo "❌ Failed to restart $SERVICE."
  fi
done

echo "--------------------------------------------"
echo "✅ All Mahjong-related services have been restarted."
echo "Checking status..."
echo ""

# ステータス表示
for SERVICE in "${SERVICES[@]}"; do
  sudo systemctl status "$SERVICE" --no-pager -l | grep -E "Active:|Loaded:"
done
