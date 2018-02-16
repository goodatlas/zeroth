#!/usr/bin/env python3
import requests
import json
import sys
import fileinput
import subprocess
import editDistance
import re


BASE_URL = "http://csearch.naver.com/dcontent/spellchecker.nhn"
_agent = requests.Session()

def check(text, debug=False):  # len(text) < 500
    text = text.strip()
    
    queries = {
        '_callback':'window.__jindo2_callback._spellingCheck_0',
        'q':text
    }
    
    headers = {
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Content-Type':'application/javascript;charset=UTF-8'
    }
    
    response = _agent.get(BASE_URL, params=queries, headers=headers)
    response = response.text[42:-2]
    
    # json
    responseDebug = response
    response = json.loads(response)
    html = response['message']['result']['html']

    # replace html tag
    html = html.replace('<span class=\'re_green\'>', '')
    html = html.replace('<span class=\'re_red\'>', '')
    html = html.replace('<span class=\'re_purple\'>', '')
    html = html.replace('</span>', '')

    if debug is True:
        return html, responseDebug
    else:
        return html

def main():
    nLine = 1
    for line in fileinput.input():
        # empty line
        if not line.strip():
            continue

        if nLine % 100 == 0:
            print("  %d line processed"%nLine, end='\r', file=sys.stderr)
        nLine += 1

        tstr = line.strip()

        freq = tstr.split()[0]
        iStr = " ".join(tstr.split()[1:])

        if len(iStr) < 10 or re.match('^[^가-힣]+$', iStr):
            print(freq, iStr)
            continue
        oStr = check(iStr)
       
        # check edit-distance 
        strA = iStr.replace(' ', '').strip()
        strB = oStr.replace(' ', '').strip()
        distance, backtrace = editDistance.get_distance(strA, strB)
        alignedA, alignedB  = editDistance.get_alignment(strA, strB, backtrace)

        if distance == 0 and len(iStr) == len(oStr):
            # No difference, so pass it
            print(freq, iStr)
            continue

        # apply only spacing
        list_oStr = list(oStr)
        i_count = 0
        result = []
        for i in range(len(list_oStr)):
            syl = list_oStr[i]
            if syl == ' ':
                result.append(' ')
                continue
            
            flag = backtrace[i_count]
            if flag == 'M':
                result.append(syl)
            elif flag in ['D', 'S']:
                result.append(alignedA[i_count])
            i_count += 1
            
        print(freq, "".join(result))

if __name__ == '__main__':
    main()
