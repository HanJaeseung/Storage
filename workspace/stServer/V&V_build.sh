#!/bin/bash
SRC_HOME=/root/storage/combine/workspace/stServer

TARGET_HOME=/root/storage/combine/target/stServer/Storage/VV/stServer

rm -rf $TARGET_HOME

mkdir -p $TARGET_HOME

rm -rf build/*
rm -rf dist && rm -rf $TARGET_HOME/dist
rm -rf cert/ && rm -rf $TARGET_HOME/cert
rm -rf lib/* && rm -rf $TARGET_HOME/lib/*

mkdir -p $TARGET_HOME/lib/lz4
mkdir -p $TARGET_HOME/conf
mkdir -p $TARGET_HOME/dist
mkdir -p $TARGET_HOME/log
mkdir -p $TARGET_HOME/cert

pyinstaller -F pysrc/consumer.py pysrc/keyManageServer.py
rm -rf *.spec

cd lz4/lib
source /opt/intel/compilers_and_libraries_2018/linux/ipp/bin/ippvars.sh intel64
IPPROOT=/opt/intel/compilers_and_libraries_2018/linux/ipp
export CFLAGS="-O3 -DWITH_IPP -I$IPPROOT/include"

make clean
make WITH_IPP=yes
mkdir -p $SRC_HOME/build/lz4

cp liblz4.so.1.7.5 $SRC_HOME/build/lz4
cd ../..

cp -r build/lz4 lib

cp stserver_env_install_centos.sh $TARGET_HOME

cp -r lib/* $TARGET_HOME/lib
cp -r conf/target_server_configure $TARGET_HOME/conf/server_configure
cp -r dist/* $TARGET_HOME/dist
cp -r cert/ $TARGET_HOME/cert
