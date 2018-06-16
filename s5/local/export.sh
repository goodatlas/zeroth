#!/bin/bash

# Copyright  2017  Atlas Guide (Author : Lucas Jo)
# Apache 2.0

if [ $# -ne 1 ]; then
	echo "Usage: $0 <export-dir>"
	echo " , where <export-dir> is the directory in which the whole nnet3 component is stored"
	echo "   it can be used as a model for kaldi gstreamer server"
	exit 1
fi

final_graph_dir=/home/ubuntu/_prjs_/zeroth/s5/exp/chain_rvb/tree_a/graph_tgsmall
final_model_dir=/home/ubuntu/_prjs_/zeroth/s5/exp/chain_rvb/tdnn1n_rvb_online
small_lm=/home/ubuntu/_prjs_/zeroth/s5/data/lang_test_tgsmall/G.fst
large_lm=/home/ubuntu/_prjs_/zeroth/s5/data/lang_test_fglarge/G.carpa

dir=$1/test/models/korean/zeroth
mkdir -p $dir

# HCLG / words.txt / final.mdl
cp -rpf $final_graph_dir/HCLG.fst $dir
cp -rpf $final_graph_dir/words.txt $dir
cp -rpf $final_graph_dir/phones.txt $dir
cp -rpf $final_graph_dir/phones/word_boundary.int $dir

cp -rpf $final_model_dir/final.mdl $dir
cp -rpf $final_model_dir/frame_subsampling_factor $dir

# copy LMs: small (G.fst) large (G.carpa)
cp -rpf $small_lm $dir
cp -rpf $large_lm $dir

# copy configuration files
cp -rpf $final_model_dir/ivector_extractor/ $dir
cp -rpf $final_model_dir/conf/ $dir

# replace path info
var="$final_model_dir""/"
var=$(echo "$var" | sed 's/\//\\\//g')
replace="test/models/korean/zeroth/"
replace=$(echo "$replace" | sed 's/\//\\\//g')
sed -i "s/$var/$replace/g" $dir/conf/ivector_extractor.conf
sed -i "s/$var/$replace/g" $dir/conf/online.conf

#cp -rpf local/zeroth_korean_tdnn_lstm.yaml $1
