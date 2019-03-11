#!/bin/bash

. env
ssh $DEV_SERVER <<EOF
cd /app/vpn_bot
git pull origin master
python3 manage.py makemigrations
python3 manage.py migrate
sudo supervisorctl add shadowsocks vpn_bot
sudo supervisorctl restart shadowsocks vpn_bot
EOF
