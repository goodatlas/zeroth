#!/bin/bash
#
# Copyright  2017  Atlas Guide (Author : Lucas Jo)
# Apache 2.0
# 
# Build a task-domain Language Model
exists(){
    command -v "$1" >/dev/null 2>&1
}

# check parallel installed
if ! exists parallel; then
    echo "Please, install parallel"
    echo "-  sudo apt-get install parallel"
    exit 1
fi

. ./path.sh
. ./cmd.sh

cmd=$normalize_cmd
srcdir=buildLM/_corpus_task_
scriptdir=buildLM/_scripts_
morfessorUpdate=false

. parse_options.sh || exit 1;

set -e
date=$(date +'%F-%H-%M')
echo start at $date

if [ ! -f zeroth_morfessor.seg ]; then
	echo "file:  zeroth_morfessor.seg is missing"
	echo "Did you download it from AWS temprorary credential? Plz check it"
	exit 1
fi

if [ ! -f $srcdir/morfessor.model.pickled ]; then
	echo "Fetch Morfessor segment model from the official Zeroth project"
	morfessor -l zeroth_morfessor.seg \
		-S morfessor.model.txt \
		-x morfessor.lexicon
	cp zeroth_morfessor.seg morfessor.model.pickled

	ln -s ../../morfessor.model.pickled $srcdir/morfessor.model.pickled
	ln -s ../../morfessor.model.txt $srcdir/morfessor.model.txt
	ln -s ../../morfessor.lexicon $srcdir/morfessor.lexicon
fi

#  split corpus into similar length around 1,000,000 line
echo 'Split corpus --------------------------------------------------------------'
numSplitedfiles=$(find $srcdir ! -name '*.tar.gz*' ! -name '.*' ! -name 'normedCorpus*' -name "*.a*" | wc -l)
if [ $numSplitedfiles -eq 0 ]; then
    find $srcdir ! -name '*.tar.gz*' ! -name '.*' ! -name 'normedCorpus*' ! -name "*.a*" -type f |\
        parallel "split -l 1000000 {} {}'.'"
else
    echo '  It seems like already splited, if not plz remove *.a* files and run again'
fi

splitedfiles=$(find $srcdir ! -name '*.tar.gz*' ! -name '.*' ! -name 'normedCorpus*' -name "*.a*")
job=1
for file in $splitedfiles; do
    if [ -f $srcdir/rawCorpus.$job ]; then
        continue
    fi
    echo "  Copy $file into $srcdir/rawCorpus.$job"
    cp -rpf $file $srcdir/rawCorpus.$job
    echo $job > $srcdir/num_jobs
    job=$(( $job + 1 ))
done

hostInAtlas="ares hephaestus jupiter neptune"
if [[ ! -z $(echo $hostInAtlas | grep -o $(hostname -f)) ]]; then
    echo "Found grid-engine environment ... preparing distributed computation"
    utils/create_split_dir.pl /mnt/{ares,hephaestus,jupiter,neptune}/$USER/lm_data/zeroth/s5/_corpus_task_/storage \
        $srcdir/storage
fi

# Normalization
nj=$(cat $srcdir/num_jobs)
logdir=$srcdir/log
if [ ! -d $logdir ]; then
    mkdir -p $logdir
fi

if [ ! -e $srcdir/normedCorpus.1 ] ; then
	echo 'Text normalization starts ---------------------------------------------------'
    for n in $(seq $nj); do
        # the next command does nothing unless _corpus_task_/storage/ exists, see
        # utils/create_data_link.pl for more info.
        utils/create_data_link.pl $srcdir/normedCorpus.$n
    done
    $cmd JOB=1:$nj $logdir/rawCorpus.JOB.log \
        $scriptdir/normStep1.py $srcdir/rawCorpus.JOB \| \
        $scriptdir/normStep2.py \| \
        $scriptdir/normStep_tmp.py \| \
        $scriptdir/normStep4.py \| \
        $scriptdir/strip.py  \> $srcdir/normedCorpus.JOB || exit 1;
fi

if [ ! -e $srcdir/uniqWords.1 ] ; then
	echo 'Finding Uniq. words for morpheme analysis --------------------------------------'
    for n in $(seq $nj); do
        # the next command does nothing unless _corpus_task_/storage/ exists, see
        # utils/create_data_link.pl for more info.
        utils/create_data_link.pl $srcdir/uniqWords.$n
    done
    $cmd JOB=1:$nj $logdir/normedCorpus.JOB.log \
        cat $srcdir/normedCorpus.JOB \| \
        tr -s \'[:space:]\' \'\\n\' \| sort \| uniq -c \| \
        sort -k1 -n -r \> $srcdir/uniqWords.JOB || exit 1;
fi

if [ ! -f $srcdir/uniqWordList ]; then
	echo "Accumulate statistics into: uniqWordList ------------------------------------------"
    cat $srcdir/uniqWords.* | \
        $scriptdir/sumStatUniqWords.py > $srcdir/uniqWordList
    stat=$(awk 'BEGIN{sum=0;cnt=0}{cnt+=1;if($2 == 1){sum+=1}}END{print sum"/"cnt}' $srcdir/uniqWordList)
    echo "  total uniq. word count: $(echo $stat | awk -F'/' '{print $2}')"
    percentage=$(echo "print('portion of freq.== 1 word: {:.2f} %'.format($stat*100))" | python3)
    echo "  $percentage"
