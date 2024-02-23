#!/bin/bash/
git clone https://github.com/jackbalageru/MERN-CRUD.git
cd MERN-CRUD/client
sudo apt update
sudo apt install npm -y
sudo npm install
sudo npm install -g pm2
pm2 start npm --name client -- start
cd
sudo apt install nginx -y
sudo systemctl start nginx

file_path="/etc/nginx/sites-enabled/default"
add_line="proxy_pass http://localhost:3000;"
find_line='try_files $uri $uri/ =404;'

if grep -qF "$find_line" "$file_path"; then
    sed -i "s|$find_line|$add_line|g" "$file_path"
    echo "Line replaced successfully." >> ~/errors.txt
    sudo systemctl restart nginx
else
    echo "Error: The specified line was not found in the Nginx configuration file." >> ~/errors.txt
fi
pm2 save
