#!/bin/bash
# this file should be executed using sudo
apt-get install -y python3 python3-pip python-m2crypto sqlite3
pip3 install -r requirements.txt

python3 manage.py makemigrations && python3 manage.py migrate

sed -i 's/libcrypto.EVP_CIPHER_CTX_cleanup/libcrypto.EVP_CIPHER_CTX_reset/g' /usr/local/lib/python3.5/dist-packages/shadowsocks/crypto/openssl.py


