#!/bin/bash
exists(){
	command -v "$1" >/dev/null 2>&1
}

# LM pruning threshold for the 'small' trigram model
prune_thresh_small=0.0000003

# LM pruning threshold for the 'medium' trigram model
prune_thresh_medium=0.0000001

vocab=../_textNormalization_/morphemes  # vocab for LM training
src=../_textNormalization_

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
testSetSize=100
find $src -name "mergedNormCorpus.task.a*.seg" | parallel "$cmd_shuf {} |\
	./splitText -l $testSetSize {} {}"
cat ../_textNormalization_/mergedNormCorpus.task.a*.seg.train > corpus_task.train
cat ../_textNormalization_/mergedNormCorpus.task.a*.seg.test > corpus_task.test

txt=corpus_task
echo 'Generate LM --------------------------------------------------------------------------'
echo 'Perplexity test: --------------------------------------------------------------'
echo '  text: '$txt', vocab: '$vocab
echo '  Perplexity test 3-gram '
ngram=3
ngram-count -order $ngram -unk -map-unk "<UNK>" -vocab $vocab -text $txt.train -lm $txt.lm.tg.arpa.gz \
	-kndiscount -interpolate
ngram -order 3 -lm $txt.lm.tg.arpa.gz -ppl $txt.test -debug 2 > $txt.ppl.tg

echo '  Perplexity test 4-gram '
ngram=4
ngram-count -order $ngram -unk -map-unk "<UNK>" -vocab $vocab -text $txt.train -lm $txt.lm.fg.arpa.gz \
	-kndiscount	-interpolate
ngram -order 4 -lm $txt.lm.fg.arpa.gz -ppl $txt.test -debug 2 > $txt.ppl.fg




exit 1 
