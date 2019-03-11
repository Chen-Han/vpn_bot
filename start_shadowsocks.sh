#!/bin/bash

rm /run/shadowsocks-manager.sock
ssserver -c /app/vpn_bot/ssconfig.json --manager-address /run/shadowsocks-manager.sock

