#!/bin/bash
# Build n-gram LM & do the PPL test
#
# Copyright  2017  Atlas Guide (Author : Lucas Jo)
#
# Apache 2.0
# 
exists(){
	command -v "$1" >/dev/null 2>&1
}

. ./cmd.sh
. ./path.sh

prune_thresh_small=0.0000003
prune_thresh_medium=0.0000001
scriptdir=buildLM/_scripts_
cmd=$normalize_cmd

. parse_options.sh || exit 1;

if [ "$#" -ne 1 ]; then
	echo "Usage: $0 <src-dir>"
	exit 1
fi
srcdir=$1

set -e 
date=$(date +'%F-%H-%M')
echo start at $date

vocab=$srcdir/morphemes  # vocab for LM training
nj=$(cat $srcdir/num_jobs)
logdir=$srcdir/log

echo 'Shuffle corpus ---------------------------------------------------------------'
if exists gshuf; then
	cmd_shuf=gshuf
elif exists shuf; then
	cmd_shuf=shuf
else
	echo 'need gshuf or shuf, please install'
	exit 1
fi

echo 'Now split train and test set --------------------------------------------------'
testSetSizeFactor=10 # 1/10
if [ ! -f $srcdir/normedCorpus.seg.1.train ]; then
    for n in $(seq $nj); do
        # the next command does nothing unless _corpus_/storage/ exists, see
        # utils/create_data_link.pl for more info.
        utils/create_data_link.pl $srcdir/normedCorpus.seg.$n.train
        utils/create_data_link.pl $srcdir/normedCorpus.seg.$n.test
    done
    $cmd JOB=1:$nj $logdir/normedCorpus.seg.split.JOB.log \
		$cmd_shuf $srcdir/normedCorpus.seg.JOB \| \
		$scriptdir/splitText -f $srcdir/normedCorpus.seg.JOB -t $testSetSizeFactor - $srcdir/normedCorpus.seg.JOB
fi

echo 'merge train/test corpus ----------------------------------------------------------'
if [ ! -f $srcdir/corpus.train ]; then
	cat $srcdir/normedCorpus.seg.*.train > $srcdir/corpus.train
	cat $srcdir/normedCorpus.seg.*.test > $srcdir/corpus.test
fi

txt=$srcdir/corpus
echo 'Generate LM --------------------------------------------------------------------------'
echo 'Perplexity test: --------------------------------------------------------------'
echo '  text: '$txt', vocab: '$vocab
echo '  Perplexity test 3-gram '
ngram=3
ngram-count -order $ngram -unk -map-unk "<UNK>" -vocab $vocab -text $txt.train -lm $txt.lm.tg.arpa.gz \
	-kndiscount -interpolate
ngram -order 3 -lm $txt.lm.tg.arpa.gz -ppl $txt.test

echo '  Perplexity test 4-gram '
ngram=4
ngram-count -order $ngram -unk -map-unk "<UNK>" -vocab $vocab -text $txt.train -lm $txt.lm.fg.arpa.gz \
	-kndiscount	-interpolate
ngram -order 4 -lm $txt.lm.fg.arpa.gz -ppl $txt.test


echo 'Generate pruned LM --------------------------------------------------------------------------'
ngram -prune $prune_thresh_small -lm $txt.lm.tg.arpa.gz -write-lm $txt.lm.tgsmall.arpa.gz
echo '  3-gram small: ' $(du -h $txt.lm.tgsmall.arpa.gz)

ngram -prune $prune_thresh_medium -lm $txt.lm.tg.arpa.gz -write-lm $txt.lm.tgmed.arpa.gz
echo '  3-gram medium: ' $(du -h $txt.lm.tgmed.arpa.gz)

echo started at $date
date=$(date +'%F-%H-%M')
echo ends at $date