fi

coverage=1.00
srcFile=$srcdir/uniqWordList
inFile=$srcdir/uniqWordList.hangul
inFile2=$srcdir/uniqWordList.nonhangul
outFile=$srcdir/uniqWordList.hangul.pruned
if [ ! -f $inFile ]; then
	echo "Pruning uniqWordList for Morfessor training -----------------------------------------"
    grep -E '[가-힣]+ [0-9]+' $srcFile |\
		awk -v file=$inFile '{if(length($1)<=10 || $2>5){print $0}else{print $0 > file".remained"}}' > $inFile  ##  
	grep -v -E '[가-힣]+ [0-9]+' $srcFile > $inFile2
    
	totalCnt=$(awk 'BEGIN{sum=0}{sum+=$2}END{print sum}' $inFile)
    echo '  pruned coverge:' $coverage
    echo '  total acc. count:' $totalCnt
    awk -v totalCnt="$totalCnt" -v coverage="$coverage" -v file=$outFile \
        'BEGIN{sum=0}{sum+=$2; if(sum/totalCnt <= coverage){print $1}else{print $1 > file".remained"}}' $inFile > $outFile
	echo "  final uniq. word for training: $(wc -l <$outFile)"
fi

if $morfessorUpdate; then
	echo 'Morfessor model training (Update) ----------------------------------------------------'
	rm -f $srcdir/morfessor.* # remove symbolic link

	# CAUTION:
	# if morfessor model is updated,
	# existing morphemes are not valid anymore
    morfessor -l buildLM/_corpus_/morfessor.model.pickled \
		--traindata-list \
        -t $outFile \
        -S $srcdir/morfessor.model.txt \
        -s $srcdir/morfessor.model.pickled \
        -x $srcdir/morfessor.lexicon \
        --randsplit 0.5 --skips \
		--progressbar \
        --nosplit-re '[0-9\[\]\(\){}a-zA-Z&.,\-]+'

fi

# The Morfessor should be installed in the all Grid machines
if [ ! -f $srcdir/normedCorpus.seg.1 ]; then
	echo 'Morpheme segmentation --------------------------------------------------------------'
    for n in $(seq $nj); do
        # the next command does nothing unless _corpus_task_/storage/ exists, see
        # utils/create_data_link.pl for more info.
        utils/create_data_link.pl $srcdir/normedCorpus.seg.$n
    done
    $cmd JOB=1:$nj $logdir/normedCorpus.seg.JOB.log \
		morfessor -l $srcdir/morfessor.model.pickled \
		--output-format \'{analysis} \' -T $srcdir/normedCorpus.JOB \
		-o $srcdir/normedCorpus.seg.JOB --output-newlines \
		--nosplit-re "'[0-9\[\]\(\){}a-zA-Z&.,\-]+'"
fi

# nonHangulList from general domain (freq. > 10)  + morphemes from Morfessor
if [ ! -f $srcdir/morphemes ]; then
	echo 'Extract uniq Morphemes ----------------------------------------------------------'

	cat $srcdir/uniqWordList.nonhangul | grep -E "^[A-Z]+ " > $srcdir/uniqWordList.nonhangul.alphabet
	cat $srcdir/uniqWordList.nonhangul | grep -v -E "^[A-Z]+ " | awk '{print $1}' > $srcdir/morphemes.etc

	coverage=0.98
	totalCnt=$(awk 'BEGIN{sum=0}{sum+=$2}END{print sum}' $srcdir/uniqWordList.nonhangul.alphabet)
    awk -v totalCnt="$totalCnt" -v coverage="$coverage" \
        'BEGIN{sum=0}{sum+=$2; if(sum/totalCnt <= coverage){print $1}}' $srcdir/uniqWordList.nonhangul.alphabet \
		> $srcdir/morphemes.alphabet
	
	cat $srcdir/morfessor.lexicon | awk '{print $2}' > $srcdir/morphemes.hangul
	cat $srcdir/morphemes.hangul $srcdir/morphemes.alphabet $srcdir/morphemes.etc |\
		sort | uniq > $srcdir/morphemes
	
	echo '  morphemes hangul: '$(wc -l <$srcdir/morphemes.hangul)
	echo '  morphemes alphabet: '$(wc -l <$srcdir/morphemes.alphabet)
	echo '  morphemes etc: '$(wc -l <$srcdir/morphemes.etc)
	echo '  total morphemes: '$(wc -l <$srcdir/morphemes) 
	echo '  check morphemes longer than 10 characters'
	awk 'BEGIN{sum=0;total=0}{if(length($1)>10){print $0;sum+=1}total+=1}END{print(sum" "total)}' \
		$srcdir/morphemes
fi

if [ ! -f $srcdir/lexicon ]; then
(
	echo "Starts to build lexicon ----------------------------------------------------------"
	$scriptdir/buildLexicon.sh $srcdir $srcdir/morfessor.model.txt
)&
fi

if [ ! -f $srcdir/corpus.lm.fg.arpa.gz ]; then
(
	echo "Starts to build n-gram language model ---------------------------------------------"
	$scriptdir/buildNGRAM.sh $srcdir
)&
fi
wait

date=$(date +'%F-%H-%M')
echo ends at $date
