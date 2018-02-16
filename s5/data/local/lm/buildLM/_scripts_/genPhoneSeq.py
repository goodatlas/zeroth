#!/usr/bin/env python3
# Author: Lucas Jo
# Data: 2017.04.05
# Ref.: https://www.korean.go.kr/front/page/pageView.do?page_id=P000097&mn_id=95
#
#  받침 대표음
#
#            ㄾ
#   ㄳ       ㄽ    ㅄ        ㅀ
#   ㄺ ㄵ    ㄾ ㄻ ㄿ        ㄶ
#   ----------------------------
#   ㄱ ㄴ ㄷ ㄹ ㅁ ㅂ ㅇ    (ㅎ)
#   ----------------------------
#   ㄲ    ㅅ       ㅍ
#   ㅋ    ㅆ
#         ㅈ
#         ㅊ
#         ㅌ
#
#
# 구현상 주의점
# 1.  15항 내용은 13항 앞서 적용함 
#       맛없다 [마섭따] (x)
#              [마답따] (o)

import re
import sys
import fileinput
from konlpy.tag import Mecab

# Unicode
BASE_CODE   = 0xac00 # 44032
START_CODE  = 0x1100
MIDDLE_CODE = 0x1161
END_CODE    = 0x11A7

CHOSUNG_LIST =  [u'ㄱ', u'ㄲ', u'ㄴ', u'ㄷ', u'ㄸ', u'ㄹ', u'ㅁ', u'ㅂ', u'ㅃ', u'ㅅ',\
                 u'ㅆ', u'ㅇ', u'ㅈ', u'ㅉ', u'ㅊ', u'ㅋ', u'ㅌ', u'ㅍ', u'ㅎ']
JUNGSUNG_LIST = [u'ㅏ', u'ㅐ', u'ㅑ', u'ㅒ', u'ㅓ', u'ㅔ', u'ㅕ', u'ㅖ', u'ㅗ', u'ㅘ',\
                 u'ㅙ', u'ㅚ', u'ㅛ', u'ㅜ', u'ㅝ', u'ㅞ', u'ㅟ', u'ㅠ', u'ㅡ', u'ㅢ', u'ㅣ']
JONGSUNG_LIST = [u'_', u'ㄱ', u'ㄲ', u'ㄳ', u'ㄴ', u'ㄵ', u'ㄶ', u'ㄷ', u'ㄹ', u'ㄺ',\
                 u'ㄻ', u'ㄼ', u'ㄽ', u'ㄾ', u'ㄿ', u'ㅀ', u'ㅁ', u'ㅂ', u'ㅄ', u'ㅅ',\
                 u'ㅆ', u'ㅇ', u'ㅈ', u'ㅊ', u'ㅋ', u'ㅌ', u'ㅍ', u'ㅎ']

CHOSUNG_SYM =  [u'g', u'gg', u'n', u'd', u'dd', u'l', u'm', u'b', u'bb', u's',\
                u'ss', u'', u'j', u'jj', u'ch', u'kh', u't', u'p', u'h']
JUNGSUNG_SYM = [u'a', u'ae', u'ya', u'yae', u'eo', u'e', u'yeo', u'ye', u'o', u'wa',\
                u'wae', u'oe', u'yo', u'u', u'wo', u'we', u'wi', u'yu', u'eu', u'ui', u'i']
JONGSUNG_SYM = [u'', u'g2', u'', u'', u'n2', u'', u'', u'd2', u'l2', u'',\
                u'', u'', u'', u'', u'', u'', u'm2', u'b2', u'', u'',\
                u'', u'ng', u'', u'', u'', u'', u'', u'']

# Ref.: http://blog.daum.net/_blog/BlogTypeView.do?blogid=06Se2&articleno=13296286
SYM_NOSOUND = '_'
DELIM_PRONUN = ':'

# MECAB SYMBOLS
JOSA    = ['JKS','JKC','JKG','JKO','JKB','JKV','JKQ','JC']      # 조사
URMIE   = ['EP','EF','EC','ETN','ETM']                          # 어미
POSTFIX = ['XSN','XSV','XSA']                                   # 접미사
EFFMORF = ['NNG','NNP','NNB','NNBC','VV','VA','MAG','MAJ']      # 실질형태소 


def toCode(idx, plist):
    if idx< 0 or idx >= len(plist):
        return SYM_NOSOUND
    else:
        return plist[idx]

