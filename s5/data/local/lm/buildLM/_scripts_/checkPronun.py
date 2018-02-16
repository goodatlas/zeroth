#!/usr/bin/env python3
import fileinput
import sys
import re

def main():

    nLine=0
    for line in fileinput.input():
        if nLine%1000 == 0:
            print('  %d line processed' %(nLine), end='\r', file=sys.stderr)
            sys.stderr.flush()
        nLine+=1
        tstr = line.strip()
        
        if len(tstr.split()) == 1:
            print(tstr)
        
    print('  %d line processed' %(nLine), file=sys.stderr)

if __name__ == '__main__':
    main()
