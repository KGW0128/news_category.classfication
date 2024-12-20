

import pickle
from operator import index

import  pandas as pd
import  numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
from konlpy.tag import Okt, Kkma      #한글 토큰 분리기
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

df= pd.read_csv('./crawling_data/all_naver_headline_news.csv')


df.drop_duplicates(inplace=True)
df.reset_index(drop=True,inplace= True)
print(df.head())
df.info()
print(df.category.value_counts())

X=df['titles']
Y=df['category']
encoder = LabelEncoder()

#라벨 데이터로 변환
#처음에 한번만 사용해야됨(유니크 데이터이기 때문에)
labeled_y = encoder.fit_transform(Y)
print(labeled_y[:3])

label = encoder.classes_
print(label)


#엔코더 저장
with open('./models/encoder.pickle','wb') as f:
    pickle.dump(encoder, f)

onehot_Y =to_categorical(labeled_y)
print(onehot_Y)


#형태소 분리 후 일일이 라벨링
print(X[0])
okt = Okt()
okt_x = okt.morphs(X[0], stem=True)
print('Okt: ',okt_x)

#kkma = Kkma()
#kkma_x =kkma.morphs(X[0])
#print('Kkma: ',kkma_x)


for i in range(len(X)):
    X[i]=okt.morphs(X[i], stem =True)

print(X)


#한글자 또는 불용어 등 전처리 과정
stopwords = pd.read_csv('./crawling_data/stopwords.csv',index_col=0)
print(stopwords)


#한글자,불용어 등 빼고 띄어쓰기 기준으로 합쳐줌
for sentence in range(len(X)):
    words = []
    for word in range(len(X[sentence])):
        if len(X[sentence][word])>1:
            if X[sentence][word] not in list(stopwords['stopword']):
                words.append(X[sentence][word])
    X[sentence] = ' '.join(words)

#결과 출력해보기
print(X[:5])


#형태소 하나하나 숫자 라벨링
token = Tokenizer()
token.fit_on_texts(X)
tokened_X = token.texts_to_sequences(X)
wordsize = len(token.word_index) + 1


print(tokened_X[:5])