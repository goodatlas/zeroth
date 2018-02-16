#
# Copyright  2017  Atlas Guide (Author : Lucas Jo)
#
# Apache 2.0
# 
import unicodedata
import re

measureUnits = "".join(chr(i) for i in range(0xffff) if i >= 0x3380 and i<=0x33DD)
percents = ''.join(chr(i) for i in range(0xffff) \
        if unicodedata.category(chr(i)) == 'Po' and re.search('PERCENT', unicodedata.name(chr(i))))
currencies = "".join(chr(i) for i in range(0xffff) if unicodedata.category(chr(i)) == 'Sc')
quatation = ''.join(chr(i) for i in range(0xffff) if unicodedata.category(chr(i)) in ['Pc', 'Pd', 'Pe', 'Pf', 'Pi',
    'Po', 'Ps'] and re.search('QUOTATION', unicodedata.name(chr(i))))
apostrophe = ''.join(chr(i) for i in range(0xffff) if unicodedata.category(chr(i)) in ['Pc', 'Pd', 'Pe', 'Pf', 'Pi',
    'Po', 'Ps'] and re.search('APOSTROPHE', unicodedata.name(chr(i))))
userDefines = "-~+=%/:;"
puctuations = ".,?!'"

triangles = ''.join(chr(i) for i in range(0xffff) if unicodedata.category(chr(i)) == 'So'
        and re.search(' TRIANGLE\\b', unicodedata.name(chr(i))))
circles = ''.join(chr(i) for i in range(0xffff) if unicodedata.category(chr(i)) == 'So'
        and re.search(' CIRCLE\\b', unicodedata.name(chr(i))))
squares = ''.join(chr(i) for i in range(0xffff) if unicodedata.category(chr(i)) == 'So'
        and re.search(' SQUARE\\b', unicodedata.name(chr(i))))

separators = triangles + circles + squares
valids = measureUnits + percents + currencies + userDefines + puctuations
invalids_chars = r"[^ \n가-힣0-9a-zA-Z" + re.escape(valids) + r"]+"
valids_chars = r"[ \n가-힣0-9a-zA-Z" + re.escape(valids) + r"]+"

chinese = re.compile(u'[⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎]', re.UNICODE)

#3000-303F : punctuation
#3040-309F : hiragana
#30A0-30FF : katakana
#FF00-FFEF : Full-width roman + half-width katakana
#4E00-9FAF : Common and uncommon kanji
japanese = re.compile(u'[\u3040-\u309f\u30a0-\u30ff\uff00-\uffef\u4e00-\u9faf]', re.UNICODE)

userDefines_pronun={
        '-': ['마이너스', '에서', '다시'],
        '~': ['에서', '부터'],
        '+': ['더하기', '플러스'],
        #'=': ['는', '은', '이콜'],
        '%': ['퍼센트', '프로', '퍼센티지'],
        '/': ['나누기', '퍼', '슬래쉬'],
}

