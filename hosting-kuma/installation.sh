#!/bin/bash

echo "-----------------------New Execution from date ----------------------">> ~/errors.txt

echo "Checking Permission privileges" >> ~/errors.txt

if [[ $EUID -ne 0 ]]; then
  echo "Permission Denied. Try"
  echo "sudo bash monitoring.sh"
  exit 1
fi

echo "Checking for port availability" >> ~/errors.txt

if lsof -i :3001 >> ~/errors.txt 2>&1; then
 echo "Port is already in use."
 echo "Either Uptime-Kuma is running or another website has occupied the port"
 exit 1
fi

sudo apt update
sudo apt install curl -y

#echo "Installing the latest Node.js version..." >> ~/errors.txt

echo "Installing Dependencies like nvm, npm and node......." >> ~/errors.txt

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
. ~/.nvm/nvm.sh
nvm install 20
nvm use 20
npm install -g npm

if [[ $(find /etc/nginx -name "nginx.conf") ]]; then
    echo "Web Server found" >> ~/errors.txt
else
    sudo apt install nginx -y
fi


echo "Updating Node to latest" >> ~/errors.txt
nvm install 20
nvm use 20

node_version=$(node -v)
npm_version=$(npm -v)

echo "Node.js version: $node_version"
echo "npm version: $npm_version"
# Install or update MySQL
echo "Installing or updating MySQL..." >> ~/errors.txt
sudo apt install mysql-server -y

# Change MySQL bind IP to 0.0.0.0
echo "Changing MySQL bind IP to 0.0.0.0..." >> ~/errors.txt
sudo sed -i 's/bind-address\s*=\s*127.0.0.1/bind-address = 0.0.0.0/g' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo systemctl restart mysql

# Create database
sudo mysql -e "CREATE DATABASE kuma;"

# Create websites table in kuma database
echo "Creating websites table..." >> ~/errors.txt
sudo mysql -e "USE kuma; CREATE TABLE websites (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) UNIQUE, url VARCHAR(255), status VARCHAR(255));"
echo "Creating admin user..." >> ~/errors.txt
sudo mysql -e "CREATE USER 'admin'@'%' IDENTIFIED BY 'root@123';"
sudo mysql -e "GRANT SELECT, INSERT, UPDATE ON kuma.websites TO 'admin'@'%';"
sudo mysql -e "FLUSH PRIVILEGES;"

echo ""
echo "----------------Installing Monitoring Tool UPTIME-KUMA----------------"
echo ""
echo "Cloning Uptime-Kuma..." >> ~/errors.txt

if ! git clone https://github.com/louislam/uptime-kuma.git; then
  echo "Error cloning Uptime-Kuma. Please check connectivity and repository URL."
  exit 1
fi

sudo git clone https://github.com/louislam/uptime-kuma.git
echo "Providing Permissions" >> ~/errors.txt
sudo chown -R $USER:$USER uptime-kuma/
cd uptime-kuma/

echo "Setting up the app" >> ~/errors.txt

npm run setup

#node server/server.js

echo "Installing PM2" >> ~/errors.txt

npm install pm2 -g

echo "Setting up pm2 process" >> ~/errors.txt

pm2 start server/server.js --name uptime-kuma

pm2 save

echo "Setting up Server" >> ~/errors.txt

file_path="/etc/nginx/sites-enabled/default"
add_line="proxy_pass http://localhost:3001;"
find_line='try_files $uri $uri/ =404;'

if grep -qF "$find_line" "$file_path"; then
    sed -i "s|$find_line|$add_line|g" "$file_path"
    echo "Line replaced successfully." >> ~/errors.txt
    sudo systemctl restart nginx
else
    echo "Error: The specified line was not found in the Nginx configuration file." >> ~/errors.txt
fi

echo "Uptime-Kuma is installed and running.)."

echo "-------------------------Script Ended-----------------------------" >> ~/errors.txt