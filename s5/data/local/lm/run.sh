#!/bin/bash
# Build Korean n-gram based Language Model
#
# Copyright  2017  Atlas Guide (Author : Lucas Jo)
# Apache 2.0
# 
# run ./extras/install_srilm.sh at $KALDI_ROOT/tools
# after download and locate archeived file named as srilm.taz
exists(){
    command -v "$1" >/dev/null 2>&1
}

# check parallel installed
if ! exists parallel; then
    echo "Please, install parallel"
    echo "-  sudo apt-get install parallel"
    exit 1
fi

. ./cmd.sh
. ./path.sh

corpusList=" \
    rawCorpus_subtitle_cineaste.tar.gz \
    rawCorpus_DramaMovieScripts.tar.gz \
    rawCorpus_Bobaedream.tar.gz \
    rawCorpus_Clien.tar.gz \
    rawCorpus_Chosun.tar.gz \
    rawCorpus_Joongang.tar.gz \
    rawCorpus_NamuWiki_n.tar.gz \
    rawCorpus_DAUM_INTERVIEW.tar.gz \
    rawCorpus_DAUM_RANKINGNEWS.tar.gz \
    rawCorpus_DAUM_RANKINGNEWS2.tar.gz \
    rawCorpus_JW_AWAKE.tar.gz \
    rawCorpus_SEJONG.tar.gz \
    rawCorpus_RECSCRIPT.tar.gz \
    rawCorpus_WIKI_AA.tar.gz \
    rawCorpus_WIKI_AB.tar.gz \
    rawCorpus_WIKI_AC.tar.gz \
    rawCorpus_WIKI_AD.tar.gz \
    rawCorpus_WIKI_AE.tar.gz \
    rawCorpus_WIKI_AF.tar.gz"

cmd=$normalize_cmd
srcdir=buildLM/_corpus_
scriptdir=buildLM/_scripts_

. parse_options.sh || exit 1;


set -e
date=$(date +'%F-%H-%M')
echo start at $date
# Download rawCorpus
#  raw text corpus is not open-source, plz use run_task.sh
#  
#echo "Now download raw corpus -------------------------------------------------"
#for corpus in $corpusList; do
#    $scriptdir/download_corpus.sh $corpus $srcdir
#done
#
#echo 'Untar all ----------------------------------------------------------------'
#for corpus in $(find $srcdir -name "*.tar.gz"); do
#    tardir=$(echo $corpus | sed -E 's/.tar.gz//g')
#    if [ -d $tardir ]; then
#        echo "  $corpus is already untar-ed"
#        continue
#    fi
#    tar -zxvf $corpus -C $srcdir
#done

echo "Raw text corpus is not open-source, this code is not working"
echo "  plz use run_task.sh"
exit 1

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
    utils/create_split_dir.pl /mnt/{ares,hephaestus,jupiter,neptune}/$USER/lm_data/zeroth/s5/_corpus_/storage \
        $srcdir/storage
fi

# Normalization
echo 'Text normalization starts ---------------------------------------------------'
nj=$(cat $srcdir/num_jobs)
logdir=$srcdir/log
if [ ! -d $logdir ]; then
    mkdir -p $logdir
fi

if [ ! -e $srcdir/normedCorpus.1 ] ; then
    for n in $(seq $nj); do
        # the next command does nothing unless _corpus_/storage/ exists, see
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

echo 'Finding Uniq. words for morpheme analysis --------------------------------------'
if [ ! -e $srcdir/uniqWords.1 ] ; then
    for n in $(seq $nj); do
        # the next command does nothing unless _corpus_/storage/ exists, see
        # utils/create_data_link.pl for more info.
        utils/create_data_link.pl $srcdir/uniqWords.$n
    done
    $cmd JOB=1:$nj $logdir/normedCorpus.JOB.log \
        cat $srcdir/normedCorpus.JOB \| \
        tr -s \'[:space:]\' \'\\n\' \| sort \| uniq -c \| \
        sort -k1 -n -r \> $srcdir/uniqWords.JOB || exit 1;
fi

echo "Accumulate statistics into: uniqWordList ------------------------------------------"
if [ ! -f $srcdir/uniqWordList ]; then
    cat $srcdir/uniqWords.* | \
        $scriptdir/sumStatUniqWords.py > $srcdir/uniqWordList
    stat=$(awk 'BEGIN{sum=0;cnt=0}{cnt+=1;if($2 == 1){sum+=1}}END{print sum"/"cnt}' $srcdir/uniqWordList)
    echo "  total uniq. word count: $(echo $stat | awk -F'/' '{print $2}')"
    percentage=$(echo "print('portion of freq.== 1 word: {:.2f} %'.format($stat*100))" | python3)
    echo "  $percentage"
fi

echo "Pruning uniqWordList for Morfessor training -----------------------------------------"
coverage=0.98
srcFile=$srcdir/uniqWordList
inFile=$srcdir/uniqWordList.hangul
inFile2=$srcdir/uniqWordList.nonhangul
outFile=$srcdir/uniqWordList.hangul.pruned
if [ ! -f $inFile ]; then
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

