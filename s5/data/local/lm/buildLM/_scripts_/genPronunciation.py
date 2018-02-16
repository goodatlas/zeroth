#!/usr/bin/env python3
import fileinput
import sys
import re
import at_unicode

MAX_NUMBER  = 9999999999999999

readTextUnit  = [['','만','억','조'], '십', '백', '천']
readText      = ['영','일','이','삼','사','오','육','칠','팔','구', '']
readNumber    = ['공','일','이','삼','사','오','육','칠','팔','구', '']
readCountUnit = ['','열','스물','서른','마흔','쉰','예순', '일흔', '여든','아흔']
readCount     = [['','하나','둘','셋','넷','다섯','여섯','일곱','여덟','아홉'],
                 ['','한','두','세','네','다섯','여섯','일곱','여덟','아홉']]

# 숫자를 서수방식으로 읽기
#  1~99 사이 숫자만 지원 
#  Option
#     0: 뒤에 단위가 없을 때 (default)
#     1: 뒤에 단위가 있는 경우 사용 
def number2readCount(numbers, option=1):
    # numbers expected as a text variable 
    cnt=0
    result=[]
    if int(numbers) > 99:
        sys.exit('Out-of-range: read count range is 1~99')
    for number in reversed(numbers):
        idxNum = int(number)
        if cnt == 0:
            res=readCount[option][idxNum]
        else:
            res=readCountUnit[idxNum]
        #print(number, res)     
        if res:
            result.insert(0, res)
        cnt +=1
    return result
    #return " ".join(result)


