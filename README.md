# Project: Zeroth
* Kaldi-based Korean ASR open-source project
* License: Apache 2.0

Zeroth is an open source project for Korean speech recognition implemented using the Kaldi toolkit.

This project was developed as part of Atlas’s (https://www.goodatlas.com) Language AI platform, which enables enterprises to add intelligence to their B2C communications.

By introducing an official Korean Kaldi recipe, the Zeroth project aims to make Korean speech recognition more broadly accessible to everyone.

As the name Zeroth, or the 0th, suggests, this project’s aim to be the starting point and a foundational piece upon which anyone can build new products and services using speech recognition. 

We hope you find this project useful and welcome any opportunities to discuss or work together.

Contact: Lucas Jo (lucasjo@goodatlas.com)

### Special thanks

* Zeroth was developed in collaboration with Wonkyum Lee (wonkyum@gridspace.com) at [Gridspace Inc.] (https://www.gridspace.com).

### Mentioned links
* [Interview] (http://blog.naver.com/fastcampus/221181060609) with FastCampus
* [Deep Learning - Speech Recognition CAMP] (http://www.fastcampus.co.kr/data_camp_dsr/) @ FastCampus

## 0. Overview
<img src="/doc/imgs/Zeroth.png" width="60%">

## 1. Audio Data

* As of 3 February 2018: 51.6 hours transcribed Korean audio for training data (22,263 utterances, 105 people, 3000 sentences)
* License: [CC BY 4.0] (https://creativecommons.org/licenses/by/4.0/)

We offer a voice recording app [MoreCoin (Android)] (https://play.google.com/store/apps/details?id=com.goodatlas.morecoin) that you can use to participate in building our open source database of Korean training data.

## 2. Requirements

* [Requirements] description of packages needed to run the Zeroth project: https://github.com/goodatlas/zeroth/wiki/Requirements)
* [Requirements-2] additional packages to execute code for the language model and phonetic dictionary: (https://github.com/goodatlas/zeroth/wiki/Requirement-2) 

## Acoustic Model
The latest Kaldi recipe is applied to the Zeroth's acoustic model:

* TDNN (with Factorization) / TDNN + LSTM / TDNN + OPGRU
* Chain model
* Data augmentation of reverberant speech

## Language Model & Lexicon
Zeroth's language model and phonetic dictionary use an end-to-end data driven approach. Any contributions to our open source audio database will automatically be incorporated into the latest language model and phonetic dictionary. 

To create a custom language model and phonetic dictionary: [s5 / data / local / lm / README.md] (https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/README.md).

* Corpus (Corpus)
  * Training sentences: 108,408,327
  * Test sentences: 12,045,282
  * Total: 120,453,609

* Phonetic Dictionary
  * Unique words: 29,832,494
  * Unique words with the highest 98% frequency: 7,991,121
  * Unique morphemes: 458,406
  * Size of phonetic dictionary considering pronunciation diversity: 688,503

* Language Model
  * Perplexity test 3-gram: ppl = 220.4536 (12,045,282 sentences, 194,241,480 words, 26,845 OOVs)
  * Perplexity test 4-gram: ppl = 186.458 (12,045,282 sentences, 194,241,480 words, 26,845 OOVs)

***

# Project: Zeroth
* 칼디를 이용하여 구축하는 한국어 음성인식
* License: Apache 2.0

Zeroth 프로젝트는 Kaldi open source tool-kit 을 사용해서 한국어 음성인식기를 구현하는 프로젝트 입니다. 
이 프로젝트는 기업이 AI를 고객 서비스에 추가하는 데 도움이되는 [(주)아틀라스가이드](https://www.goodatlas.com)의 Language AI 플랫폼 개발의 일부로서 개발되었습니다. 
Kaldi official recipe 에 한국어 버전을 소개하는 것을 시작으로, 
많은 사람들의 참여를 통해 누구나 사용할 수 있는 음성인식기를 만들어 나갈 수 있도록 하는 것을 목표로하는 프로젝트입니다.
제로스라는 이름은 0-th, 즉 0 번째를 의미합니다. 이름이 의미하는 것처럼 이 프로젝트를 통해 음성인식기를 
만들기 위해 필요한 모든 과정을 처음부터 끝까지 함께 해보고 토론할 수 있기를 바랍니다.

Contact: Lucas Jo (lucasjo@goodatlas.com)

### Special thanks 

* [Gridspace Inc.](https://www.gridspace.com) 사에서 일하고 계신 Wonkyum Lee 님과의 co-work 를 통해 이 프로젝트를 진행하고 있음을 밝힙니다. 

### Mentioned links
* [Interview](http://blog.naver.com/fastcampus/221181060609) with FastCampus
* [딥러닝-음성인식 CAMP](http://www.fastcampus.co.kr/data_camp_dsr/) @ FastCampus

## 0. Overview
<img src="/doc/imgs/Zeroth.png" width="60%">

## 1. Audio Data

* 2018.02.03: 51.6 시간 한국어 학습데이터 (22,263 발화, 105명, 3000 문장)
* License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

현재 제로스 프로젝트에는 상기와 같은 음성데이터가 포함되어 있습니다.
공개 음성 DB 구축에 참여할 수 있는 음성 녹음 앱 [모아코인(Android)](https://play.google.com/store/apps/details?id=com.goodatlas.morecoin)을 제공하고 있으며, 
해당 앱을 통해 음성 데이터를 1시간 기부해주시면 해당 시점까지 구축된 공개 음성 DB에 접근하여 다운로드할 수 있는 권한을
AWS temporary credential 형태로 발급해 드립니다. 한번 발급된 credential은 12 시간 동안 유효합니다.
더 자세한 내용은 [AWS-temporary-credential](https://github.com/goodatlas/zeroth/wiki/AWS-temporary-credential) 
페이지를 확인하시기 바랍니다

## 2. Requirements

* 제로스 프로젝트를 실행하는데 필요한 패키지들에 대한 설명은 [Requirements](https://github.com/goodatlas/zeroth/wiki/Requirements)
위키 페이지를 참조하시기 바랍니다.
* 언어모델과 발음사전을 구현하는 코드를 직접 실행하기 위해서는 [Requirements-2](https://github.com/goodatlas/zeroth/wiki/Requirement-2)
위키 페이지를 참조하여 추가적인 패키지를 설치하시기 바랍니다.

## 3. Acoustic Model
현재 제로스 프로젝트 음향모델에는 아래와 같은 최신 kaldi recipe 가 적용되어 있습니다.

* TDNN (with Factorization) / TDNN + LSTM / TDNN + OPGRU 
* Chain model
* Data augmentation of reverberant speech

## 4. Language Model & Lexicon
제로스 프로젝트에 사용되는 언어모델과 발음사전은 처음부터 끝까지 data-driven 방식으로 만들어집니다.
아래는 [AWS-temporary-credential](https://github.com/goodatlas/zeroth/wiki/AWS-temporary-credential)
을 발급받은 경우 오디오 데이터와 함께 자동으로 받아지는 언어모델과 발음사전의 세부사항입니다.
개인적으로 직접 특화된 언어모델과 발음사전을 만들고자 하는 경우에는 세부적인 방법이  
[s5/data/local/lm/README.md ](https://github.com/goodatlas/zeroth/blob/master/s5/data/local/lm/README.md)에 기술되어 있으니 
참조하시기 바랍니다.

* 말뭉치(Corpus)
  * 훈련된 문장의 수: 108,408,327
  * 테스트 문장의 수:  12,045,282
  * 전 체:         120,453,609

* 발음사전(Lexicon)
  * 고유한 단어의 수: 29,832,494 
  * 상위 98% 빈도 수를 보이는 고유한 단어의 수: 7,991,121
  * Data-drive 방식으로 찾은 고유한 형태소의 수: 458,406
  * 발음 다양성을 고려한 발음사전의 크기: 688,503

* 언어모델(Language Model)
  * Perplexity test 3-gram: ppl= 220.4536 (12,045,282 sentences, 194,241,480 words, 26,845 OOVs)
  * Perplexity test 4-gram: ppl= 186.458 (12,045,282 sentences, 194,241,480 words, 26,845 OOVs)
