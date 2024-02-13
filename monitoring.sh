#!/bin/bash

#echo "Updating..."

#sudo apt update
if [[ $EUID -ne 0 ]]; then
  echo "Permission Denied. Try"
  echo "sudo bash monitoring.sh"
  exit 1
fi

if lsof -i :3001; then
 echo "Port is already in use."
 echo "Either Uptime-Kuma is running or another website has occupied the port"
 exit 1
fi

nohup sudo apt install curl -y

#echo "Installing the latest Node.js version..." >> ~/errors.txt
echo "Installing Dependencies......."
nohup curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
. ~/.nvm/nvm.sh
nvm install 20
nvm use 20

echo "Installing Node"  >> ~/errors.txt
sudo apt install nodejs
echo "Updating Node to latest" >> ~/errors.txt
nvm install 20
nvm use 20

node_version=$(node -v)
npm_version=$(npm -v)
echo "Node.js version: $node_version"
echo "npm version: $npm_version"
echo ""
echo "----------------Installing Monitoring Tool UPTIME-KUMA----------------"
echo ""
echo "Cloning Uptime-Kuma..." >> ~/errors.txt

if ! git clone https://github.com/louislam/uptime-kuma.git; then
  echo "Error cloning Uptime-Kuma. Please check connectivity and repository URL."
  exit 1
fi

sudo git clone https://github.com/louislam/uptime-kuma.git
echo "Providing Permissions"
sudo chown -R $USER:$USER uptime-kuma/
cd uptime-kuma/

echo "Setting up the app"

npm run setup

#node server/server.js

echo "Installing PM2"

npm install pm2 -g

pm2 start server/server.js --name uptime-kuma

pm2 save

echo "-------------------------Script Ended-----------------------------"

