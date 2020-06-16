#!/bin/bash
HOST_NAME=`hostname -I`

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

# yum update
sudo yum -y update

rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm


sudo yum -y install gcc
sudo yum -y install python-pip
sudo yum -y install python-devel

pip install kafka
pip install sysv_ipc
sudo pip install pycrypto



sudo yum -y install java-1.8.0-openjdk-devel.x86_64
sudo yum -y install wget

wget https://archive.apache.org/dist/kafka/0.10.2.1/kafka_2.11-0.10.2.1.tgz

tar -xvf kafka_2.11-0.10.2.1.tgz
rm -rf kafka_2.11-0.10.2.1.tgz

echo "replica.fetch.max.bytes=2000000000" >> kafka_2.11-0.10.2.1/config/server.properties
echo "message.max.bytes=2000000000" >> kafka_2.11-0.10.2.1/config/server.properties
echo "max.message.bytes=200000000" >> kafka_2.11-0.10.2.1/config/server.properties
echo "max.request.size=2000000000" >> kafka_2.11-0.10.2.1/config/server.properties
echo "advertised.host.name"=$HOST_NAME >> kafka_2.11-0.10.2.1/config/server.properties



wget https://archive.apache.org/dist/zookeeper/zookeeper-3.4.12/zookeeper-3.4.12.tar.gz
tar -xvf zookeeper-3.4.12.tar.gz
rm -rf zookeeper-3.4.12.tar.gz

cd zookeeper-3.4.12
cp conf/zoo_sample.cfg conf/zoo.cfg
cd $STORAGE_HOME


systemctl stop firewalld
systemctl mask firewalld
yum -y install iptables-services
systemctl enable iptables
iptables -A INPUT -p tcp -m tcp --dport 8888 -j ACCEPT
service iptables save