measureUnits_pronun = {
        '㎀': ['피코 암페어'],
        '㎁': ['나노 암페어'],
        '㎂': ['마이크로 암페어'],
        '㎃': ['밀리 암페어'],
        '㎄': ['킬로 암페어'],
        '㎅': ['킬로 바이트'],
        '㎆': ['메가 바이트'],
        '㎇': ['기가 바이트'],
        '㎈': ['칼로리'],
        '㎉': ['킬로 칼로리'],
        '㎊': ['피코 페럿'],
        '㎋': ['나노 페럿'],
        '㎌': ['마이크로 페럿'],
        '㎍': ['마이크로 그램'],
        '㎎': ['밀리 그램'],
        '㎏': ['킬로 그램'],
        '㎐': ['헤르츠'],
        '㎑': ['킬로 헤르츠'],
        '㎒': ['메가 헤르츠'],
        '㎓': ['기가 헤르츠'],
        '㎔': ['킬로 헤르츠'],
        '㎕': ['마이크로 리터'],
        '㎖': ['밀리 리터'],
        '㎗': ['데시 리터'],
        '㎘': ['킬로 리터'],
        '㎙': ['펨토 미터'],
        '㎚': ['나노 미터'],
        '㎛': ['마이크로 미터'],
        '㎜': ['밀리 미터'],
        '㎝': ['센티 미터'],
        '㎞': ['킬로 미터'],
        '㎟': ['제곱 밀리 미터'],
        '㎠': ['제곱 센티 미터'],
        '㎡': ['제곱 미터'],
        '㎢': ['제곱 킬로 미터'],
        '㎣': ['세 제곱 밀리 미터'],
        '㎤': ['세 제곱 센티 미터'],
        '㎥': ['세 제곱 미터'],
        '㎦': ['세 제곱 킬로 미터'],
        '㎧': ['미터 퍼 쎄크'],
        '㎨': ['미터 퍼 제곱 쎄그'],
        '㎩': ['파스칼'],
        '㎪': ['킬로 파스칼'],
        '㎫': ['메가 파스칼'],
        '㎬': ['기가 파스칼'],
        '㎭': ['라디안'],
        '㎮': ['라디안 퍼 쎄크'],
        '㎯': ['라디안 퍼 제곱 쎄크'],
        '㎰': ['피코 쎄크'],
        '㎱': ['나노 쎄크'],
        '㎲': ['마이크로 쎄크'],
        '㎳': ['밀리 쎄크'],
        '㎴': ['피코 볼트'],
        '㎵': ['나노 볼트'],
        '㎶': ['마이크로 볼트'],
        '㎷': ['밀리 볼트'],
        '㎸': ['킬로 볼트'],
        '㎹': ['메가 볼트'],
        '㎺': ['피코 와트'],
        '㎻': ['나노 와트'],
        '㎼': ['마이크로 와트'],
        '㎽': ['밀리 와트'],
        '㎾': ['킬로 와트'],
        '㎿': ['메가 와트'],
        '㏀': ['킬로 옴'],
        '㏁': ['메가 옴'],
        '㏂': ['오전'],
        '㏃': ['베크렐'],
        '㏄': ['씨씨'],
        '㏅': ['칸델라'],
        '㏆': ['쿨롱 퍼 킬로 그램'],
        '㏇': ['씨 오'],
        '㏈': ['데시 벨'],
        '㏉': ['그레이'],
        '㏊': ['헥타르'],
        '㏋': ['마력'],
        '㏌': ['인치'],
        '㏍': ['킬로 카이저'],
        '㏎': ['킬로 미터'],
        '㏏': ['킬로 톤'],
        '㏐': ['루멘'],
        '㏑': ['로그'],
        '㏒': ['로그'],
        '㏓': ['럭스'],
        '㏔': ['밀리 바'],
        '㏕': ['밀'],
        '㏖': ['몰'],
        '㏗': ['피 에이치'],
        '㏘': ['오후'],
        '㏙': ['피 피 엠'],
        '㏚': ['피 알'],
        '㏛': ['스테라디안'],
        '㏜': ['시버트'],
        '㏝': ['웨버']
}

currencies_pronun = {
        '$': ['달러'],
        '¢': ['센트'],
        '£': ['파운드'],
        '¤': ['화폐 표시'],
        '¥': ['엔'],
        '֏': ['드람'],
        '؋': ['아프가니'],
        '৲': ['루피 마크'],
        '৳': ['루피 싸인'],
        '৻': ['간다'],
        '૱': ['루피'],
        '௹': ['루피'],
        '฿': ['바트'],
        '៛': ['리엘'],
        '₠': ['유로'],
        '₡': ['콜론'],
        '₢': ['크루제이로'],
        '₣': ['프랑'],
        '₤': ['리라'],
        '₥': ['밀'],
        '₦': ['나이라'],
        '₧': ['페세타'],
        '₨': ['루피'],
        '₩': ['원'],
        '₪': ['세겔'],
        '₫': ['동'],
        '€': ['유로'],
        '₭': ['킵'],
        '₮': ['터그릭'],
        '₯': ['드라크마'],
        '₰': ['페니'],
        '₱': ['페소'],
        '₲': ['과라니'],
        '₳': ['오스트랄'],
        '₴': ['리브니아'],
        '₵': ['세디'],
        '₶': ['토르노'],
        '₷': ['스페스밀로'],
        '₸': ['텐지'],
        '₹': ['루피'],
        '₺': ['리라'],
        '₻': ['노르딕'],
        '₼': ['마네'],
        '₽': ['루블'],
        '₾': ['라리'],
        '꠸': ['루피'],
        '﷼': ['리알'],
        '﹩': ['달러'],
        '＄': ['달러'],
        '￠': ['센트'],
        '￡': ['파운드'],
        '￥': ['엔'],
        '￦': ['원']
}

# TBD
# extracted from the corpus
validChars={
        '℃': ['도', '도 섭씨', '도 씨'],
        '㈜': ['주', '주식회사'],
        'ρ': ['로'],
        'μ': ['뮤', '마이크로'],
        'µ': ['마이크로', '뮤'],
        'Ｗ': ['와트'],
}












































































if __name__ == '__main__':
    print(valids_chars)
