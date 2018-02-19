#!/usr/bin/env python3
import re
import fileinput
import sys
import at_unicode

def segment(match):
    tstr=match.group(0)
    tstr=re.sub('([\,\.\'\!\/])', ' ', tstr)
    return tstr


def normalize():
    nLine = 1
    for line in fileinput.input():
        if nLine % 1000 == 0:
            print("  %d line processed"%nLine, end='\r', file=sys.stderr)
        nLine += 1
        tstr = line.strip()
        
        # numbers with '.'
        tstr = re.sub('(?=\S*[A-Z])(?=\S*[\.\,\'])\S*', segment, tstr)
        tstr = re.sub('(?=\S*[A-Z])(?=\S*[0-9])\S*', segment, tstr)

        tstr = re.sub(r'(\ )+', ' ', tstr).strip()
        print(tstr)
    print("  %d line processed"%nLine, file=sys.stderr)

if __name__ == '__main__':
    normalize()
