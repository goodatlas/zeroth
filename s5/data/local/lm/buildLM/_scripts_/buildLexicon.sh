#!/bin/bash
# Build lexicon, pronunciation dictionary
#
# Copyright  2017  Atlas Guide (Author : Lucas Jo)
#
# Apache 2.0
#
. ./cmd.sh
. ./path.sh


scriptdir=buildLM/_scripts_

. parse_options.sh || exit 1;

if [ "$#" -ne 2 ]; then
	echo "Usage: $0 <src-dir> <src-model>"
	exit 1
fi
srcdir=$1
model=$2
nonHangulList="$srcdir/morphemes.alphabet $srcdir/morphemes.etc"
if [ $srcdir != buildLM/_corpus_task_ ] && [ -d buildLM/_corpus_task_ ]; then
    echo "  merging morphemes from buildLM/_corpus_task_"

    if [ -f buildLM/_corpus_task_/morphemes.alphabet ]; then
        nonHangulList="buildLM/_corpus_task_/morphemes.alphabet "$nonHangulList
    fi
    if [ -f buildLM/_corpus_task_/morphemes.etc ]; then
        nonHangulList="buildLM/_corpus_task_/morphemes.etc "$nonHangulList
    fi
fi

set -e 
date=$(date +'%F-%H-%M')
echo start $0 at $date

echo 'Generate pronunciation for non-hangul morphemes'
if [ ! -f $srcdir/morphemes.nonhangul.sorted.pron ]; then

	cat $nonHangulList | sort | uniq > $srcdir/morphemes.nonhangul.sorted
	$scriptdir/genPronunciation_cmu.py $srcdir/morphemes.nonhangul.sorted > tmp
	$scriptdir/genPronunciation.py tmp > $srcdir/morphemes.nonhangul.sorted.pron
	rm -f tmp
	$scriptdir/checkPronun.py $srcdir/morphemes.nonhangul.sorted.pron > noPronList
	if [ $(wc -l <noPronList) -ne 0 ]; then
		echo '  [ERROR] There exist morphemes without pronunciation, plz check noPronList'
		cat noPronList
		rm -f noPronList
		exit 0
	fi
fi

echo 'Generated Korean pronunciation'
if [ ! -f $srcdir/lexicon ]; then
	cat $srcdir/morphemes.nonhangul.sorted.pron > $srcdir/finalList
	cut -d' ' -f2- $model | awk '{if(NR>1){print $0}}' >> $srcdir/finalList
	
	# genPhoneSeq.py generates dic.pronun
	if [ -f dic.pronun ]; then
		cp dic.pronun dic.pronun.old
	fi
	$scriptdir/genPhoneSeq.py $srcdir/finalList  

	echo 'Extract uniq lexicon '
	$scriptdir/genLexicon.py dic.pronun > $srcdir/lexicon
	mv dic.pronun $srcdir/dic.pronun
fi
date=$(date +'%F-%H-%M')
echo ends $0 at $date
