# 필요한 라이브러리 및 모듈 불러오기
import pickle
from operator import index
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
from konlpy.tag import Okt, Kkma  # 한글 형태소 분석기
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# CSV 파일 불러오기 및 중복 제거
df = pd.read_csv('./crawling_data/all_naver_headline_news.csv')
df.drop_duplicates(inplace=True)  # 중복 데이터 제거
df.reset_index(drop=True, inplace=True)  # 인덱스 초기화

# 데이터 프레임 정보 확인
print(df.head())  # 상위 5개 데이터 출력
df.info()  # 데이터 구조 확인
print(df.category.value_counts())  # 카테고리별 데이터 개수 확인

# X: 뉴스 제목, Y: 뉴스 카테고리로 분리
X = df['titles']
Y = df['category']

# 카테고리 라벨링
encoder = LabelEncoder()
labeled_y = encoder.fit_transform(Y)  # 문자열 카테고리를 숫자로 변환
print(labeled_y[:3])  # 변환 결과 일부 확인
label = encoder.classes_  # 클래스 확인
print(label)

# 라벨 인코더 저장
with open('./models/encoder.pickle', 'wb') as f:
    pickle.dump(encoder, f)

# 카테고리 데이터를 원-핫 인코딩
onehot_Y = to_categorical(labeled_y)
print(onehot_Y)

# 형태소 분석 (예: 첫 번째 뉴스 제목)
print(X[0])  # 원본 텍스트 확인
okt = Okt()
okt_x = okt.morphs(X[0], stem=True)  # 형태소 분석 결과
print('Okt: ', okt_x)

# 형태소 분석을 전체 데이터에 적용
for i in range(len(X)):
    X[i] = okt.morphs(X[i], stem=True)

print(X)  # 분석 결과 확인

# 불용어 처리
stopwords = pd.read_csv('./crawling_data/stopwords.csv', index_col=0)
print(stopwords)

# 불용어 및 한 글자 단어 제거
for sentence in range(len(X)):
    words = []
    for word in range(len(X[sentence])):
        if len(X[sentence][word]) > 1:  # 한 글자 제거
            if X[sentence][word] not in list(stopwords['stopword']):  # 불용어 제거
                words.append(X[sentence][word])
    X[sentence] = ' '.join(words)  # 단어들을 공백으로 연결

# 전처리 결과 확인
print(X[:5])

# 텍스트 데이터 숫자 라벨링 (단어 인덱싱)
token = Tokenizer()
token.fit_on_texts(X)  # 전체 데이터 학습
tokened_X = token.texts_to_sequences(X)  # 텍스트를 정수 시퀀스로 변환
wordsize = len(token.word_index) + 1  # 고유 단어 수 + 1
print(wordsize)

print(tokened_X[:5])  # 라벨링 결과 일부 확인

# 입력 데이터 길이 맞추기 (패딩)
# 가장 긴 문장의 길이를 기준으로 패딩
max = 0
for i in range(len(tokened_X)):
    if max < len(tokened_X[i]):
        max = len(tokened_X[i])
print(max)  # 최대 길이 출력

X_pad = pad_sequences(tokened_X, max)  # 패딩 추가
print(X_pad)
print(len(X_pad[0]))  # 패딩 결과 확인

# 학습 및 테스트 데이터 분리
X_train, X_test, Y_train, Y_test = train_test_split(X_pad, onehot_Y, test_size=0.1)
print(X_train.shape, Y_train.shape)  # 학습 데이터 크기 확인
print(X_test.shape, Y_test.shape)  # 테스트 데이터 크기 확인

# 데이터 저장
np.save('./crawling_data/news_data_X_train_max_{}_wordsize_{}'.format(max, wordsize), X_train)
np.save('./crawling_data/news_data_Y_train_max_{}_wordsize_{}'.format(max, wordsize), Y_train)
np.save('./crawling_data/news_data_X_test_max_{}_wordsize_{}'.format(max, wordsize), X_test)
np.save('./crawling_data/news_data_Y_test_max_{}_wordsize_{}'.format(max, wordsize), Y_test)
