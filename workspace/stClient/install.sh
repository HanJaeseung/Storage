#!/bin/bash
#PYTHON_PATH=/usr/local/lib/python2.7/dist-packages
#PYTHON_PATH=/usr/local/lib/python3.5/dist-packages
PYTHON_PATH=/usr/lib/python2.7/site-packages/

cp -r lib/*.so $PYTHON_PATH
echo "Install Python Library lib/*.so -> "$PYTHON_PATH