echo 'Morfessor model training  -----------------------------------------------------------'
if [ ! -f $srcdir/morfessor.model.pickled ]; then
    morfessor --traindata-list \
        -t $outFile \
        -S $srcdir/morfessor.model.txt \
        -s $srcdir/morfessor.model.pickled \
        -x $srcdir/morfessor.lexicon \
        --randsplit 0.5 --skips \
		--progressbar \
        --nosplit-re '[0-9\[\]\(\){}a-zA-Z&.,\-]+'

	#morfessor --traindata-list \
    #    -t $outFile \
    #    -S $srcdir/morfessor.model.txt \
    #    -s $srcdir/morfessor.model.pickled \
    #    -x $srcdir/morfessor.lexicon \
	#	-a viterbi --viterbi-smoothing 20 \
	#	--randsplit 0.5 --skips \
	#	--progressbar \ 
    #    --nosplit-re '[0-9\[\]\(\){}a-zA-Z&.,\-]+'

fi

segModel=$srcdir/morfessor.model.pickled
segModelTxt=$srcdir/morfessor.model.txt
segModelLexicon=$srcdir/morfessor.lexicon
if [ -f buildLM/_corpus_task_/morfessor.model.pickled ] && 
	[ buildLM/_corpus_task_/morfessor.model.pickled -nt $srcdir/morfessor.model.pickled ]; then
	segModel=buildLM/_corpus_task_/morfessor.model.pickled
	segModelTxt=buildLM/_corpus_task_/morfessor.model.txt
	segModelLexicon=buildLM/_corpus_task_/morfessor.lexicon
	echo "  found more recently trained segment model: "
	echo "  1.  $segModel"
	echo "  2.  $segModelTxt"
	echo "  3.  $segModelLexicon"
	echo "  use this one"
fi

echo 'Morpheme segmentation --------------------------------------------------------------'
# The Morfessor should be installed in the all Grid machines
if [ ! -f $srcdir/normedCorpus.seg.1 ]; then
    for n in $(seq $nj); do
        # the next command does nothing unless _corpus_/storage/ exists, see
        # utils/create_data_link.pl for more info.
        utils/create_data_link.pl $srcdir/normedCorpus.seg.$n
    done
	
    $cmd JOB=1:$nj $logdir/normedCorpus.seg.JOB.log \
		morfessor -l $segModel \
		--output-format \'{analysis} \' -T $srcdir/normedCorpus.JOB \
		-o $srcdir/normedCorpus.seg.JOB --output-newlines \
		--nosplit-re "'[0-9\[\]\(\){}a-zA-Z&.,\-]+'"
fi

echo 'Extract uniq Morphemes ----------------------------------------------------------'
# nonHangulList from general domain (freq. > 10)  + morphemes from Morfessor
if [ ! -f $srcdir/morphemes ]; then

	cat $srcdir/uniqWordList.nonhangul | grep -E "^[A-Z]+ " > $srcdir/uniqWordList.nonhangul.alphabet
	cat $srcdir/uniqWordList.nonhangul | grep -v -E "^[A-Z]+ " | awk '{print $1}' > $srcdir/morphemes.etc

	coverage=0.98
	totalCnt=$(awk 'BEGIN{sum=0}{sum+=$2}END{print sum}' $srcdir/uniqWordList.nonhangul.alphabet)
    awk -v totalCnt="$totalCnt" -v coverage="$coverage" \
        'BEGIN{sum=0}{sum+=$2; if(sum/totalCnt <= coverage){print $1}}' $srcdir/uniqWordList.nonhangul.alphabet \
		> $srcdir/morphemes.alphabet


	cat $segModelLexicon | awk '{print $2}' > $srcdir/morphemes.hangul
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

echo "Starts to build lexicon ----------------------------------------------------------"
if [ ! -f $srcdir/lexicon ]; then
(
	$scriptdir/buildLexicon.sh $srcdir $segModelTxt
)&
fi

echo "Starts to build n-gram language model ---------------------------------------------"
if [ ! -f $srcdir/corpus.lm.fg.arpa.gz ]; then
(
	$scriptdir/buildNGRAM.sh $srcdir
)&
fi
wait

echo "Copy LM files to top --------------------------------------------------------------"
echo "  $segModel"
cp -rpf $segModel zeroth_morfessor.seg
cp -rpf $srcdir/lexicon zeroth_lexicon
cp -rpf $srcdir/corpus.lm.fg.arpa.gz zeroth.lm.fg.arpa.gz
cp -rpf $srcdir/corpus.lm.tg.arpa.gz zeroth.lm.tg.arpa.gz
cp -rpf $srcdir/corpus.lm.tgmed.arpa.gz zeroth.lm.tgmed.arpa.gz
cp -rpf $srcdir/corpus.lm.tgsmall.arpa.gz zeroth.lm.tgsmall.arpa.gz

date=$(date +'%F-%H-%M')
echo ends at $date
