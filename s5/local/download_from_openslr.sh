#!/bin/bash

# Copyright 2018 Lucas Jo (Atlas Guide)
# Apache 2.0

if [ ! -f zeroth_korean.tar.gz ]; then
	echo "1. Download opensource data from openslr"
	wget http://www.openslr.org/resources/40/zeroth_korean.tar.gz
else
	echo " zeroth_korean.tar.gz already exist"
fi

if [ ! -d ./speechDATA ]; then
	echo "2. Untar data"
	mkdir -p ./speechDATA
	tar -zxvf zeroth_korean.tar.gz -C speechDATA
	
	echo "3. put LM fils into daa/local/lm"
	mv speechDATA/zeroth* data/local/lm
fi

exit 0
