#!/bin/bash

# Copyright 2017 Lucas Jo (Atlas Guide)
# Apache 2.0

if [ $# -ne "2" ]; then
	echo "Usage: $0 <download_dir> <part_name>"
	echo "e.g.: $0 ./speechDATA recData01"
	exit 1
fi

exists(){
	command -v "$1" >/dev/null 2>&1
}

# check AWS Cli 
if ! exists aws; then
	echo "Please, install AWS Cli (Command-line interface) and configure it"
	echo "  > pip install awscli"
	echo "  > aws configure"
	exit 1
fi

data=$1

AUDIOINFO='AUDIO_INFO'
AUDIOLIST=$2
bucketname="zeroth-opensource"
# download audio info file
if [ ! -f $data/$AUDIOINFO ]; then
    aws s3 cp s3://$bucketname/$AUDIOINFO $data/$AUDIOINFO
    success=$(echo $?)
    if [ $success -ne 0 ]; then
        echo "Download from AWS is failed, check your credential and configure your aws CLI"
        exit 1
    fi
fi

# download Audio
echo "Now download Audio ----------------------------------------------------"
for file in $AUDIOLIST
do
	echo "check if $file.tar.gz exist or not"
	if [ ! -f $data/$file.tar.gz ]; then
		aws s3 cp s3://$bucketname/$file.tar.gz $data/$file.tar.gz
	else
		echo "  $data/$file.tar.gz already exist"
	fi
done

echo "Now extract Audio ----------------------------------------------------"
for file in $AUDIOLIST
do
	if [ -f $data/$file/.complete ]; then
		echo "  alreay extracted"
		continue
	else
		tar -zxvf $data/$file.tar.gz -C $data
		touch $data/$file/.complete
	fi
done
