#!/usr/bin/env python3
#     _____   __  .__                    ________      .__    .___      
#    /  _  \_/  |_|  | _____    ______  /  _____/ __ __|__| __| _/____  
#   /  /_\  \   __\  | \__  \  /  ___/ /   \  ___|  |  \  |/ __ |/ __ \ 
#  /    |    \  | |  |__/ __ \_\___ \  \    \_\  \  |  /  / /_/ \  ___/ 
#  \____|__  /__| |____(____  /____  >  \______  /____/|__\____ |\___  >
#      \/               \/     \/          \/              \/    \/ 
#
import re
import fileinput
import sys
import at_unicode

def normalize():

    nLine_passed = 0
    nLine = 0
    for line in fileinput.input():
        if nLine % 1000 == 0:
            print("  %d line processed"%nLine, end='\r', file=sys.stderr)
        nLine += 1
        
        tstr = line.strip()
        # remove meaningless start
        tstr = re.sub('^[^0-9a-zA-Z가-힣]+', '', tstr) 
        
        # delete no-Hangul line
        tstr = re.sub('^([^가-힣]+)$', ' ', tstr)

        # ignore sentences with urls
        if re.search('www', tstr): continue 
        if re.search('http', tstr): continue 
        if re.search('ftp', tstr): continue 

        # .
        tstr = re.sub('\.\s*$', '.', tstr)
        
        # ;
        tstr = re.sub(';', '', tstr)
     
        # ignore sentences with multi-variate pronunciation symbols
        # too many, need to another approach
        if re.search('[/\-=:~+]', tstr): continue

        # remove ? !
        #tstr = re.sub('[!?]', ' ', tstr)
        tstr = re.sub('\s+([\.\,\'\!\?])', '\\1 ', tstr)

        # . , should be removed after treating numerics
        
        # filter sentence with [a-z] characters
        #  not convertable into Korean now, need transliteration
        regexEpr = r"^[ \.,?!가-힣0-9A-Z" + re.escape(at_unicode.valids) + r"]+$"
        if re.match(regexEpr, tstr):
            tstr = re.sub(r'(\ )+', ' ', tstr).strip()
            print(tstr)
            nLine_passed += 1

    print("  %d / %d line processed"%(nLine_passed, nLine), file=sys.stderr)

if __name__ == '__main__':
    normalize()
