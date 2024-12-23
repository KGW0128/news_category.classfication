# 필요한 라이브러리 임포트
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
import re
import time
import datetime
import os

# 뉴스 카테고리 리스트 정의
category = ['Politics', 'Economic', 'Social', 'Culture', 'World', 'IT']

# 크롬 브라우저 옵션 설정
options = ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
options.add_argument('user_agent=' + user_agent)  # 사용자 에이전트 설정
options.add_argument('lang=ko_KR')  # 언어 설정

# 크롬 드라이버 초기화
service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 카테고리별 뉴스 크롤링 시작
for page_i in range(6):
    # 데이터프레임 초기화
    df_titles = pd.DataFrame()

    # 카테고리에 따른 URL 설정
    url = 'https://news.naver.com/section/10{}'.format(page_i)
    driver.get(url)  # 브라우저 실행
    time.sleep(1)  # 페이지 로드 대기

    # 더보기 버튼 XPATH 정의 (카테고리에 따라 다름)
    if page_i == 1:  # 경제 카테고리
        button_xpath = '//*[@id="newsct"]/div[5]/div/div[2]'
    else:  # 나머지 카테고리
        button_xpath = '//*[@id="newsct"]/div[4]/div/div[2]'

    # 더보기 버튼 클릭 (15번 반복)
    for i in range(15):
        time.sleep(1)
        driver.find_element(By.XPATH, button_xpath).click()

    # 뉴스 제목 수집
    for i in range(1, 98):  # 뉴스 블록 탐색
        titles = []
        for j in range(1, 7):  # 각 블록 내 뉴스 항목 탐색
            if page_i == 1:  # 경제 카테고리
                title_xpath = '//*[@id="newsct"]/div[5]/div/div[1]/div[{}]/ul/li[{}]/div/div/div[2]/a/strong'.format(i, j)
            else:  # 다른 카테고리
                title_xpath = '//*[@id="newsct"]/div[4]/div/div[1]/div[{}]/ul/li[{}]/div/div/div[2]/a/strong'.format(i, j)

            try:
                # 뉴스 제목 크롤링 및 한글 외 문자 제거
                title = driver.find_element(By.XPATH, title_xpath).text
                title = re.compile('[^가-힣 ]').sub('', title)
                titles.append(title)
            except:  # 예외 처리 (존재하지 않는 항목 무시)
                print('pass: ', i, j)

        # 크롤링된 제목을 데이터프레임에 저장
        df_section_titles = pd.DataFrame(titles, columns=['titles'])
        df_section_titles['category'] = category[page_i]
        df_titles = pd.concat([df_titles, df_section_titles], axis='rows', ignore_index=True)

    # 카테고리별 데이터프레임 정보 출력
    print(df_titles.head())
    df_titles.info()
    print(df_titles['category'].value_counts())

    # 제목 리스트 초기화
    titles.clear()

    # 카테고리별 데이터를 CSV 파일로 저장
    df_titles.to_csv('./crawling_data/{}_naver_headline_news{}.csv'.format(
        category[page_i], datetime.datetime.now().strftime('%Y%m%d')), index=False)

# 브라우저 대기
time.sleep(1)

# 병합할 CSV 파일이 있는 폴더 경로 설정
folder_path = 'C:/workspace/news_category_classfication/crawling_data'

# 폴더 내 파일 확인
try:
    files_in_folder = os.listdir(folder_path)
    print(f"폴더 내 파일: {files_in_folder}")
except FileNotFoundError:  # 폴더가 없을 경우 예외 처리
    print(f"폴더 경로가 올바르지 않습니다: {folder_path}")

# CSV 파일 필터링
csv_files = [file for file in files_in_folder if file.endswith('.csv')]
print(f"CSV 파일 목록: {csv_files}")

# CSV 파일 병합
if csv_files:
    dataframes = [pd.read_csv(os.path.join(folder_path, file)) for file in csv_files]
    merged_df = pd.concat(dataframes, ignore_index=True)

    # 병합된 결과를 저장
    output_path = os.path.join(folder_path, "all_naver_headline_news.csv")
    merged_df.to_csv(output_path, index=False)
    print(f"병합된 파일이 저장되었습니다: {output_path}")
else:
    print("CSV 파일이 폴더에 없습니다.")

# 병합된 CSV 파일 확인
df = pd.read_csv('./crawling_data/all_naver_headline_news.csv')

# 중복 데이터 제거 및 정보 출력
df.drop_duplicates(inplace=True)
print(df.head())
df.info()
print(df.category.value_counts())