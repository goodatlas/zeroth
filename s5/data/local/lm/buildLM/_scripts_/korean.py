# -*- coding: utf-8 -*-
import abc
import sys
import copy
import collections
import re

reload(sys)
sys.setdefaultencoding('utf-8')


class Korean(object):
    unicode_base_code, unicode_onset_offset, unicode_nucleus_offset = 44032, 588, 28

    # 초성(19)
    phoneme_onset_list = [
        u'ㄱ', u'ㄲ', u'ㄴ', u'ㄷ',
        u'ㄸ', u'ㄹ', u'ㅁ', u'ㅂ',
        u'ㅃ', u'ㅅ', u'ㅆ', u'ㅇ',
        u'ㅈ', u'ㅉ', u'ㅊ', u'ㅋ',
        u'ㅌ', u'ㅍ', u'ㅎ']

    phoneme_onset_list_len = len(phoneme_onset_list)
    phoneme_onset_dict = {v: i for i, v in enumerate(phoneme_onset_list)}

    # 중성(21)
    phoneme_nucleus_list = [
        u'ㅏ', u'ㅐ', u'ㅑ', u'ㅒ',
        u'ㅓ', u'ㅔ', u'ㅕ', u'ㅖ',
        u'ㅗ', u'ㅘ', u'ㅙ', u'ㅚ',
        u'ㅛ', u'ㅜ', u'ㅝ', u'ㅞ',
        u'ㅟ', u'ㅠ', u'ㅡ', u'ㅢ',
        u'ㅣ']

    phoneme_nucleus_list_len = len(phoneme_nucleus_list)
    phoneme_nucleus_dict = {v: i for i, v in enumerate(phoneme_nucleus_list)}

    # 종성(28)
    phoneme_coda_list = [
        u' ', u'ㄱ', u'ㄲ', u'ㄳ',
        u'ㄴ', u'ㄵ', u'ㄶ', u'ㄷ',
        u'ㄹ', u'ㄺ', u'ㄻ', u'ㄼ',
        u'ㄽ', u'ㄾ', u'ㄿ', u'ㅀ',
        u'ㅁ', u'ㅂ', u'ㅄ', u'ㅅ',
        u'ㅆ', u'ㅇ', u'ㅈ', u'ㅊ',
        u'ㅋ', u'ㅌ', u'ㅍ', u'ㅎ']

    phoneme_coda_list_len = len(phoneme_coda_list)
    phoneme_coda_dict = {v: i for i, v in enumerate(phoneme_coda_list)}

    # 쌍자음/된소리
    phoneme_double_consonant_dict = {
        u'ㄲ': [u'ㄱ', u'ㄱ'], u'ㄳ': [u'ㄱ', u'ㅅ'],
        u'ㄵ': [u'ㄴ', u'ㅈ'], u'ㄶ': [u'ㄴ', u'ㅎ'],
        u'ㄸ': [u'ㄷ', u'ㄷ'],
        u'ㄺ': [u'ㄹ', u'ㄱ'], u'ㄻ': [u'ㄹ', u'ㅁ'],
        u'ㄼ': [u'ㄹ', u'ㅂ'], u'ㄽ': [u'ㄹ', u'ㅅ'],
        u'ㄾ': [u'ㄹ', u'ㅌ'], u'ㄿ': [u'ㄹ', u'ㅍ'], u'ㅀ': [u'ㄹ', u'ㅎ'],
        u'ㅃ': [u'ㅂ', u'ㅂ'], u'ㅄ': [u'ㅂ', u'ㅅ'],
        u'ㅆ': [u'ㅅ', u'ㅅ'],
        u'ㅉ': [u'ㅈ', u'ㅈ']
    }

    phoneme_lenis_to_fortis_dict = {
        u'ㄱ': u'ㄲ',
        u'ㄷ': u'ㄸ',
        u'ㅂ': u'ㅃ',
        u'ㅅ': u'ㅆ',
        u'ㅈ': u'ㅉ'
    }

    phoneme_lenis_to_asprite_dict = {
        u'ㄱ': u'ㅋ',
        u'ㄷ': u'ㅌ',
        u'ㅂ': u'ㅍ',
        u'ㅈ': u'ㅊ'
    }

    # 중성 발음 합성
    phoneme_nucleus_phonetic_combine_dict = {
        u'ㅣㅏ': u'ㅑ',
        u'ㅣㅓ': u'ㅕ',
        u'ㅣㅐ': u'ㅒ',
        u'ㅣㅔ': u'ㅖ',
        u'ㅣㅜ': u'ㅠ',
        u'ㅣㅗ': u'ㅛ',
        u'ㅡㅣ': u'ㅢ',
        u'ㅜㅣ': u'ㅟ',
        u'ㅜㅏ': u'ㅘ',
        u'ㅜㅓ': u'ㅝ',
        u'ㅜㅐ': u'ㅙ',
        u'ㅜㅔ': u'ㅞ',
        u'ㅗㅣ': u'ㅚ',
        u'ㅗㅏ': u'ㅘ',
        u'ㅗㅓ': u'ㅝ',
        u'ㅗㅐ': u'ㅙ',
        u'ㅗㅔ': u'ㅞ'
    }

    # 중성 합성
    phoneme_nucleus_combine_dict = {
        u'ㅡ+ㅣ': u'ㅢ',
        u'ㅜ+ㅣ': u'ㅟ',
        u'ㅜ+ㅓ': u'ㅝ',
        u'ㅜ+ㅔ': u'ㅞ',
        u'ㅗ+ㅣ': u'ㅚ',
        u'ㅗ+ㅏ': u'ㅘ',
        u'ㅗ+ㅐ': u'ㅙ',
    }

    # 문자셋
    phoneme_set = set(phoneme_onset_list + phoneme_nucleus_list + phoneme_coda_list)

    text = None
    character_list = None

    # Exceptions
    class TypeErrorException(Exception):
        pass

    class SyllableFailedException(Exception):
        pass

    # Filters
    class Filter(object):
        __metaclass__ = abc.ABCMeta

        def pre(self, sequence):
            pass

        def post(self, sequence):
            pass

        @abc.abstractmethod
        def do(self, sequence, character, index):
            pass

    # Syllable
    class Syllable(object):
        letter = None
        phoneme_onset = None
        phoneme_nucleus = None
        phoneme_coda = None

        def __init__(self, **kwargs):
            letter = kwargs.get('letter', None)
            phoneme_onset = kwargs.get('phoneme_onset', None)
            phoneme_nucleus = kwargs.get('phoneme_nucleus', None)
            phoneme_coda = kwargs.get('phoneme_coda', None)

            # nuclues combine
            if isinstance(phoneme_nucleus, (str, unicode)):
                phoneme_nucleus = unicode(phoneme_nucleus)

                # nuclues combine
                if re.search(r'.\+.', phoneme_nucleus):
                    if phoneme_nucleus in Korean.phoneme_nucleus_combine_dict:
                        phoneme_nucleus = Korean.phoneme_nucleus_combine_dict[phoneme_nucleus]
                    else:
                        raise Korean.SyllableFailedException()

                # nuclues phonetic combine
                elif re.search(r'..', phoneme_nucleus):
                    if phoneme_nucleus in Korean.phoneme_nucleus_phonetic_combine_dict:
                        phoneme_nucleus = Korean.phoneme_nucleus_phonetic_combine_dict[phoneme_nucleus]
                    else:
                        raise Korean.SyllableFailedException()

            if kwargs.get('check', True):
                if letter is not None:
                    if not isinstance(letter, (str, unicode)):
                        raise Korean.SyllableFailedException()

                    letter = letter if isinstance(letter, unicode) else unicode(letter)
                    if len(letter) != 1:
                        raise Korean.SyllableFailedException()

                    if not Korean.is_korean(letter, include_phoneme=False):
                        raise Korean.SyllableFailedException()

                if phoneme_onset is not None:
                    if not isinstance(phoneme_onset, (str, unicode)):
                        raise Korean.SyllableFailedException()

                    phoneme_onset = phoneme_onset \
                        if isinstance(phoneme_onset, unicode) else unicode(phoneme_onset)
                    if len(phoneme_onset) != 1:
                        raise Korean.SyllableFailedException()

                    if not Korean.is_korean_phoneme(phoneme_onset):
                        raise Korean.SyllableFailedException()

                if phoneme_nucleus is not None:
                    if not isinstance(phoneme_nucleus, (str, unicode)):
                        raise Korean.SyllableFailedException()

                    phoneme_nucleus = phoneme_nucleus \
                        if isinstance(phoneme_nucleus, unicode) else unicode(phoneme_nucleus)
                    if len(phoneme_nucleus) != 1:
                        raise Korean.SyllableFailedException()

                    if not Korean.is_korean_phoneme(phoneme_nucleus):
                        raise Korean.SyllableFailedException()

                if phoneme_coda is not None:
                    if not isinstance(phoneme_coda, (str, unicode)):
                        raise Korean.SyllableFailedException()

                    phoneme_coda = phoneme_coda \
                        if isinstance(phoneme_coda, unicode) else unicode(phoneme_coda)
                    if len(phoneme_coda) != 1:
                        raise Korean.SyllableFailedException()

                    # space include
                    if not Korean.is_korean_phoneme(phoneme_coda, include_space=True):
                        raise Korean.SyllableFailedException()

            self.letter = letter
            self.phoneme_onset = phoneme_onset if phoneme_onset is not u'' else None
            self.phoneme_nucleus = phoneme_nucleus if phoneme_nucleus is not u'' else None
            self.phoneme_coda = phoneme_coda if phoneme_coda is not u'' else None

            if self.phoneme_onset or self.phoneme_nucleus or self.phoneme_coda:
                self.combine()
            else:
                self.decompose()

        def __deepcopy__(self, memo):
            return Korean.Syllable(letter=self.letter)

        def __str__(self):
            return str(self.letter)

        def __unicode__(self):
            return unicode(self.letter)

        def combine(self):
            phoneme_onset = self.phoneme_onset if self.phoneme_onset is not u' ' else u'ㅇ'
            phoneme_nucleus = self.phoneme_nucleus if self.phoneme_nucleus is not u' ' else None
            phoneme_coda = self.phoneme_coda

            # nuclues combine
            if isinstance(phoneme_nucleus, (str, unicode)):
                phoneme_nucleus = unicode(phoneme_nucleus)

                # nuclues combine
                if re.search(r'.\+.', phoneme_nucleus):
                    if phoneme_nucleus in Korean.phoneme_nucleus_combine_dict:
                        phoneme_nucleus = Korean.phoneme_nucleus_combine_dict[phoneme_nucleus]
                    else:
                        raise Korean.SyllableFailedException()

                # nuclues phonetic combine
                elif re.search(r'..', phoneme_nucleus):
                    if phoneme_nucleus in Korean.phoneme_nucleus_phonetic_combine_dict:
                        phoneme_nucleus = Korean.phoneme_nucleus_phonetic_combine_dict[phoneme_nucleus]
                    else:
                        raise Korean.SyllableFailedException()

            if self.letter is not None:
                self.decompose()
                phoneme_onset = phoneme_onset if phoneme_onset is not None else self.phoneme_onset  #
                phoneme_nucleus = phoneme_nucleus if phoneme_nucleus is not None else self.phoneme_nucleus  #
                phoneme_coda = phoneme_coda if phoneme_coda is not None else self.phoneme_coda

            # phoneme only exists
            elif phoneme_onset is None or phoneme_nucleus is None:

                    if phoneme_onset:
                        if phoneme_coda is None or phoneme_coda == u' ':
                            # onset only
                            self.letter = phoneme_onset
                            if self.letter is None:
                                raise Korean.SyllableFailedException()
                            return
                        else:
                            # onset + coda
                            if self.letter is None:
                                raise Korean.SyllableFailedException()
                            return

                    elif phoneme_nucleus:
                        if phoneme_coda is None or phoneme_coda == u' ':
                            # nucleus only
                            self.letter = phoneme_nucleus
                            if self.letter is None:
                                raise Korean.SyllableFailedException()
                            return
                        else:
                            # nucleus + coda
                            phoneme_onset = u'ㅇ'

            try:
                # if exists only onset
                if phoneme_onset and not phoneme_nucleus and not phoneme_coda:
                    self.letter = phoneme_onset

                else:
                    onset_index = Korean.phoneme_onset_dict[phoneme_onset]
                    nucleus_index = Korean.phoneme_nucleus_dict[phoneme_nucleus]
                    coda_index = Korean.phoneme_coda_dict[phoneme_coda] if phoneme_coda is not None else 0

                    nucleus_size = Korean.phoneme_nucleus_list_len
                    coda_size = Korean.phoneme_coda_list_len

                    code = (onset_index * nucleus_size * coda_size) + (nucleus_index * coda_size) + coda_index
                    self.letter = unichr(code + Korean.unicode_base_code)

            except KeyError:
                raise Korean.SyllableFailedException()

            self.phoneme_onset = phoneme_onset
            self.phoneme_nucleus = phoneme_nucleus
            self.phoneme_coda = phoneme_coda

            if self.phoneme_coda == u' ':
                self.phoneme_coda = None

        def decompose(self):
            if self.letter is None and self.letter == u' ':
                raise Korean.SyllableFailedException()

            self.phoneme_onset = None
            self.phoneme_nucleus = None
            self.phoneme_coda = None

            base_code = ord(self.letter) - Korean.unicode_base_code

            if base_code < 0:
                if self.letter in Korean.phoneme_onset_dict:
                    self.phoneme_onset = self.letter
                    return
                elif self.letter in Korean.phoneme_nucleus_dict:
                    self.phoneme_nucleus = self.letter
                    return
                elif self.letter in Korean.phoneme_coda_dict:
                    self.phoneme_coda = self.letter
                    return
                else:
                    raise Korean.SyllableFailedException()

            c1 = base_code / Korean.unicode_onset_offset
            self.phoneme_onset = Korean.phoneme_onset_list[c1]

            c2 = (base_code - (Korean.unicode_onset_offset * c1)) / Korean.unicode_nucleus_offset
            self.phoneme_nucleus = Korean.phoneme_nucleus_list[c2]

            c3 = (base_code - (Korean.unicode_onset_offset * c1) - (Korean.unicode_nucleus_offset * c2))
            self.phoneme_coda = Korean.phoneme_coda_list[c3]

            # blank check
            if self.phoneme_coda == u' ':
                self.phoneme_coda = None

        def is_completed(self):
            if not self.phoneme_onset:
                return False

            return self.phoneme_nucleus

        def has_double_onset(self):
            if not self.phoneme_onset:
                return False

            return self.phoneme_onset in Korean.phoneme_double_consonant_dict

        def has_double_coda(self):
            if not self.phoneme_coda:
                return False

            return self.phoneme_coda in Korean.phoneme_double_consonant_dict

    def __init__(self, text):
        if isinstance(text, str):
            self.text = unicode(text)
        elif isinstance(text, unicode):
            self.text = text
        else:
            raise Korean.TypeErrorException()

        self.parse()

    def __getitem__(self, key):
        return self.character_list[key]

    def __iter__(self):
        for x in self.character_list:
            yield x

    def __len__(self):
        return len(self.character_list)

    def __str__(self):
        return str(self.text)

    def __unicode__(self):
        return unicode(self.text)

    def parse(self):
        if isinstance(self.text, str):
            self.text = unicode(self.text)

        self.character_list = []

        for i in self.text:
            if Korean.is_korean(i, include_space=False):
                self.character_list.append(Korean.Syllable(letter=i, check=False))
            else:
                self.character_list.append(i)

        return self.character_list

    def join(self):
        self.text = u''

        for character in self.character_list:
            self.text += unicode(character)

        if not self.text:
            self.text = None

    def _tokenization(self, **kwargs):
        clone = kwargs.get('clone', False)
        token_list = []
        token = []

        for character in self.character_list:
            if isinstance(character, Korean.Syllable):
                token.append(copy.deepcopy(character) if clone else character)
            else:
                token_list.append(token)
                token = []

        if token:
            token_list.append(token)

        return token_list

    @staticmethod
    def transform(sequence, filters):
        if isinstance(sequence, (str, unicode)):
            sequence = Korean(sequence)

        if not hasattr(sequence, '__iter__') and not isinstance(sequence, collections.Sequence):
            return None

        if not filters:
            return None

        if not isinstance(filters, list):
            filters = [filters]

        # pre
        for filter in filters:
            if isinstance(filter, Korean.Filter):
                filter.pre(sequence=sequence)

        index = 0
        for c in sequence:
            for filter in filters:
                if isinstance(filter, Korean.Filter):
                    filter.do(sequence=sequence, character=c, index=index)
                elif hasattr(filter, '__call__'):
                    filter(sequence=sequence, character=c, index=index)

            index += 1

        # post
        for filter in filters:
            if isinstance(filter, Korean.Filter):
                filter.post(sequence=sequence)

        # combine
        if isinstance(sequence, Korean):
            sequence.join()

        return sequence

    @staticmethod
    def is_korean(text, **kwargs):
        src = text
        include_legacy = kwargs.get('include_legacy', False)
        include_space = kwargs.get('include_space', False)
        include_phoneme = kwargs.get('include_phoneme', True)

        if not isinstance(text, unicode):
            src = unicode(text)

        range_syllable_max = 0xD7AF if include_legacy else 0xD7A3
        range_phoneme_max = 0x3131 if include_legacy else 0x3163

        for i in src:
            if i == u' ':
                if include_space:
                    continue
                else:
                    return False

            value = ord(i)

            # syllable range(AC00~D7AF)
            if 0xAC00 <= value <= range_syllable_max:
                pass
            # phoneme range(3131~318E)
            elif include_phoneme and 0x3131 <= value <= range_phoneme_max:
                pass
            # is not korean
            else:
                return False

        return True

    @staticmethod
    def is_korean_phoneme(text, **kwargs):
        src = text
        include_legacy = kwargs.get('include_legacy', False)
        include_space = kwargs.get('include_space', False)

        if not isinstance(text, unicode):
            src = unicode(text)

        range_phoneme_max = 0x3131 if include_legacy else 0x3163

        for i in src:
            if i == u' ':
                if include_space:
                    continue
                else:
                    return False

            value = ord(i)

            # phoneme range(3131~318E)
            if 0x3131 <= value <= range_phoneme_max:
                pass
            # is not phoneme
            else:
                return False

        return True
