from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from setuptools.package_index import user_agent
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
import re
import time
import datetime

import os
from pandas.compat.numpy import np_long


#뉴스 카테고리 list
category = ['Politics','Economic','Social','Culture','World','IT']


#크롬에서 연다
#열어볼 주소
options = ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

#한글만 긁어옴
options.add_argument('user_agent='+user_agent)
options.add_argument('lang=ko_KR')

service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

#정치~세계 페이지 까지 반복
for page_i in range(6):

    # 데이터 프레임 초기화
    df_titles = pd.DataFrame()

    #주소는 맨뒤에 100~106까지 반복됨
    url = 'https://news.naver.com/section/10{}'.format(page_i)
    driver.get(url)  # 브라우저 띄우기
    time.sleep(1)    # 버튼 생성이 될때까지 기다리는 딜레이

    # 버튼 더보기 주소
    if page_i==1 :#경제일 때만 주소 다름
        button_xpath = '//*[@id="newsct"]/div[5]/div/div[2]'#경제 버튼주소
    else:
        button_xpath = '//*[@id="newsct"]/div[4]/div/div[2]'#나머지 버튼 주소



    # 버튼을 15번 정도 누르기
    for i in range(15):
        time.sleep(1)
        driver.find_element(By.XPATH, button_xpath).click()



    # 뉴스 제목 수집
    for i in range(1, 98):
        titles = []
        
        #한 문단에 6개씩 있음
        for j in range(1, 7):

            if page_i==1:
                title_xpath = '//*[@id="newsct"]/div[5]/div/div[1]/div[{}]/ul/li[{}]/div/div/div[2]/a/strong'.format(i,j)#경제 제목주소
            else:
                title_xpath = '//*[@id="newsct"]/div[4]/div/div[1]/div[{}]/ul/li[{}]/div/div/div[2]/a/strong'.format(i, j)  # 정치 제목주소

            try:
                #한글을 제외한 모든 문자 제거 후 저장
                title = driver.find_element(By.XPATH, title_xpath).text
                title = re.compile('[^가-힣 ]').sub('', title)
                titles.append(title)  # 리스트에 추가

            except:  # 예외처리(없는건 그냥 넘어가라)
                print('pass: ', i, j)

        # 데이터프레임 생성 (컬럼: 제목, 카테고리)
        df_section_titles = pd.DataFrame(titles, columns=['titles'])
        df_section_titles['category'] = category[page_i]

        # 최종 데이터프레임에 카테고리별 뉴스 제목 추가
        df_titles = pd.concat([df_titles, df_section_titles], axis='rows', ignore_index=True)

    # 데이터프레임 확인
    print(df_titles.head())
    df_titles.info()
    print(df_titles['category'].value_counts())

    #리스트 초기화
    titles.clear()

    # CSV 파일로 저장
    df_titles.to_csv('./crawling_data/{}_naver_headline_news{}.csv'.format(
        category[page_i], datetime.datetime.now().strftime('%Y%m%d')), index=False)



time.sleep(1)




# 병합할 CSV 파일이 있는 폴더 경로 설정
# Windows의 경우, '\' 대신 '/'
folder_path = 'C:/workspace/news_category_classfication/crawling_data'

# 폴더에 있는 파일 목록 확인
try:
    files_in_folder = os.listdir(folder_path)
    print(f"폴더 내 파일: {files_in_folder}")
except FileNotFoundError:
    print(f"폴더 경로가 올바르지 않습니다: {folder_path}")

# CSV 파일만 필터링
csv_files = [file for file in files_in_folder if file.endswith('.csv')]
print(f"CSV 파일 목록: {csv_files}")

# CSV 파일 병합
if csv_files:
    dataframes = [pd.read_csv(os.path.join(folder_path, file)) for file in csv_files]
    merged_df = pd.concat(dataframes, ignore_index=True)

    # 결과 저장
    output_path = os.path.join(folder_path, "all_naver_headline_news.csv")
    merged_df.to_csv(output_path, index=False)
    print(f"병합된 파일이 저장되었습니다: {output_path}")
else:
    print("CSV 파일이 폴더에 없습니다.")




#통합본 출력
df= pd.read_csv('./crawling_data/all_naver_headline_news.csv')

df.drop_duplicates(inplace=True)
print(df.head())
df.info()
print(df.category.value_counts())


