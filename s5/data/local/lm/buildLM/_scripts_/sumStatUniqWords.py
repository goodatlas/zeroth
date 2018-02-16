#!/usr/bin/env python3
# summation all the stat from uniqWord.JOB
# build uniq word dictionary with count
#
# Copyright  2017  Atlas Guide (Author : Lucas Jo)
#
# Apache 2.0
# 
import fileinput
import json
import sys

def main():

    nLine = 1
    word_dict = dict()
    #f_out     = open('json_words' ,'w')
    word_count = 0
    for line in fileinput.input():
        # empty line
        if not line.strip():
            continue

        if nLine % 1000 == 0:
            print("  %d line processed"%nLine, end='\r', file=sys.stderr)
        nLine += 1

        tstrList = line.split()
        if len(tstrList) < 2:
            continue

        wordList = tstrList[1:]
        # from refining, incomming field could be multiple
        for curr_word in wordList:
            curr_count = int(tstrList[0])

            if curr_word not in word_dict:
                if len(wordList) == 1:
                    word_dict[curr_word] = curr_count
                else:
                    word_dict[curr_word] = 1
                word_count += 1
            else:
                word_dict[curr_word] += curr_count

    print("  REPORT: {} uniq. words are founded".format(word_count), file=sys.stderr)
    print("  now sorting", file=sys.stderr)

    sortedResult=sorted(word_dict.items(), key=lambda x:x[1], reverse=True)
    #resultDict = {a[0]: a[1] for a in sortedResult}
    #json_dump  = json.dumps(resultDict, f_out, indent=4, ensure_ascii=False)

    for item in sortedResult:
        print(item[0], item[1])

if __name__ == '__main__':
    main()
