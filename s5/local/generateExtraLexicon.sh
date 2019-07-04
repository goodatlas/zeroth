#!/bin/bash

# Copyright 2019 hwiorn <hwiorn@gmail.com>
# Apache 2.0

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <data-dir> <lm-dir>"
    echo "   ex: $0 data/kspon data/local/lm"
    exit 1
fi
data_dir=$1
lm_dir=$2

text=$data_dir/text
script_dir=$lm_dir/buildLM/_scripts_

if [ ! -f $text ]; then
	echo $0: No such file: $text
	exit 1
fi

if [ ! -f $script_dir/cmudict-0.7b.txt ]; then
	echo $0: No such cmudict dictionary file.
	exit 1
fi

cut -d' ' -f2- $text > $text.tmp
echo "$0: Segmenting word class"
cat $text.tmp |\
	perl -Mutf8 -CS -pe 's/(?<=[가-힣])([^ 가-힣])/ \1/g; s/(?<=[^ 가-힣])([가-힣])/ \1/g;
			     s/(?<=[a-zA-Z])([^ a-zA-Z])/ \1/g; s/(?<=[^ a-zA-Z])([a-zA-Z])/ \1/g;
			     s/(?<=[0-9])([^0-9])/ \1/g; s/(?<=[^0-9])([0-9])/ \1/g' >\
		$text.tmp2

echo "$0: Generating unique word from AM text"
parallel -a $text.tmp2 --pipepart --block=11M tr -s '[:space:]' '\\n' \| env LC_ALL=C sort -u | env LC_ALL=C sort -u > $data_dir/uniqWords.txt

grep -P '[가-힣]+_?' $data_dir/uniqWords.txt  | env LC_ALL=C sort -u > $data_dir/uniqWords.hangul
grep -v -P '[가-힣]+_?' $data_dir/uniqWords.txt | env LC_ALL=C sort -u > $data_dir/uniqWords.nonhangul
cat $data_dir/uniqWords.nonhangul | grep -E "^[A-Z]+_? " > $data_dir/uniqWords.nonhangul.alphabet
cat $data_dir/uniqWords.nonhangul | grep -v -E "^[A-Z]+_? " | awk '{print $1}' > $data_dir/uniqWords.nonhangul.etc
cat $data_dir/uniqWords.nonhangul.{alphabet,etc} | env LC_ALL=C sort -u > $data_dir/uniqWords.nonhangul.sorted

echo "$0: Generating pronunciation for non-hangul morphemes"
env LC_ALL=en_US.UTF-8 $script_dir/genPronunciation_cmu.py $data_dir/uniqWords.nonhangul.sorted > $data_dir/tmp
env LC_ALL=en_US.UTF-8 $script_dir/genPronunciation.py $data_dir/tmp > $data_dir/tmp2

awk -F'\t' '{if(NF>1){print $0}}' $data_dir/tmp2 > $data_dir/uniqWords.nonhangul.sorted.pron
awk -F'\t' '{if(NF<2){print $0}}' $data_dir/tmp2 > $data_dir/noPronList
noPronCount=$(wc -l <$data_dir/noPronList)
if [ $noPronCount -ne 0 ]; then
        echo $0: There exist morphemes without pronunciation, plz check noPronList: $noPronCount
        head $data_dir/noPronList
        echo "... (omitted) ..."
        #rm -f $data_dir/noPronList
        #exit 1
fi

echo $0: Generating pronunciation
cat $data_dir/uniqWords.nonhangul.sorted.pron $data_dir/uniqWords.hangul > $data_dir/finalList
env LC_ALL=en_US.UTF-8 $script_dir/genPhoneSeq.py $data_dir/finalList

echo $0: Extracting uniq lexicon
env LC_ALL=en_US.UTF-8 $script_dir/genLexicon.py dic.pronun | perl -pe 's/^\s+$//g' > $data_dir/extra_lexicon.tmp
utils/filter_scp.pl --exclude $lm_dir/zeroth_lexicon $data_dir/extra_lexicon.tmp > $data_dir/extra_lexicon
mv -f dic.pronun $data_dir/dic.pronun

[ ! -s $data_dir/noPronList ] && rm -f $data_dir/noPronList
[ ! -s $data_dir/extra_lexicon ] && rm -f $data_dir/extra_lexicon

rm -f $text.tmp* $data_dir/tmp* $data_dir/*.tmp* $data_dir/uniqWords.* $data_dir/{dic.pronun,finalList,pronoun.dict}
echo $0: done

exit 0
