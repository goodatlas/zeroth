#!/bin/bash
# 
# This code split a data set into two set with ratio
#
# Copyright  2017  Atlas Guide (Author : Lucas Jo)
#
# Apache 2.0

ratio=10

echo "$0 $@"  # Print the command line for logging

. parse_options.sh || exit 1;

if [ $# != 3 ]; then
	echo "Usage: $0 [options] <src-dir> <tar-dir-1> <tar-dir-2>"
	echo "E.g: $0 data/dev data/dev_train data/dev_test"
	echo "  --ratio <N>						# 1/N for tar-dir-2"
	exit 1
fi

src_dir=$1
tar_dir_1=$2
tar_dir_2=$3
name=$(basename $src_dir)

echo $src_dir $tar_dir_1 $tar_dir_2 $name

# $src_dir/split$ratio will be generated
utils/split_data.sh --per-utt $src_dir $ratio

utils/copy_data_dir.sh $src_dir/split${ratio}utt/1 $tar_dir_2
dirs=
for i in $(seq 2 $ratio); do
	dirs+=" $src_dir/split${ratio}utt/$i"
done

utils/combine_data.sh $tar_dir_1 $dirs

rm -rf $src_dir/split${ratio}utt
