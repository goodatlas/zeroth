#!/bin/bash
# Copyright 2019   hwiorn <hwiorn@gmail.com>
# Apache 2.0.

nj=8
max_gen=10

. ./cmd.sh
. ./path.sh
. ./utils/parse_options.sh

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <src-dir> <dst-dir>"
    echo "e.g.: $0 /mnt/data/aihub/KsponSpeechAll data/aihub_kspon"
    exit 1
fi

src=${1%/}
dst=${2%/}

echo "$0: Data preparation for AI Hub Korean speech datasets(2000 speakers, ~1000hrs)"
mkdir -p $dst || exit 1

[ ! -d $src ] && echo "$0: no such directory $src" && exit 1
part_dirs=( $src/KsponSpeech_0{1,2,3,4,5} )

echo $0: Unzipping datasets ...
for part in ${part_dirs[@]}; do
    if [ ! -f $part/.done ]; then
        if [ ! -f $part.zip ]; then
            echo $0: $part.zip is not exists
            exit 1
        fi

        (
            set -e
            unzip -oqq $part.zip -d $src/
            touch $part/.done
        ) &
    fi
done
wait $(jobs -p)

gen_item() {
    path=${1%.pcm}
    txt=$path.txt
    echo -en "$path\t" | perl -pe 's:^./::g;s:/:_:g'
    echo -en "$1\t"
    perl -MEncode -ne '$_=encode("utf-8", decode("cp949", $_)); chomp; @dict=();
         s:\r::g; # remove LF
         for(m:(\(.+?\)/\(.+?\)):) { push @dict, $1; }
         $d=join "\t",@dict; # gather up filler words.
         print "$_\t$d\n";' $txt
}
export -f gen_item

echo -n "$0: Generating files.info "
iter=0
old_iter=0
files_info=()
for part_dir in ${part_dirs[@]}; do
    files_info+=($part_dir/files.info)
    if [ ! -s "$part_dir/files.info" ]; then
        ( find $part_dir -name '*.pcm'| parallel gen_item {} > $part_dir/files.info ) &
        iter=$[iter+1]
    fi

    if [ $old_iter -ne $iter -a $[iter%max_gen] -eq 0 ]; then
        echo -n .
        wait $(jobs -p)
    fi
    old_iter=$iter
done
echo
wait $(jobs -p)

echo -n "$0: Generating kspon dataset from files.info "
:>$dst/wav.scp.tmp>$dst/text.tmp>$dst/utt2spk.tmp>$dst/pronoun.dict.tmp
for info in ${files_info[@]}; do
    echo -n .
    awk -F'\t' '{print $1 " " $1}' $info >>$dst/utt2spk.tmp || exit 1

    # Ref. http://ai-hub.promptech.co.kr/notice_product/569
    perl -F'\t' -ane '#next if ($F[2] =~ m:u/:); # Skip the inaudiable(or unclear) utterance of sentence
         $F[2] =~ s:(\d+)\s*/\s*(\d+):\2 분에 \1:g; #Chagne division mark
         $F[2] =~ s:\.+:.:g; # remove multi-dots
         $F[2] =~ s:([a-zA-Z])\.([a-zA-Z])\.:\1\2:g; # e.g., D.C.
         $F[2] =~ s:u/::g; # Unclear utterance of sentence mark
         $F[2] =~ s:o/::g; # Noise mark of utterance
         $F[2] =~ s:[lbn]/::g; # Breath, laugh, BG noise mark
         $F[2] =~ s:([가-힣]+?)/:\1:g; # Replace a interjection(filler words)
         $F[2] =~ s:\+::g; # Utterance repetation mark
         $F[2] =~ s:\Q*\E::g; # Unclear words utterance mark
         $F[2] =~ s:[\?\#\!,]::g; # Some other symbols
         $F[2] =~ s:([^\d])\.([^\d]):\1\2:g; # Remove dot with non-numbers
         $F[2] =~ s:([\d])\.([^\d ]):\1\2:g; # Remove dot with non-numbers
         $F[2] =~ s:([^\d ])\.([\d]):\1\2:g; # Remove dot with non-numbers
         #$F[2] =~ s:\((.+?)\)/\((.+?)\):\1:g; #representation (it needs too much exception)
         $F[2] =~ s:\((.+?)\)/\((.+?)\):\2:g; #representation
         $F[2] =~ s:([\w가-힣])-([\w가-힣]):\1 \2:g; #remove hyphen mark used to join words
         $F[2] =~ s:/::g; # remove some slash
         $F[2] =~ s:^[\s\.]+::g; # trim left
         $F[2] =~ s:[\s\.]+$::g; # trim right
         $F[2] =~ s: +: :g; # remove multi-spaces
         print "$F[0] $F[2]\n";' $info >>$dst/text.tmp || exit 1
    awk -F'\t' '{print $1 " sox -t raw -r 16k -b 16 -e signed-integer -L \"" $2 "\" -t wav - | "}' $info >>$dst/wav.scp.tmp || exit 1
    cut -f4- $info | perl -lane 'next if(/^$/); print "$1\t$2" if(/\(\s*(.+?)\s*\)\/\(\s*(.+?)\s*\)/)' >>$dst/pronoun.dict.tmp || exit 1
done
echo

echo $0: Sorting kspon dataset
env LC_ALL=C sort -u $dst/pronoun.dict.tmp > $dst/pronoun.dict
env LC_ALL=C sort -u $dst/text.tmp > $dst/text.tmp2
env LC_ALL=C sort -u $dst/utt2spk.tmp > $dst/utt2spk.tmp2
env LC_ALL=C sort -u $dst/wav.scp.tmp > $dst/wav.scp.tmp2

echo $0: Filtering inaudiable data
mv $dst/text.tmp2 $dst/text
utils/filter_scp.pl $dst/text $dst/utt2spk.tmp2 > $dst/utt2spk || exit 1
utils/filter_scp.pl $dst/text $dst/wav.scp.tmp2 > $dst/wav.scp || exit 1
rm -f $dst/*.tmp $dst/*.tmp2

echo $0: Generating spk2utt from utt2spk
utils/utt2spk_to_spk2utt.pl <$dst/utt2spk >$dst/spk2utt || exit 1
echo $0: Generating utt2dur
utils/data/get_utt2dur.sh --cmd "$train_cmd" --nj $nj $dst 1>&2 || exit 1
echo $0: Checking data
utils/validate_data_dir.sh --no-feats $dst || exit 1;

echo $0: done
exit 0
