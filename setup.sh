#!/bin/bash
echo "=== shirA Kitchen Bot Setup ==="
cd /root
if [ -d "shira-miniapp" ]; then
  cd shira-miniapp && git pull
else
  git clone https://github.com/mmo-rgb/mini-app.git shira-miniapp && cd shira-miniapp
fi
pip install aiogram --break-system-packages -q
pm2 delete shira-bot 2>/dev/null
pm2 start bot.py --name shira-bot --interpreter python3
pm2 save
echo "=== Done! Bot is running ==="
pm2 status
