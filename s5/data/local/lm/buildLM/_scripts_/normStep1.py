#!/usr/bin/env python3
# Normalization step 1
#
# Copyright  2017  Atlas Guide (Author : Lucas Jo)
#
# Apache 2.0
# 

import re
import fileinput
import sys
import at_unicode

def normalize():
    nLine = 0
    for line in fileinput.input():
        if nLine % 1000 == 0:
            print("  %d line processed"%nLine, end='\r', file=sys.stderr)
        nLine += 1
        tstr = line

        # empty line
        if not line.strip():
            continue

        # separator (conventions)
        tstr = re.sub('['+re.escape(at_unicode.separators)+']','\n', tstr)

        # remove bracked contents 
        tstr = re.sub('\([^\)]+\)', '', tstr)
        tstr = re.sub('\[[^\]]+\]', '', tstr)
        tstr = re.sub('【[^】]+】', '', tstr)
        tstr = re.sub('\<[^\>]+\>', '', tstr)

        # handle apostrophe
        quotes = at_unicode.apostrophe + at_unicode.quatation
        tstr = re.sub('([a-zA-Z])['+re.escape(quotes)+']([a-zA-Z])', '\\1<apostrophe>\\2', tstr)
        tstr = re.sub('['+re.escape(quotes)+']', '', tstr)
        tstr = re.sub('<apostrophe>', '\'',tstr)

        # replace various percent into one 
        tstr = re.sub('['+re.escape(at_unicode.percents)+']', '%' ,tstr)

        # miscellaneous
        tstr = re.sub('%p', '% 포인트', tstr)
        tstr = re.sub('±', '플러스 마이너스', tstr)
        tstr = re.sub('[a-zA-Z0-9_.]+@[a-zA-Z0-9_.]*',' ', tstr)   # delete e-mail
        
        # remove chinese and japanese characters
        tstr = re.sub(at_unicode.chinese, '', tstr)
        tstr = re.sub(at_unicode.japanese, '', tstr)
        
        # segment b/w Hangul and non-Hangul
        tstr = re.sub(r"([가-힣])([^ 가-힣])",r"\1 \2", tstr)
        tstr = re.sub(r"([^ 가-힣])([가-힣])",r"\1 \2", tstr)

        # segment b/w numerices and non-numerics
        tstr = re.sub('([0-9])([^ \.\,0-9])', '\\1 \\2', tstr)
        tstr = re.sub('([^ \+\-\.\,0-9])([0-9])', '\\1 \\2', tstr)

        # Leave only valid characters
        tstr = re.sub(at_unicode.invalids_chars, ' ', tstr)

        # remove repeated valid symbols
        tstr = re.sub('(['+re.escape(at_unicode.valids)+'])+', '\\1', tstr)

        # make valid symbols, except puctuations, as a unique word
        symbols = at_unicode.measureUnits + at_unicode.percents + at_unicode.currencies + at_unicode.userDefines
        regexEpr = r"([" + re.escape(symbols) + "])"
        tstr = re.sub(regexEpr, ' \\1 ', tstr)

        # remove spaces before puctuations 
        #tstr = re.sub('\s+(['+re.escape(at_unicode.puctuations)+'])', '\\1', tstr)

        # segment sentences
        tstr = re.sub('([가-힣])\s*\.', '\\1.\n', tstr)

        # segment sentences 2
        tstr = re.sub('([가-힣])\s*([\.?!])\s*([^가-힣]+ )', '\\1\\2\n\\3', tstr)
        
        # segment sentences 3
        # / (not readable)
        tstr = re.sub('([가-힣])\s+[/=:]\s+([가-힣])', '\\1\n\\2', tstr)
        tstr = re.sub('([a-zA-Z])\s+[/=:]\s+([가-힣])', '\\1\n\\2', tstr)
        tstr = re.sub('([가-힣])\s+[/=:]\s+([a-zA-Z])', '\\1\n\\2', tstr)

        tstr = re.sub(r'(\ )+', ' ', tstr).strip()
        print(tstr)

    print("  %d line processed"% nLine, file=sys.stderr)

if __name__ == '__main__':
    normalize()
