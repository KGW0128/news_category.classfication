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

#뉴스 제목 카테고리
category = ['Politics','Economic','Social','Culture','World','IT']


#데이터 프레임 초기화
df_titles = pd.DataFrame()


options = ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

options.add_argument('user_agent='+user_agent)
options.add_argument('lang=ko_KR')

service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

url = 'https://news.naver.com/section/100'#정치 사이트주소
#url = 'https://news.naver.com/section/101'#경제 사이트주소
driver.get(url)#브라우저 띄우기

#버튼 생성이 될때까지 기다리는 딜레이
time.sleep(1)

#버튼 더보기 주소
button_xpath = '//*[@id="newsct"]/div[4]/div/div[2]'#정치 버튼주소
#button_xpath = '//*[@id="newsct"]/div[5]/div/div[2]'#경제 버튼주소


#버튼을 15번 정도 누르기
for i in range(15):
    time.sleep(0.5)
    driver.find_element(By.XPATH, button_xpath).click()





#사이트 규칙 찾은 후 데이터 수집
for i in range(1,98):
    # txt로 변환된 타이틀을 한글제외 가공해서 넣을 list변수
    titles = []

    for j in range(1,7):

        title_xpath = '//*[@id="newsct"]/div[4]/div/div[1]/div[{}]/ul/li[{}]/div/div/div[2]/a/strong'.format(i,j)#정치 제목주소
        #title_xpath = '//*[@id="newsct"]/div[5]/div/div[1]/div[{}]/ul/li[{}]/div/div/div[2]/a/strong'.format(i,j)#경제 제목주소
        try:
            title = driver.find_element(By.XPATH, title_xpath).text
            title = re.compile('[^가-힣 ]').sub('', title)
            titles.append(title)  #리스트에 추가

        except:#예외처리(없는건 그냥 넘어가라)
            print('pass: ',i, j)

    # 데이터프레임 생성 (컬럼: 제목, 카테고리)
    df_section_titles = pd.DataFrame(titles, columns=['titles'])
    df_section_titles['category'] = category[0]#경제list
    #df_section_titles['category'] = category[1]#정치list

    # 최종 데이터프레임에 카테고리별 뉴스 제목 추가
    df_titles = pd.concat([df_titles, df_section_titles], axis='rows', ignore_index=True)


# 데이터프레임 확인
print(df_titles.head())
df_titles.info()
print(df_titles['category'].value_counts())


# CSV 파일로 저장 (파일명: naver_headline_news_YYYYMMDD.csv)
#datetime.datetime.now() :현재 시간을 알려줌
df_titles.to_csv('./crawling_data/Politics_naver_headline_news{}.csv'.format(
    datetime.datetime.now().strftime('%Y%m%d')), index=False)

# df_titles.to_csv('./crawling_data/Economic_naver_headline_news{}.csv'.format(
#     datetime.datetime.now().strftime('%Y%m%d')), index=False)





time.sleep(3)

#driver.close()#브라우저 닫기



