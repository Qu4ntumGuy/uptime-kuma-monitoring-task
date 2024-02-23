#!/bin/bash/

sudo apt install python3 -y

sudo apt install python3-pip -y

pip install uptime-kuma-api
pip install python-dotenv

python3 add_monitor.py
