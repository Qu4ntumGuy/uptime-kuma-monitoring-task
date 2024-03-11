#!/bin/bash/
sudo apt update -y
sudo apt install python3 -y
sudo apt install python3-pip -y
pip install mysql-connector-python
pip install uptime-kuma-api
pip install python-dotenv
pip install psutil

python3 monitoring.py

crontab -e
* * * * * /usr/bin/python3 /home/ubuntu//uptime-kuma-monitoring-task/monitoring-kuma/monitoring.py >> /home/ubuntu/cron.log 2>&1
```
