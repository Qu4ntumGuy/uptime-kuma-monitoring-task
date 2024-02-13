#!/bin/bash

#echo "Updating..."

#sudo apt update
if [[ $EUID -ne 0 ]]; then
  echo "This script requires root privileges. Please run as sudo."
  exit 1
fi

echo "Installing the latest Node.js version..." >> ~/errors.txt
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
. ~/.nvm/nvm.sh
nvm install 20
nvm use 20

echo "Installing Node"
sudo apt install nodejs
echo "Updating Node to latest"
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

