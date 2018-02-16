#!/bin/bash
lambda=0.2
use_best=true
# LM pruning threshold for the 'small' trigram model
prune_thresh_small=0.0000003
# LM pruning threshold for the 'medium' trigram model
prune_thresh_medium=0.0000001

echo "$0 $@" # print cmd line
. ./parse_options.sh

lambda_tg=$lambda
lambda_fg=$lambda
echo 'use_best: '$use_best
echo 'lamda: '$lambda 
echo 'lamda 3-gram: '$lambda_tg 
echo 'lamda 4-gram: '$lambda_fg

echo 'Build a 3-gram mixed-LM ---------------------'
general_domain_lm=corpus.lm.tg.arpa.gz
task_domain_lm=corpus_task.lm.tg.arpa.gz
test_corpus=corpus_task.test
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
mixed_lm_tg=mixed_$lambda.lm.tg.arpa.gz
ngram -lm $general_domain_lm -mix-lm $task_domain_lm -lambda $lambda -write-lm $mixed_lm_tg

echo 'Build a 4-gram mixed-LM ---------------------'
general_domain_lm=corpus.lm.fg.arpa.gz
task_domain_lm=corpus_task.lm.fg.arpa.gz
test_corpus=corpus_task.test
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
mixed_lm_fg=mixed_$lambda.lm.fg.arpa.gz
ngram -lm $general_domain_lm -mix-lm $task_domain_lm -lambda $lambda -write-lm $mixed_lm_fg

echo 'Generate pruned 3-gram mixed-LM ----------------------------------------'
ngram -prune $prune_thresh_small -lm $mixed_lm_tg -write-lm mixed_$lambda_tg.lm.tgsmall.arpa.gz
echo '  3-gram small: ' $(du -h mixed_$lambda_tg.lm.tgsmall.arpa.gz)

ngram -prune $prune_thresh_medium -lm $mixed_lm_tg -write-lm mixed_$lambda_tg.lm.tgmed.arpa.gz
echo '  3-gram medium: ' $(du -h mixed_$lambda_tg.lm.tgmed.arpa.gz)
