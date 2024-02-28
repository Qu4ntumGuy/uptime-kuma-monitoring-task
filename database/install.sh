sudo apt update
sudo apt install mysql-server -y
sudo systemctl start mysql.service

ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root@123';
exit

MYSQL_USER="root"
MYSQL_PASSWORD="root@123"
MYSQL_HOST="localhost"

mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -h"$MYSQL_HOST" -e "CREATE DATABASE IF NOT EXISTS websites;"

# Create a database
mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -h"$MYSQL_HOST" -e "CREATE DATABASE IF NOT EXISTS websites;"
mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -h"$MYSQL_HOST"  -e "CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'root@123';"
mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -h"$MYSQL_HOST"  -e "GRANT ALL PRIVILEGES ON websites.* TO 'admin'@'%';"
mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -h"$MYSQL_HOST"  -e "FLUSH PRIVILEGES;"
mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -h"$MYSQL_HOST"  -e "exit"
#mysql -u root -e "USE mern_crud; CREATE TABLE IF NOT EXISTS employees (id int(11) NOT NULL AUTO_INCREMENT, name varchar(50) NOT NULL, email varchar(50) NOT NULL, phone varchar(15) NOT NULL, PRIMARY KEY (id));"

