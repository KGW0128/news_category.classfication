from bs4 import  BeautifulSoup
import requests
import re
import pandas as pd
import datetime

# 네이버 뉴스에서 긁어와서 자료 만듬(crawilng)

#뉴스 제목 카테고리
category = ['Politics','Economic','Social','Culture','World','IT']

#데이터 프레임 초기화
df_titles = pd.DataFrame()



#모든 뉴스 헤드라인 카테고리 가져옴

for i in range(6):

    #주소설정
    #주소는 맨뒤에 100~106까지 반복됨
    url = 'https://news.naver.com/section/10{}'.format(i)

    #가져온 주소 저장
    resp = requests.get(url)

    # html 문서로 변환
    soup = BeautifulSoup(resp.text, 'html.parser')

    #뉴스 제목 가져오기
    title_tags = soup.select('.sa_text_strong')

    # 각 제목을 리스트에 저장
    titles = []
    for title_tag in title_tags:
        title = title_tag.text # 태그에서 텍스트만 추출

        # 한글을 제외한 모든 문자 제거(특수문자, 숫자 포함)
        #가~힣까지를 제외한 나머지를 null값으로 대체
        title = re.compile('[^가-힣 ]').sub('',title)

        titles.append(title) # 리스트에 추가

    # 데이터프레임 생성 (컬럼: 제목, 카테고리)
    df_section_titles =pd.DataFrame(titles,columns=['titles'])
    df_section_titles['category'] = category[i]

    # 최종 데이터프레임에 카테고리별 뉴스 제목 추가
    df_titles = pd.concat([df_titles, df_section_titles],axis='rows',ignore_index=True)

# 데이터프레임 확인
print(df_titles.head())
df_titles.info()
print(df_titles['category'].value_counts())


# CSV 파일로 저장 (파일명: naver_headline_news_YYYYMMDD.csv)
#datetime.datetime.now() :현재 시간을 알려줌
df_titles.to_csv('./crawling_data/naver_headline_news{}.csv'.format(
    datetime.datetime.now().strftime('%Y%m%d')), index=False)

