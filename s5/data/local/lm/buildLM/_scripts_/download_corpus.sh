#!/bin/bash
# Download crawled corpus file from AWS
#
# Copyright  2017  Atlas Guide (Author : Lucas Jo)
#
# Apache 2.0
# 
exists(){
	command -v "$1" >/dev/null 2>&1
}

# check AWS Cli
if ! exists aws; then
    echo "Please, install AWS Cli (Command-line interface)"
    echo "-  sudo pip install awscli"
    exit 1
fi

# Print the command line for logging
#echo "$0 $@"  

# Option parsing
bucketName=acoustic-model-data
. utils/parse_options.sh || exit 1;

# Arguments check
if [ "$#" -ne 2 ]; then
	echo "Usage: $0 <src-corpus-name> <tar-dir>"
	exit 1
fi
srcCorpusName=$1
tardir=$2

if [ ! -d $tardir ]; then
	mkdir -p _corpus_
fi

if [ ! -f $tardir/$srcCorpusName ]; then
	echo "  $tardir/$srcCorpusName not exist, download it from AWS"
	aws s3 cp s3://$bucketName/$srcCorpusName $tardir/.
else
	echo "  $tardir/$srcCorpusName already exist"
fi
