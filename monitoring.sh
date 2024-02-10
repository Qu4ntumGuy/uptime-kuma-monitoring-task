#!/bin/bash
echo ""
echo ""
echo "---------------------------::  AUTHOR  ::------------------------------"
echo "-----------------------------------------------------------------------"
echo "-------#####-----------------------------------------------------------"
echo "-----##     ##----####----##   ##--######-----####---##       ##-------"
echo "-----##        --##  ##---##   ##--##   ##---##  ##--##       ##-------"
echo "-----##    ###--##    ##--##   ##--##   ##--##    ##--##     ##--------"
echo "-----##     ##--########--##   ##--#####----########---##   ##---------"
echo "-----##     ##--##    ##--##   ##--##  ##---##    ##----## ##----------"
echo "-------#####----##    ##--#######--##   ##--##    ##-----##------------"
echo "-----------------------------------------------------------------------"
echo "-----------------------------------------------------------------------"
echo ""
echo ""
#echo "Updating..."
#sudo apt update
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
git clone https://github.com/louislam/uptime-kuma.git
echo "Providing Permissions"
sudo chown -R $USER:$USER uptime-kuma/
sleep 5
cd uptime-kuma/
echo "setting up the app"
npm run setup
sleep 20
#node server/server.js
npm install pm2 -g
pm2 start server/server.js --name uptime-kuma
pm2 save
echo "ending"

