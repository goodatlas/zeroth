#!/usr/bin/env python3

import fileinput
import sys

lexicon = {}
nLine = 1
for line in fileinput.input():
    #if nLine == 1:
    #    nLine += 1
    #    continue
    if nLine % 500 == 0:
        print('  %d line processed' %(nLine), end='\r', file=sys.stderr)
        sys.stderr.flush()
    nLine += 1

    if line.strip() == '+pause+':
        morphList = '+pause+'
        pronunList = ''
    else:
        morphs, pronuns = line.strip().split('\t')
        morphList  = morphs.split('+')
        pronunList = pronuns.split('+')
        if morphs == '+':
            morphList = morphs.split()

        if len(morphList) != len(pronunList):
            sys.stderr('number of morphemes and pronunciations are differenet')

    for elem in zip(morphList, pronunList):
        morph  = elem[0].strip()
        pronun = elem[1].strip()
        if morph not in lexicon:
            lexicon[morph] = [pronun]
        else:
            if pronun not in lexicon[morph]:
                lexicon[morph].append(pronun)

print('  %d line processed' %(nLine), file=sys.stderr)
print('There are %d unique morphemes' % len(lexicon), file=sys.stderr)

sortedList = sorted(lexicon.items(), key=lambda x:x[0])
print('', file=sys.stderr)
print('Lexicon is now sorted', file=sys.stderr)
sys.stderr.flush()

for key, values in sortedList:
    for value in values:
        print(key+'\t'+value)
