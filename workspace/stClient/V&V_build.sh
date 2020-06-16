#!/bin/bash

SRC_HOME=/root/storage/combine/workspace/stClient
TARGET_HOME=/root/storage/combine/target/stClient/Storage/VV/stClient

SRC_AUTO_BENCH_HOME=/root/storage/auto_bench

TARGET_VV_HOME=/root/storage/combine/target/stClient/Storage/VV

rm -rf $TARGET_VV_HOME/*
mkdir -p $TARGET_HOME

rm -rf build/*
rm -rf dist/* && rm -rf $TARGET_HOME/dist/*
rm -rf cert/* && rm -rf $TARGET_HOME/cert/*
rm -rf lib/* && rm -rf $TARGET_HOME/lib/*
rm -rf $TARGET_AUTO_BENCH_HOME/auto_bench


mkdir -p $TARGET_HOME/log
#mkdir -p $TARGET_HOME/example/c
mkdir -p $TARGET_HOME/libCheck/c
#mkdir -p $TARGET_HOME/example/python
mkdir -p $TARGET_HOME/libCheck/python
mkdir -p $TARGET_HOME/lib
mkdir -p $TARGET_HOME/conf
mkdir -p $TARGET_HOME/dist
mkdir -p $TARGET_HOME/cert
mkdir -p $TARGET_VV_HOME/auto_bench/optimize
mkdir -p $TARGET_VV_HOME/auto_bench/baseline

python setup.py build

rm -rf pysrc/*.c
rm -rf pysrc/*.pyc

pyinstaller -F pysrc/treeServer.py pysrc/tree.py  pysrc/precheck.py pysrc/anchor_block.py pysrc/block.py
pyinstaller -F pysrc/prechecker.py pysrc/precheck.py pysrc/anchor_block.py pysrc/block.py pysrc/lz4aes.py
pyinstaller -F pysrc/stcli.py pysrc/producer.py pysrc/AESCipher.py pysrc/keyManageClient.py pysrc/tree.py pysrc/anchor_block.py pysrc/block.py pysrc/precheck.py pysrc/lz4aes.py

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


#cd example/c
cd libCheck/c
make clean && make

#cp libkms.so $TARGET_HOME/example/c
#cp main $TARGET_HOME/example/c
#cp main.c $TARGET_HOME/example/c
#cp kms.h $TARGET_HOME/example/c
#cp Makefile2 $TARGET_HOME/example/c/Makefile

cp libkms.so $TARGET_HOME/libCheck/c
#cp main $TARGET_HOME/libCheck/c
cp main.c $TARGET_HOME/libCheck/c
cp kms.h $TARGET_HOME/libCheck/c
cp Makefile $TARGET_HOME/libCheck/c/Makefile


cd ../..

#cp example/python/example_stcli.py $TARGET_HOME/example/python
cp libCheck/python/example_stcli.py $TARGET_HOME/libCheck/python
cp stclient_env_install_centos.sh $TARGET_HOME


cp build/lib.linux-x86_64-2.7/* lib/
cp -r build/lz4 lib

cp -r lib/* $TARGET_HOME/lib
cp -r conf/target_client_configure $TARGET_HOME/conf/client_configure
cp -r dist/* $TARGET_HOME/dist
#cp -r cert/ $TARGET_HOME/cert

cp install.sh $TARGET_HOME

pyinstaller -F /root/storage/auto_bench/optimize/auto_lz4_optimize_bench.py
pyinstaller -F /root/storage/auto_bench/baseline/auto_lz4_base_bench.py

cp -r V\&V/test $TARGET_VV_HOME
cp -r dist/auto_lz4_optimize_bench $TARGET_VV_HOME/auto_bench/optimize
cp -r $SRC_AUTO_BENCH_HOME/optimize/calc_repeat_avg.sh $TARGET_VV_HOME/auto_bench/optimize
cp -r $SRC_AUTO_BENCH_HOME/optimize/calc_comp_avg.sh $TARGET_VV_HOME/auto_bench/optimize

cp -r $SRC_AUTO_BENCH_HOME/lz4 $TARGET_VV_HOME/auto_bench/

cp -r dist/auto_lz4_base_bench $TARGET_VV_HOME/auto_bench/baseline


