#!/bin/bash

# Copyright 2017 Lucas Jo (Atlas Guide)
# Apache 2.0

if [ $# -ne "1" ]; then
	echo "Usage: $0 <download_dir>"
	echo "e.g.: $0 data/local/lm"
	exit 1
fi

dst_dir=$1
bucketname="zeroth-opensource"

if [ ! -d $dst_dir ]; then
    mkdir -p $dst_dir
fi
echo "Check LMs files"
LMList="\
	zeroth.lm.fg.arpa.gz \
	zeroth.lm.tg.arpa.gz \
	zeroth.lm.tgmed.arpa.gz \
	zeroth.lm.tgsmall.arpa.gz \
	zeroth_lexicon \
	zeroth_morfessor.seg"

for file in $LMList; do
	if [ -f $dst_dir/$file ]; then
		echo $file already exist
	else
		echo "Download "$file
		aws s3 cp s3://$bucketname/$file $dst_dir
	fi 
done
echo "all the files (lexicon, LM, segment model) are ready"

#echo "Need to  build lexicon and LM, clone from zeroth project"
#if [ ! -d $dst_dir ]; then
#	git clone https://github.com/goodatlas/zeroth.git $dst_dir
#fi
#echo "Start to build"
#$dst_dir/run.sh