def separate(ch):
    uindex = ord(ch) - 0xac00

    jongseong = uindex % 28
    joongseong = ((uindex - jongseong) // 28) % 21
    choseong = ((uindex - jongseong) // 28) // 21

    return [choseong, joongseong, jongseong]

def build(choseong, joongseong, jongseong):
    code = int(((((choseong) * 21) + joongseong) * 28) + jongseong + BASE_CODE)
    #try:
    #    # Python 2.x
    #    return unichr(code)
    #except NameError:
        # Python 3.x
    return chr(code)

def unroll(sentence):
    text = re.sub('[^ 가-힣]', '', sentence).strip()  # 띄어쓰기 남겨놓기
    #text = re.sub('[^가-힣]', '', sentence).strip()
    unrolled_indexes = []
    for i in range(len(text)):
        syllable = text[i]
        if syllable == u' ':
             unrolled_indexes.append([-1])
        else:
            indexes = separate(syllable)
            unrolled_indexes.append(indexes)
    return unrolled_indexes

def toPhonemeString(sentence):
    unrolled = unroll(sentence)

    oStr = ''
    for syllable in unrolled:
        if len(syllable) == 3:
            oStr += toCode(syllable[0], CHOSUNG_LIST)
            oStr += toCode(syllable[1], JUNGSUNG_LIST)
            oStr += toCode(syllable[2], JONGSUNG_LIST)
        else:
            oStr += '/'
    return oStr

def toUnrolled(pStr):

    text = re.sub('[/:]','', pStr)
    if len(text) % 3 != 0:
        sys.exit('Total length is not a multiple of 3')

    unrolled=[]
    i = 0
    while i < len(pStr):
        if pStr[i] == '/' or pStr[i] == DELIM_PRONUN:
            unrolled.append([-1])
            i += 1
        else:
            start  = CHOSUNG_LIST.index(pStr[i])
            middle = JUNGSUNG_LIST.index(pStr[i+1])
            end    = JONGSUNG_LIST.index(pStr[i+2])
            unrolled.append([start, middle, end])
            i += 3

    return unrolled

def toHangul(pStr):

    unrolled = toUnrolled(pStr)

    outputText = ''
    for syllable in unrolled:
        if len(syllable) == 3:
            outputText += build(syllable[0], syllable[1], syllable[2])
        else:
            outputText +=  ' '

    return outputText


def effSyllable(_in, option=0):
    pStr = _in
    if option == 1: # _in is hangul
        pStr = toPhonemeString(_in)

    idx=0
    count=0
    result=''
    for syllable in pStr:
        sLoc = idx % 3  # 0: CHOSUNG, 1: JUNGSUNG 2: JUNGSUNG
        idx+=1
        if syllable == 'ㅇ' and sLoc == 0:
            continue
        elif syllable == '_' and sLoc == 2:
            continue
        else:
            count+=1
            result+=syllable
    return count, result


def pronun2psymbol(pronun):
    i = 0
    result = ''
    if pronun == '':
        return 'SIL'
    for syllable in pronun:
        if syllable == ' ':
            continue
        elif syllable == '+':
            result += ' + '
            continue

        sLoc = i % 3
        i += 1
        if   sLoc == 0: result += CHOSUNG_SYM[CHOSUNG_LIST.index(syllable)]+' '
        elif sLoc == 1: result += JUNGSUNG_SYM[JUNGSUNG_LIST.index(syllable)]+' '
        else:           result += JONGSUNG_SYM[JONGSUNG_LIST.index(syllable)]+' '

        result = re.sub('(\ )+', ' ', result)
    return result.strip()


#
# Follows Korean Pronunciation Standard
#
def pString2Pronun(pStr):

    mecab = Mecab()
    pronounces = []
    nStr = pStr
    tStr = ''

    # 5항 --------------------------------------------------------- 
    rule = re.compile('[ㅈㅉㅊ][ㅕ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            tmpList[match[0]+1] = 'ㅓ'
        nStr = "".join(tmpList)

    rule = re.compile('[^ㅇㄹ][ㅖ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            tmpList[match[0]+1] = 'ㅔ'
        nStr = "".join(tmpList)
        #nStr += DELIM_PRONUN + tStr

    rule = re.compile('[^ㅇ][ㅢ][_]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            tmpList[match[0]+1] = 'ㅣ'
        nStr = "".join(tmpList)

    rule = re.compile('[^ ][ㅇ][ㅢ][_][^ ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            tmpList[match[0]+2] = 'ㅣ'
        nStr = "".join(tmpList)
        #nStr += DELIM_PRONUN + tStr

    rule = re.compile('[ㅇ][ㅢ][_]([ /\n]|$)')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            tmpList[match[0]+1] = 'ㅔ'
        nStr = "".join(tmpList)
        #nStr += DELIM_PRONUN + tStr

    # 8 항 -------------------------------------------------------
    # 받침소리: ㄱ,ㄴ,ㄷ,ㄹ,ㅁ,ㅂ,ㅇ (7개)

    # 9항 (받침 대표음)  ------------------------------------------------
    #   받침 ‘ㄲ, ㅋ’, ‘ㅅ, ㅆ, ㅈ, ㅊ, ㅌ’, ‘ㅍ’은 어말 또는 자음 앞에서 
    #   각각 대표음 [ㄱ, ㄷ, ㅂ]으로 발음한다
    #
    # 자음 ㅇ, ㅎ 경우는 뒤에서 따로  정의함
    #rule = re.compile('[ㄲㅋ]($|[ /\n]|[ㄱ-ㅆㅈ-ㅍ])')
    rule = re.compile('[ㄲㅋ]($|[ /\n]|[ㄱ-ㅆㅈ-ㅎ])')   # 12항에 추가해야 할지 검토 필요
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            tmpList[match[0]] = 'ㄱ'
        nStr = "".join(tmpList)

    rule = re.compile('[ㅅㅆㅈㅊㅌ]($|[ /\n]|[ㄱ-ㅆㅈ-ㅍ])')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            tmpList[match[0]] = 'ㄷ'
        nStr = "".join(tmpList)

    rule = re.compile('[ㅍ]($|[ /\n]|[ㄱ-ㅆㅈ-ㅍ])')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            tmpList[match[0]] = 'ㅂ'
        nStr = "".join(tmpList)

    # 10 항 -------------------------------------------------------
    #   겹받침 ‘ㄳ’, ‘ㄵ’, ‘ㄼ, ㄽ, ㄾ’, ‘ㅄ’은 어말 또는 자음 앞에서 
    #   각각 [ㄱ, ㄴ, ㄹ, ㅂ]으로 발음한다
    #
    # 자음 ㅇ, ㅎ 경우는 뒤에서 따로  정의함
    rule = re.compile('[ㄳㄵㅄㄽㄾ]($|[ /\n]|[ㄱ-ㅆㅈ-ㅍ])')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            if tmpList[match[0]] == 'ㄳ':
                tmpList[match[0]] = 'ㄱ'
            elif tmpList[match[0]] == 'ㄵ':
                tmpList[match[0]] = 'ㄴ'
            elif tmpList[match[0]] == 'ㅄ':
                tmpList[match[0]] = 'ㅂ'
            else:
                tmpList[match[0]] = 'ㄹ'
        nStr = "".join(tmpList)

    # [추가] 실제로 사람들이 두 가지를 혼용
    rule = re.compile('[ㄼ]($|[ /\n]|[ㄱ-ㅆㅈ-ㅍ])')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList  = list(nStr)
        tmpList2 = list(nStr)
        for match in matches:
            tmpList[match[0]]  = 'ㄹ'
            tmpList2[match[0]] = 'ㅂ'
        #nStr = "".join(tmpList) + DELIM_PRONUN + "".join(tmpList2)
        nStr = "".join(tmpList)

    # 11 항 -------------------------------------------------------
    #   겹받침 ‘ㄺ, ㄻ, ㄿ’은 어말 또는 자음 앞에서 
    #   각각 [ㄱ, ㅁ, ㅂ]으로 발음한다.
    #
    # 겹받침의 경우 뒤에 ㅇ, ㅎ에 따라 달라질 수 있음 
    rule = re.compile('[ㄺㄻㄿ]($|[ /\n]|[ㄱ-ㅆㅈ-ㅍ])')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            if tmpList[match[0]] == 'ㄺ':
                tmpList[match[0]] = 'ㄱ'
            elif tmpList[match[0]] == 'ㄻ':
                tmpList[match[0]] = 'ㅁ'
            else:
                tmpList[match[0]] = 'ㅂ'
        nStr = "".join(tmpList)

    # 12 항 -------------------------------------------------------
    # 받침 ㅎ 
    #  1. ‘ㅎ(ㄶ, ㅀ)’ 뒤에 ‘ㄱ, ㄷ, ㅈ’이 결합되는 경우에는, 
    #     뒤 음절 첫소리와 합쳐서 [ㅋ, ㅌ, ㅊ]으로 발음한다.
    #       [붙임 1] 받침 ‘ㄱ(ㄺ), ㄷ, ㅂ(ㄼ), ㅈ(ㄵ)’이 뒤 음절 첫소리 
    #                ‘ㅎ’과 결합되는 경우에도, 역시 두 음을 합쳐서
    #                [ㅋ, ㅌ, ㅍ, ㅊ]으로 발음한다.
    #       [붙임 2] 규정에 따라 [ㄷ]으로 발음되는 ‘ㅅ, ㅈ, ㅊ, ㅌ’의 
    #                경우에도 이에 준한다.
    #  2. ‘ㅎ(ㄶ, ㅀ)’ 뒤에 ‘ㅅ’이 결합되는 경우에는, ‘ㅅ’을 [ㅆ]으로 발음한다
    #  3. ‘ㅎ’ 뒤에 ‘ㄴ’이 결합되는 경우에는, [ㄴ]으로 발음한다.
    #       [붙임] ‘ㄶ, ㅀ’ 뒤에 ‘ㄴ’이 결합되는 경우에는, ‘ㅎ’을 발음하지 않는다
    #  4. ‘ㅎ(ㄶ, ㅀ)’ 뒤에 모음으로 시작된 어미나 접미사가 결합되는 경우에는
    #     ‘ㅎ’을 발음하지 않는다.
    rule = re.compile('[ㅎㄶㅀ][ㄱㄷㅈ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            if tmpList[match[0]] == 'ㅎ':
                tmpList[match[0]] = SYM_NOSOUND
            elif tmpList[match[0]] == 'ㄶ':
                tmpList[match[0]] = 'ㄴ'
            else:
                tmpList[match[0]] = 'ㄹ'

            if tmpList[match[0]+1] == 'ㄱ':
                tmpList[match[0]+1] = 'ㅋ'
            elif tmpList[match[0]+1] == 'ㄷ':
                tmpList[match[0]+1] = 'ㅌ'
            else:
                tmpList[match[0]+1] = 'ㅊ'

        nStr = "".join(tmpList)

    rule = re.compile('[ㄱㄺㄷㅂㄼㅈㄵ][ㅎ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            if tmpList[match[0]] == 'ㄱ':
                tmpList[match[0]]   = SYM_NOSOUND
                tmpList[match[0]+1] = 'ㅋ'
            elif tmpList[match[0]] == 'ㄺ':
                tmpList[match[0]]   = 'ㄹ'
                tmpList[match[0]+1] = 'ㅋ'
            elif tmpList[match[0]] == 'ㄷ':
                tmpList[match[0]]   = SYM_NOSOUND
                tmpList[match[0]+1] = 'ㅌ'
            elif tmpList[match[0]] == 'ㅂ':
                tmpList[match[0]]   = SYM_NOSOUND
                tmpList[match[0]+1] = 'ㅍ'
            elif tmpList[match[0]] == 'ㄼ':
                tmpList[match[0]]   = 'ㄹ'
                tmpList[match[0]+1] = 'ㅍ'
            elif tmpList[match[0]] == 'ㅈ':
                tmpList[match[0]]   = SYM_NOSOUND
                tmpList[match[0]+1] = 'ㅊ'
            else:
                tmpList[match[0]]   = 'ㄴ'
                tmpList[match[0]+1] = 'ㅊ'
        nStr = "".join(tmpList)

    rule = re.compile('[ㅅㅈㅊㅌ][ㅎ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            tmpList[match[0]]   = SYM_NOSOUND
            tmpList[match[0]+1] = 'ㅌ'
        nStr = "".join(tmpList)

    rule = re.compile('[ㅎㄶㅀ][ㅅ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            if tmpList[match[0]] == 'ㅎ':
                tmpList[match[0]]   = SYM_NOSOUND
                tmpList[match[0]+1] = 'ㅆ'
            elif tmpList[match[0]] == 'ㄶ':
                tmpList[match[0]]   = 'ㄴ'
                tmpList[match[0]+1] = 'ㅆ'
            else:
                tmpList[match[0]]   = 'ㄹ'
                tmpList[match[0]+1] = 'ㅆ'
        nStr = "".join(tmpList)

    # 모음으로 시작하는 어미나 접미사 ... 고려하지 않음  
    rule = re.compile('[ㅎㄶㅀ][ㄴㅇ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            if tmpList[match[0]+1] == 'ㄴ':
                if tmpList[match[0]] == 'ㅀ':
                    tmpList[match[0]] = 'ㄹ'
                else:
                    tmpList[match[0]] = 'ㄴ'
            else:
                if tmpList[match[0]] == 'ㅀ':
                    tmpList[match[0]]   = SYM_NOSOUND
                    tmpList[match[0]+1] = 'ㄹ'
                elif tmpList[match[0]] == 'ㄶ':
                    tmpList[match[0]]   = SYM_NOSOUND
                    tmpList[match[0]+1] = 'ㄴ'
                else:
                    tmpList[match[0]] = SYM_NOSOUND
        nStr = "".join(tmpList)

    # 17 항 ---------------------------------------------------------
    # 구개음화
    #   받침 ‘ㄷ, ㅌ(ㄾ)’이 조사나 접미사의 모음 ‘ㅣ’와 결합되는 경우에는, 
    #   [ㅈ, ㅊ]으로 바꾸어서 뒤 음절 첫소리로 옮겨 발음한다.
    #       [붙임] ‘ㄷ’ 뒤에 접미사 ‘히’가 결합되어 ‘티’를 이루는 것은
    #              [치]로 발음한다
    rule = re.compile('[ㄷㅌㄾ][ㅇ][ㅣ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            if tmpList[match[0]] == 'ㄷ':
                tmpList[match[0]]    = SYM_NOSOUND
                tmpList[match[0]+1]  = 'ㅈ'
            elif tmpList[match[0]] == 'ㅌ':
                tmpList[match[0]]    = SYM_NOSOUND
                tmpList[match[0]+1]  = 'ㅊ'
            else:
                tmpList[match[0]]    = 'ㄹ'
                tmpList[match[0]+1]  = 'ㅊ'
        nStr = "".join(tmpList)

    # 12 항이 미리 적용된 예외 처리, 예) 묻히다[무티다->무치다]
    rule = re.compile('[ㄷ][ㅎ][ㅣ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(pStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            tmpList[match[0]+1] = 'ㅊ'
        nStr = "".join(tmpList)

    # 19 항----------------------------------------------------------
    # 붙임) 적용을 위해 18항보다 앞서서 처리
    #   예) 법리[법니] --> [범니] 
    #
    # >> 실제 사용할 때는 ㄹ이 꼭 ㄴ으로 바뀌지는 않는다
    rule = re.compile('[ㅁㅇㄱㅂ][ㄹ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            tmpList[match[0]+1] = 'ㄴ'
        nStr = "".join(tmpList)
        #nStr += DELIM_PRONUN + tStr

    # 18 항----------------------------------------------------------
    rule = re.compile('[ㄱㄷㅂ][ㄴㅁ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            if   tmpList[match[0]] == 'ㄱ':
                tmpList[match[0]] = 'ㅇ'
            elif tmpList[match[0]] == 'ㄷ':
                tmpList[match[0]] = 'ㄴ'
            else:
                tmpList[match[0]] = 'ㅁ'
        nStr = "".join(tmpList)

    # 20 항----------------------------------------------------------
    #   ‘ㄴ’은 ‘ㄹ’의 앞이나 뒤에서 [ㄹ]로 발음한다
    #
    # >> 경험상 보이는데로 있는 경우도 많은 것 같음 
    rule = re.compile('[ㄴ][ㄹ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            tmpList[match[0]] = 'ㄹ'
        nStr = "".join(tmpList)
        #nStr += DELIM_PRONUN + tStr

    rule = re.compile('[ㄹ][ㄴ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            tmpList[match[0]+1] = 'ㄹ'
        nStr = "".join(tmpList)
        #nStr += DELIM_PRONUN + tStr

    # 21 항 (인정되지 않는 자음동화) --------------------------------
    # 음성인식에는 있는 편이 낫다고 생각됨
    # TBD

    # 22 항 ---------------------------------------------------------
    #   용언의 어미는 [어]로 발음함을 원칙으로 하되, [여]로 발음함도 허용한다
    #
    # >> reg. expr. 이 용언 '의'가 아닌 것을 찾을 경우, 대응필요 
    rule = re.compile('[_][ㅇ][ㅓ][_]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            tmpList[match[0]+2] = 'ㅕ'
        nStr = "".join(tmpList)
        #nStr += DELIM_PRONUN + tStr

    # 23항 ----------------------------------------------------------
    # 된소리
    #   받침 ‘ㄱ(ㄲ, ㅋ, ㄳ, ㄺ), ㄷ(ㅅ, ㅆ, ㅈ, ㅊ, ㅌ), ㅂ(ㅍ, ㄼ, ㄿ, ㅄ)’ 
    #   뒤에 연결되는 ‘ㄱ, ㄷ, ㅂ, ㅅ, ㅈ’은 된소리로 발음한다.
    rule = re.compile('[ㄱㄷㅂ][ㄱㄷㅂㅅㅈ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            if   tmpList[match[0]+1] == 'ㄱ':
                tmpList[match[0]+1] = 'ㄲ'
            elif tmpList[match[0]+1] == 'ㄷ':
                tmpList[match[0]+1] = 'ㄸ'
            elif tmpList[match[0]+1] == 'ㅂ':
                tmpList[match[0]+1] = 'ㅃ'
            elif tmpList[match[0]+1] == 'ㅅ':
                tmpList[match[0]+1] = 'ㅆ'
            else: # 'ㅈ'
                tmpList[match[0]+1] = 'ㅉ'
        nStr = "".join(tmpList)


    # 24항 ----------------------------------------------------------
    # 된소리
    #   어간 받침 ‘ㄴ(ㄵ), ㅁ(ㄻ)’ 뒤에 결합되는 어미의 첫소리 
    #   ‘ㄱ, ㄷ, ㅅ, ㅈ’은 된소리로 발음한다
    rule = re.compile('[ㄴㅁ][ㄱㄷㅅㅈ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        posTags = mecab.pos(toHangul(pStr))
        isURMIE=False
        for match in matches:
            for morph, posTag in posTags:
                if toHangul(pStr[match[0]+1:match[0]+4]) ==  morph[0]:
                    if posTag in URMIE:
                        isURMIE=True
            if isURMIE:
                #for match in matches:
                if   tmpList[match[0]+1] == 'ㄱ':
                    if tmpList[match[0]+2] != 'ㅣ':
                        tmpList[match[0]+1] = 'ㄲ'
                elif tmpList[match[0]+1] == 'ㄷ':
                    tmpList[match[0]+1] = 'ㄸ'
                elif tmpList[match[0]+1] == 'ㅅ':
                    tmpList[match[0]+1] = 'ㅆ'
                else: # 'ㅈ'
                    tmpList[match[0]+1] = 'ㅉ'
        nStr = "".join(tmpList)

    # 25항 ----------------------------------------------------------
    #   어간 받침 ‘ㄼ, ㄾ’ 뒤에 결합되는 어미의 첫소리 ‘ㄱ, ㄷ, ㅅ, ㅈ’은 
    #   된소리로 발음한다
    # 
    # >> 된소리, 대표음으로 자음이 바뀌기 전에 된소리 적용!
    rule = re.compile('[ㄼㄾ][ㄱㄷㅅㅈ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(pStr)]  # pStr!!
    if matches:
        tmpList = list(nStr)
        posTags = mecab.pos(toHangul(pStr))
        isURMIE=False
        for match in matches:
            for morph, posTag in posTags:
                if toHangul(pStr[match[0]+1:match[0]+4]) ==  morph[0]:
                    if posTag in URMIE:
                        isURMIE=True
            if isURMIE:
                #for match in matches:
                if   tmpList[match[0]+1] == 'ㄱ':
                    if tmpList[match[0]+2] != 'ㅣ':
                        tmpList[match[0]+1] = 'ㄲ'
                elif tmpList[match[0]+1] == 'ㄷ':
                    tmpList[match[0]+1] = 'ㄸ'
                elif tmpList[match[0]+1] == 'ㅅ':
                    tmpList[match[0]+1] = 'ㅆ'
                else: # 'ㅈ'
                    tmpList[match[0]+1] = 'ㅉ'
        nStr = "".join(tmpList)

    # 26항 ---- 정해진 법칙이라하기 어려움 --------------------------

    # 27항 ----------------------------------------------------------
    #  관형사형 ‘-(으)ㄹ’ 뒤에 연결되는 ‘ㄱ, ㄷ, ㅂ, ㅅ, ㅈ’은 
    # 된소리로 발음한다
    rule = re.compile('([ㄱ-ㅎ])([ㅏ-ㅣ])(ㄹ)[ㄱㄷㅂㅅㅈ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        posTags = mecab.pos(toHangul(pStr))
        isURMIE=False
        for match in matches:
            for morph, posTag in posTags:
                if toHangul(pStr[match[0]:match[0]+3]) in  morph:
                    if posTag.split('+')[-1] in URMIE:
                        isURMIE=True
            if isURMIE:
                #for match in matches:
                if   tmpList[match[0]+3] == 'ㄱ':
                    tmpList[match[0]+3] = 'ㄲ'
                elif tmpList[match[0]+3] == 'ㄷ':
                    tmpList[match[0]+3] = 'ㄸ'
                elif tmpList[match[0]+3] == 'ㅂ':
                    tmpList[match[0]+3] = 'ㅃ'
                elif tmpList[match[0]+3] == 'ㅅ':
                    tmpList[match[0]+3] = 'ㅆ'
                else: # 'ㅈ'
                    tmpList[match[0]+3] = 'ㅉ'
        nStr = "".join(tmpList)

    # 28장 
    #   기본적으로 된소리로 됨... 어색한 경우 수정이 필요할 수 있음

    ## 29장 ---------------------------------------------------------
    ##   합성어 및 파생어에서, 앞 단어나 접두사의 끝이 자음이고 뒤 단어나 
    ##   접미사의 첫음절이 ‘이, 야, 여, 요, 유’인 경우에는, ‘ㄴ’ 음을 첨가하여 
    ##   [니, 냐, 녀, 뇨, 뉴]로 발음한다
    ##
    ## >> 자음동화, 연음은 이후처리해야 ... 
    ## >> 합성어 파생어 구분 필요한지 검토 ... 
    #rule = re.compile('[ㄱ-ㅍ][ㅇ][ㅣㅑㅕㅛㅠ]')
    #matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    #if matches:
    #    tmpList = list(nStr)
    #    posTags = mecab.pos(toHangul(pStr))
    #    #print(pStr)
    #    #print(posTags)
    #    for match in matches:
    #        # 합성어, 파생어  판단 
    #        isEFFMORF=False
    #        for morph, posTag in posTags:
    #            #if toHangul(pStr[match[0]+1:match[0]+4]) in morph:
    #            if toHangul(pStr[match[0]+1:match[0]+4]) ==  morph[0]:
    #                if posTag in EFFMORF:
    #                    isEFFMORF=True
    #        #print(toHangul(pStr[match[0]+1:match[0]+4]), isEFFMORF)

    #        if isEFFMORF:
    #            if tmpList[match[0]] == 'ㄹ':
    #                tmpList[match[0]+1] = 'ㄹ'
    #            else:
    #                tmpList[match[0]+1] = 'ㄴ'

    #    nStr = "".join(tmpList)
    #    #print(nStr)
    #    #nStr += DELIM_PRONUN + tStr

    ## 30 장 --------------------------------------------------------
    #   1. ‘ㄱ, ㄷ, ㅂ, ㅅ, ㅈ’으로 시작하는 단어 앞에 사이시옷이 올 때는 
    #   이들 자음만을 된소리로 발음하는 것을 원칙으로 하되, 사이시옷을 
    #   [ㄷ]으로 발음하는 것도 허용한다.
    #
    #   2. 사이시옷 뒤에 ‘ㄴ, ㅁ’이 결합되는 경우에는 [ㄴ]으로 발음한다
    #
    # >> 상기 두가지는 앞서 적용된 룰로 모두 자동 적용 됨
    #
    #   3. 사이시옷 뒤에 ‘이’ 음이 결합되는 경우에는 [ㄴㄴ]으로 발음한다.
    rule = re.compile('[ㅅ][ㄴ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            tmpList[match[0]] = 'ㄴ'
        nStr = "".join(tmpList)


    ## 15 항 (홑받침은 9 장에 통합)-----------------------------------
    #   받침 뒤에 모음 ‘ㅏ, ㅓ, ㅗ, ㅜ, ㅟ’들로 시작되는 실질 형태소가 
    #   연결되는 경우에는, 대표음으로 바꾸어서 뒤 음절 첫소리로 옮겨 발음한다
    # >> 실질형태소란...  명사, 동사, 형용사, 부사
    # >> 연음 적용전 대표받침으로 전환 
    #rule = re.compile('[ㄱㄴㄷㄹㅁㅂㅅㅈㅊㅋㅌㅍㄲㅆ][ㅇ]')
    rule = re.compile('[ㄱㄴㄷㄹㅁㅂㅅㅈㅊㅋㅌㅍㅆ][ㅇ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        posTags = mecab.pos(toHangul(pStr))

        isEFFMORF=False
        for match in matches:
            # 실질 형태소인지 판단 ... but 틀리는 경우가 많음
            # 덮이다[더피다] --> [더비다]로 되고 있음 
            for morph, posTag in posTags:
                if toHangul(pStr[match[0]+1:match[0]+4]) in morph:
                    if posTag in EFFMORF:
                        isEFFMORF=True
            if isEFFMORF:
                # 대표음
                if tmpList[match[0]] in ['ㅅ', 'ㅆ', 'ㅈ', 'ㅊ', 'ㅌ']:
                    tmpList[match[0]] = 'ㄷ'
                elif tmpList[match[0]] in ['ㄲ', 'ㅋ']:
                    tmpList[match[0]] = 'ㄱ'
                elif tmpList[match[0]] == 'ㅍ':
                    tmpList[match[0]] = 'ㅂ'
                else:
                    tmpList[match[0]+1] = tmpList[match[0]]
                    tmpList[match[0]]   = SYM_NOSOUND
        nStr = "".join(tmpList)

    rule = re.compile('[ㄳㄺㄵㄼㄽㄾㄻㄿㅄ][ㅇ]')  # 9개(ㄶ,ㅀ 제외)
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        posTags = mecab.pos(toHangul(pStr))

        isEFFMORF=False
        for match in matches:
            # 실질 형태소인지 판단 ... but 틀리는 경우가 많음
            # 덮이다[더피다] --> [더비다]로 되고 있음 
            for morph, posTag in posTags:
                if toHangul(pStr[match[0]+1:match[0]+4]) in morph:
                    if posTag in EFFMORF:
                        isEFFMORF=True
            if isEFFMORF:
                # 대표음
                if tmpList[match[0]] in ['ㄳ','ㄺ']:
                    tmpList[match[0]] = 'ㄱ'
                elif tmpList[match[0]] == 'ㄵ':
                    tmpList[match[0]] = 'ㄴ'
                elif tmpList[match[0]] in ['ㄼ','ㄽ','ㄾ']:
                    tmpList[match[0]] = 'ㄹ'
                elif tmpList[match[0]] == 'ㄻ':
                    tmpList[match[0]] = 'ㅁ'
                elif tmpList[match[0]] in ['ㄿ','ㅄ']:
                    tmpList[match[0]] = 'ㅂ'
                else:
                    tmpList[match[0]+1] = tmpList[match[0]]
                    tmpList[match[0]]   = SYM_NOSOUND
        nStr = "".join(tmpList)

    # 연음적용하기 
    # 13 항 --------------------------------------------------------
    # 연음
    #   홑받침이나 쌍받침이 모음으로 시작된 조사나 어미, 접미사와 결합되는 경우에는, 
    #   제 음가대로 뒤 음절 첫소리로 옮겨 발음한다.
    # 
    # >> 15항의 실질형태소에 의한 대표음이 미리 적용되었다고 가정
    # >> 조사, 어미, 접미사 판단필요 없어보임 
    rule = re.compile('[ㄱㄴㄷㄹㅁㅂㅅㅈㅊㅋㅌㅍㄲㅆ][ㅇ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            tmpList[match[0]+1] = tmpList[match[0]]
            tmpList[match[0]]   = SYM_NOSOUND
        nStr = "".join(tmpList)

    # 14 항 -------------------------------------------------------
    # 연음
    # 겹받침
    rule = re.compile('[ㄳㄵㄶㄺㄻㄼㄽㄾㄿㅀㅄ][ㅇ]')
    matches = [(m.start(0), m.end(0)) for m in rule.finditer(nStr)]
    if matches:
        tmpList = list(nStr)
        for match in matches:
            if   tmpList[match[0]] == 'ㄳ':
                tmpList[match[0]]   = 'ㄱ'
                tmpList[match[0]+1] = 'ㅆ'
            elif tmpList[match[0]] == 'ㄵ':
                tmpList[match[0]]   = 'ㄴ'
                tmpList[match[0]+1] = 'ㅈ'
            elif tmpList[match[0]] == 'ㄺ':
                tmpList[match[0]]   = 'ㄹ'
                tmpList[match[0]+1] = 'ㄱ'
            elif tmpList[match[0]] == 'ㄻ':
                tmpList[match[0]]   = 'ㄹ'
                tmpList[match[0]+1] = 'ㅁ'
            elif tmpList[match[0]] == 'ㄼ':
                tmpList[match[0]]   = 'ㄹ'
                tmpList[match[0]+1] = 'ㅂ'
            elif tmpList[match[0]] == 'ㄽ':
                tmpList[match[0]]   = 'ㄹ'
                tmpList[match[0]+1] = 'ㅆ'
            elif tmpList[match[0]] == 'ㄾ':
                tmpList[match[0]]   = 'ㄹ'
                tmpList[match[0]+1] = 'ㅌ'
            elif tmpList[match[0]] == 'ㄿ':
                tmpList[match[0]]   = 'ㄹ'
                tmpList[match[0]+1] = 'ㅍ'
            else: #ㅄ
                tmpList[match[0]]   = 'ㅂ'
                tmpList[match[0]+1] = 'ㅆ'
        nStr = "".join(tmpList)

    # 16 항 한글자모의 받침소리, 인식용으로 쓰일 것 같지 않음 -------


    return nStr

ALPH = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','&']
ALPH2KOR = ['에이','비','씨','디','이','에프','지','에이치','아이','제이','케이',
        '엘','엠','엔','오','피','큐','알','에스','티','유','브이','더블유','엑스','와이','제트','엔']

NUM     = ['0','1','2','3','4','5','6','7','8','9']
NUM2KOR = ['제로','원','투','쓰리','포','파이브','씩스','쎄븐','에잍','나인']

def convAlphabet(match):
    ch = match.group(1).lower()
    kor = ''
    for alpha in ch:
        if alpha in ALPH:
            kor += ALPH2KOR[ALPH.index(alpha)]
        else:
            kor += alpha
    return kor

def convNumber(match):
    ch = match.group(1)
    kor = ''
    for num in ch:
        if num in NUM:
            kor += NUM2KOR[NUM.index(num)]
        else:
            kor += num
    return kor

def converrtVocab2Pronounce():

    with open('dic.pronun', 'w') as f:
        #print('Vocab\tPronunciations', file=f)

        nLine=1
        for line in fileinput.input():
            if nLine%500 == 0:
                print('  %d line processed' %(nLine), end='\r', file=sys.stderr)
                sys.stderr.flush()
            nLine+=1

            if line.strip() == '+pause+':
                print(line.strip(), file=f)
                continue
            
            line_=line
            
            ## for English Capital letters
            #line_ = re.sub('([A-Z&]+)', convAlphabet, line)
            #line_ = re.sub('([0-9]+)', convNumber, line_)
            tmp = line.split('\t')
            flag = False
            if len(tmp) == 2:
                flag = True
                line_ = tmp[1]

            # convert input into pronunciation
            tline = re.sub('([ +])', '', line_)
            pStr = toPhonemeString(tline)
            pronun = pString2Pronun(pStr)

            # seperate pronunciation into each morpheme
            hPronun = toHangul(pronun)

            tline  = re.sub('[ ]', '', line_)
            morphs = tline.split('+')
            idx   = 0
            tList  = []
            tList2 = []
            for morph in morphs:
                morph_p = hPronun[idx:idx+len(morph)]
                idx    += len(morph)
                tList.append(toPhonemeString(morph))
                tList2.append(toPhonemeString(morph_p))

            # 뒷부분의 변화를 앞단어 쪽으로 옮김
            for i in range(len(tList)):
                if i == 0: continue

                if tList[i][0] == 'ㅇ' and tList2[i][0] != 'ㅇ':
                    if tList[i-1][-1] != '_' and tList2[i-1][-1] == '_':
                        tList2[i-1] += tList2[i][0]
                        tList2[i] = tList2[i][1:]

                if tList[i][0] == 'ㅎ' and tList2[i][0] != 'ㅎ':
                    if tList[i-1][-1] != '_' and tList2[i-1][-1] == '_':
                        tList2[i-1] += tList2[i][0]
                        tList2[i] = tList2[i][1:]

            tStr2 = " + ".join(tList2)

            # Outputs
            if flag:
                print(line.split('\t')[0].strip(), end='\t', file=f)
            else:
                print(line.strip(), end='\t', file=f)
            #print(hPronun, end='\t', file=f)
            #print(tStr2,file=f)
            #print(tStr2, end='\t',file=f)
            print(pronun2psymbol(tStr2), file=f)
        
        print('  %d line processed' %(nLine), file=sys.stderr)

if __name__ == '__main__':
    converrtVocab2Pronounce()

