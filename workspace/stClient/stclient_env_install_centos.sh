#!/bin/bash

KETI_STCLIENT_HOME=$(dirname $(realpath $0))

STORAGE_HOME=~
cd $STORAGE_HOME 

# backup org repository
bzip2 /etc/yum.repos.d/CentOS-*.repo

# daum repository 
echo '[base]
name=CentOS-$releasever - Base
baseurl=http://ftp.daumkakao.com/centos/$releasever/os/$basearch/
gpgcheck=0 
[updates]
name=CentOS-$releasever - Updates
baseurl=http://ftp.daumkakao.com/centos/$releasever/updates/$basearch/
gpgcheck=0
[extras]
name=CentOS-$releasever - Extraspin
baseurl=http://ftp.daumkakao.com/centos/$releasever/extras/$basearch/
gpgcheck=0' > /etc/yum.repos.d/Daum.repo
yum repolist

sudo yum -y update

rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

sudo yum -y install python-pip

yum install -y gcc

pip install kafka

sudo yum -y install python-devel

sudo yum -y install mysql-devel


pip install mysqlclient
pip install sysv_ipc
sudo pip install pycrypto
sudo pip install bs4
sudo pip install requests
sudo pip install paramiko
sudo pip install PyOpenSSL


mkdir /root/backuproot

cp /root/Storage/V\&V/test/compress_testfile/* /root/backuproot/

sudo yum -y install wget


yum -y install http://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm

yum -y install mysql-community-server


systemctl stop mysqld

systemctl set-environment MYSQLD_OPTS="--skip-grant-tables"

systemctl start mysqld

mysql -u root <<EOF

UPDATE mysql.user SET authentication_string = PASSWORD('ketilinux') WHERE User = 'root' AND Host = 'localhost';

FLUSH PRIVILEGES;

quit

EOF

systemctl stop mysqld

systemctl unset-environment MYSQLD_OPTS

systemctl start mysqld



mysql --connect-expired-password  -uroot -pketilinux mysql -e  "SET GLOBAL validate_password_policy=LOW;"
mysql --connect-expired-password  -uroot -pketilinux mysql -e  "ALTER USER 'root'@'localhost' IDENTIFIED BY 'ketilinux';"



echo "character-set-server=utf8" >> /etc/my.cnf
echo "collation-server=utf8_general_ci" >> /etc/my.cnf
echo "init_connect=SET collation_connection = utf8_general_ci" >> /etc/my.cnf
echo "init_connect=SET NAMES utf8" >> /etc/my.cnf

echo "character-set-client-handshake = FALSE" >> /etc/my.cnf
echo "skip-character-set-client-handshake" >> /etc/my.cnf


echo "[client]" >> /etc/my.cnf
echo "default-character-set = utf8" >> /etc/my.cnf

echo "[mysqldump]" >> /etc/my.cnf
echo "default-character-set = utf8" >> /etc/my.cnf

echo "[mysql]" >> /etc/my.cnf
echo "default-character-set = utf8" >> /etc/my.cnf


systemctl restart mysqld


mysql -u root -pketilinux -e "create database storage"
mysql -u root -pketilinux -D storage -e "create table fileinfo ( path char(255) character set utf8 collate utf8_general_ci, name char(100) character set utf8 collate utf8_general_ci, type char(1), size char(30), mtime char(30), cb_offset_list text, cb_sha_list text, cb_type_list text, PRIMARY KEY(path, name ) )"
mysql -u root -pketilinux -D storage -e "create table precheck ( path char(255) character set utf8 collate utf8_general_ci, name char(100) character set utf8 collate utf8_general_ci, mtime char(30), cb_offset_list text, cb_sha_list text, cb_type_list text, isLZ4 longtext, confPartionSize int, confMaxBlockNum int, confCompRatio float, PRIMARY KEY(path, name ) )"


#echo "export KETI_STCLIENT_HOME="$KETI_STCLIENT_HOME >> ~/.bashrc
echo "export KETI_STCLIENT_HOME=/root/Storage/VV/stClient" >> ~/.bashrc
echo "PATH="'$PATH'":"'$KETI_STCLIENT_HOME'"/dist">> ~/.bashrc
echo "export PATH" >> ~/.bashrc
source ~/.bashrc
