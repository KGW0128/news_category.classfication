import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, MaxPooling1D, LSTM, Dropout, Dense
import numpy as np
from tensorflow.python.keras.saving.saved_model.load import metrics

# 데이터 로드
X_train = np.load('./crawling_data/news_data_X_train_max_16_wordsize_6452.npy', allow_pickle=True)
X_test = np.load('./crawling_data/news_data_X_test_max_16_wordsize_6452.npy', allow_pickle=True)
Y_train = np.load('./crawling_data/news_data_Y_train_max_16_wordsize_6452.npy', allow_pickle=True)
Y_test = np.load('./crawling_data/news_data_Y_test_max_16_wordsize_6452.npy', allow_pickle=True)


print(X_train.shape, Y_train.shape)  # 학습 데이터 크기 확인
print(X_test.shape, Y_test.shape)  # 테스트 데이터 크기 확인

# 모델 정의
model = Sequential()
#max값: 6452, word size: 16
model.add(Embedding(input_dim=6452, output_dim=300, input_length=16))
model.add(Conv1D(32, kernel_size=5, padding='same', activation='relu'))
model.add(MaxPooling1D(pool_size=1))
model.add(LSTM(128, activation='tanh', return_sequences=True))
model.add(Dropout(0.3))
model.add(LSTM(64, activation='tanh', return_sequences=True))
model.add(Dropout(0.3))
model.add(LSTM(64, activation='tanh'))
model.add(Dropout(0.3))
model.add(Dense(6, activation='softmax'))

# 명시적으로 모델 빌드
#tensorflow버전 차이 문제인거 같음
model.build(input_shape=(None, 16))  # 입력 데이터 크기 (None은 배치 크기)
model.summary()


model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
fit_hist = model.fit(X_train, Y_train, batch_size =128,
                     epochs=10, validation_data=(X_test,Y_test))
score = model.evaluate(X_test, Y_test, verbose=0)
print('학습결과: ',score[1])

model.save('./models/news_catepory_classfication_model_{}.h5'.format(
    fit_hist.history['val_accuracy'][-1]))
plt.plot(fit_hist.history['val_accuracy'],label='val_accuracy')
plt.plot(fit_hist.history['accuracy'],label='accuracy')
plt.legend()
plt.show()
