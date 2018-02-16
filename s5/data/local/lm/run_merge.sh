#!/bin/bash
# merge n-gram based Language Models
#
# Copyright  2017  Atlas Guide (Author : Lucas Jo)
# Apache 2.0
# 
lambda=0.2
use_best=true
prune_thresh_small=0.0000003
prune_thresh_medium=0.0000001

. ./cmd.sh
. ./path.sh

echo "$0 $@" # print cmd line

. parse_options.sh || exit 1;

if ! $use_best; then
	lambda_tg=$lambda
	lambda_fg=$lambda
	echo 'lamda: '$lambda 
	echo 'lamda 3-gram: '$lambda_tg 
	echo 'lamda 4-gram: '$lambda_fg
fi


genSrcDir=buildLM/_corpus_
taskSrcDir=buildLM/_corpus_task_
tarDir=buildLM

echo 'Build a 3-gram mixed-LM --------------------------------------'
general_domain_lm=$genSrcDir/corpus.lm.tg.arpa.gz
task_domain_lm=$taskSrcDir/corpus.lm.tg.arpa.gz
test_corpus=$taskSrcDir/corpus.test
if [ "$use_best" = true ]; then
	echo 'find the best mixing weight'
	ngram -lm $general_domain_lm -ppl $test_corpus -debug 2 > $test_corpus.ppl.general_domain
	ngram -lm $task_domain_lm -ppl $test_corpus -debug 2 > $test_corpus.ppl.task_domain
	compute-best-mix $test_corpus.ppl.general_domain $test_corpus.ppl.task_domain > tmp
	lambda=$(cat tmp | grep best | awk '{print substr($6,2)}')
	
	lambda_tg=$lambda
	echo 'lamda 3-gram: '$lambda_tg 
fi
echo mixing LMs with $lambda
mixed_lm_tg=$tarDir/mixed_$lambda.lm.tg.arpa.gz
ngram -lm $general_domain_lm -mix-lm $task_domain_lm -lambda $lambda -write-lm $mixed_lm_tg


echo 'Build a 4-gram mixed-LM --------------------------------------'
general_domain_lm=$genSrcDir/corpus.lm.fg.arpa.gz
task_domain_lm=$taskSrcDir/corpus.lm.fg.arpa.gz
test_corpus=$taskSrcDir/corpus.test
if [ "$use_best" = true ]; then
	echo 'find the best mixing weight'
	ngram -lm $general_domain_lm -ppl $test_corpus -debug 2 > $test_corpus.ppl.general_domain
	ngram -lm $task_domain_lm -ppl $test_corpus -debug 2 > $test_corpus.ppl.task_domain
	compute-best-mix $test_corpus.ppl.general_domain $test_corpus.ppl.task_domain > tmp
	lambda=$(cat tmp | grep best | awk '{print substr($6,2)}')
	
	lambda_fg=$lambda
	echo 'lamda 4-gram: '$lambda_fg 
fi
echo mixing LMs with $lambda
mixed_lm_fg=$tarDir/mixed_$lambda.lm.fg.arpa.gz
ngram -lm $general_domain_lm -mix-lm $task_domain_lm -lambda $lambda -write-lm $mixed_lm_fg

echo 'Generate pruned 3-gram mixed-LM ----------------------------------------'
ngram -prune $prune_thresh_small -lm $mixed_lm_tg -write-lm $tarDir/mixed_$lambda_tg.lm.tgsmall.arpa.gz
echo '  3-gram small: ' $(du -h $tarDir/mixed_$lambda_tg.lm.tgsmall.arpa.gz)

ngram -prune $prune_thresh_medium -lm $mixed_lm_tg -write-lm $tarDir/mixed_$lambda_tg.lm.tgmed.arpa.gz
echo '  3-gram medium: ' $(du -h $tarDir/mixed_$lambda_tg.lm.tgmed.arpa.gz)