# 숫자를 기수방식을 읽기
# 최대숫자 9999,9999,9999,9999
# option1
#    0: 모두 기수방식으로 읽음 (default)
#    1: 백자리 아래를 서수로 읽음
# option2 
#    number2readCount option 참조
#
def number2readText(numbers, option1=0, option2=0):
    # numbers expected as a text variable 
    cnt=0
    result=[]
    if int(numbers) > MAX_NUMBER:
        return ''
        #sys.exit("Out of range: 0 ~ 9999999999999999")
    numbers = str(int(numbers))
    for number in reversed(numbers):
        idxNum = int(number)
        prec   = cnt%4
        if prec == 0:
            # for every 4th location
            rNum = readText[idxNum]
            rLoc =  ''
            if cnt != 0: # 1's location ignore
                rLoc = readTextUnit[0][cnt//4]
            res  = rNum +" "+ rLoc
        else:
            rNum = readText[idxNum]          # 일, 이 ...
            rLoc = readTextUnit[cnt%4]       # 천, 백 ... 
            res=rNum+rLoc

        # Exceptions for '영'
        if rNum ==  '영':
            if len(numbers) != 1:
                if rLoc in ['만', '억', '조']:
                    cLoc=len(numbers)-cnt
                    if numbers[cLoc-4:cLoc] == '0000':
                        res=''
                    else:
                        res=rLoc
                else:
                    res=''
            else:
                res=rNum

        # Exceptions for '일'
        if rNum == '일':
            if cnt not in [12, 8, 4, 0]:
                res=rLoc
            else:
                if cnt == 4 and len(numbers) == 5:
                    res=rLoc

        #print(res, number, prec, cnt)
        if res: 
            result.insert(0, res)
        cnt +=1
    if option1:
        rStr = number2readCount(numbers[-2:], option2)
        result[-2:]=rStr

    # 조/억/만 단위 띄어쓰기
    outStr = " ".join(result)
    return outStr

def number2readNumber(numbers):
    result=[]
    for number in reversed(numbers):
        idxNum = int(number)
        rNum = readNumber[idxNum]
        result.insert(0, rNum)
    return " ".join(result)

ALPH = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','&']
ALPH2KOR = ['에이','비','씨','디','이','에프','지','에이치','아이','제이','케이',
        '엘','엠','엔','오','피','큐','알','에스','티','유','브이','더블유','엑스','와이','제트','엔']

NUM     = ['0','1','2','3','4','5','6','7','8','9']
NUM2KOR = ['제로','원','투','쓰리','포','파이브','씩스','쎄븐','에잇','나인']

def convAlphabet(match):
    ch = match.group(1).lower()
    kor = match.group(0) + '\t'
    for alpha in ch:
        if alpha in ALPH:
            kor += ALPH2KOR[ALPH.index(alpha)]
        else:
            kor += alpha
        kor += ' '
    return kor

def num2engKor(ch):
    kor = ''
    if ch in NUM:
        kor += NUM2KOR[NUM.index(ch)]
    else:
        kor += ch
    return kor


def convNumber(match):

    tmp  =  number2readText(match.group(1), 1, 0)   # 열 둘
    if tmp == '': tmp = '빵'
    tmp2 =  number2readText(match.group(1), 1, 1)   # 열 두
    if tmp2 == '': tmp2 = '빵'

    tstr =  match.group(0) + '\t' + number2readText(match.group(1), 0, 0) + '\n'  # 십 이
    tstr += match.group(0) + '\t' + tmp + '\n'
    if tmp2 != tmp:
        tstr += match.group(0) + '\t' + tmp2 + '\n'
    tstr += match.group(0) + '\t' + number2readNumber(match.group(1))  # 일 이
    ch = str(int(match.group(1)))
    if len(ch) == 1:
        tstr += '\n' + match.group(0) + '\t' + num2engKor(ch) # 제로
    return tstr

def convSymbols(match, _dict_):
    prefix = match.group(0) + '\t'
    char=match.group(1)
    tstr =''
    for elem in _dict_[char]:
        if elem != '':
            tstr += prefix + elem + '\n'
        else:
            tstr += prefix + '\n'
    tstr = tstr[:-1]
    return tstr

def convEqual(match):
    tstr =  "{}\t{}\n".format(match.group(0), '은')
    tstr += "{}\t{}\n".format(match.group(0), '는')
    tstr += "{}\t{}".format(match.group(0), '이콜')
    return tstr

def main():
    units = r"([" + re.escape(''.join(at_unicode.measureUnits_pronun.keys())) + r"])"
    userDefines = r"([" + re.escape(''.join(at_unicode.userDefines_pronun.keys())) + r"])"
    currencies = r"([" + re.escape(''.join(at_unicode.currencies_pronun.keys())) + r"])"

    nLine=0
    for line in fileinput.input():
        if nLine%1000 == 0:
            print('  %d line processed' %(nLine), end='\r', file=sys.stderr)
            sys.stderr.flush()
        nLine+=1
        tstr = line.strip()

        # if the line already has its pronun
        if len(tstr.split('\t')) >= 2:
            print(tstr)
            continue

        # ignore </s> <s>
        if re.match('<.+>', tstr):  
            continue
        #tstr = re.sub('(\[)?(=)(\])?', convEqual, tstr)
        tstr = re.sub('(\d+)', convNumber, tstr)
        tstr = re.sub('([A-Z]+)', convAlphabet, tstr)
        tstr = re.sub('\[([가-힣]+)\]', '[\\1]\t\\1', tstr)
        tstr = re.sub('\{([가-힣]+)\}', '{\\1}\t\\1', tstr)
        tstr = re.sub('\(([가-힣]+)\)', '(\\1)\t\\1', tstr)

        tstr = re.sub(units, lambda x: convSymbols(x, at_unicode.measureUnits_pronun), tstr)
        tstr = re.sub(userDefines, lambda x: convSymbols(x, at_unicode.userDefines_pronun), tstr)
        tstr = re.sub(currencies, lambda x: convSymbols(x, at_unicode.currencies_pronun), tstr)
        
        print(tstr)
    print('  %d line processed' %(nLine), file=sys.stderr)

if __name__ == '__main__':
    main()
