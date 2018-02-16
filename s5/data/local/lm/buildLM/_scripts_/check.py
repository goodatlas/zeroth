#!/usr/bin/env python3
import re
import fileinput
import json
import sys

validCharsKeyboard=" \n\"\'~`!?<>@#$%^&*(){}[]_-+=|\\/.,:;"

valid = re.compile(r'[ㄱ-ㅎㅏ-ㅣ가-힣0-9a-zA-Z]+')
chinese = re.compile(r'[\u2E80-\u2FD5\u3400-\u4DBF\u4E00-\u9FCC]+')

notValidSet = dict()

nLine=0
for line in fileinput.input():
    if nLine % 1000 == 0:
        print("  %d line processed"%nLine, end='\r', file=sys.stderr)
    nLine += 1

    tline = valid.sub(' ', line)
    tline = chinese.sub(' ', tline)
    for elem in tline:
        if elem in notValidSet:
            notValidSet[elem]+=1
            continue
        else:
            if elem not in [' ', '\n']:
            #if elem not in [' ', '\n', '.', '!', ',', '?']:
            #if elem not in validCharsKeyboard:
                notValidSet[elem]=1

sortedResult=sorted(notValidSet.items(), key=lambda x:x[1], reverse=True)
#resultDict = {a[0]: a[1] for a in sortedResult}
#json_dump  = json.dumps(resultDict)
#print(json_dump)

for item in sortedResult:
    print(item)


