# [더존 빵돌이] AI (pretzel)

🗞️ 빵돌이 뉴스레터

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Selenium](https://img.shields.io/badge/selenium-4.0+-green.svg)

🔍 빠르고 쉬운 웹 크롤링을 위한 파이썬 라이브러리입니다. Google 검색 결과와 웹 페이지 콘텐츠를 손쉽게 추출하세요.

## 주요 기능

- Google 검색 결과 수집
- 검색 결과 페이지 내용 추출
- 검색 결과의 제목, URL, 날짜, 설명 정보 제공
- 결과 파일 저장 기능
- PDF 파일도 인식하여 내용 추출 

## 설치 방법
```bash
pip install douzone_crawl
```
```bash
pip install requirements.txt
```

## 사용 방법

### 기본 사용 예시

```python
import douzone_crawl

# 크롤러 생성
crawler = douzone_crawl.DouzoneCrawler(max_results=2)

# 검색 실행
results = crawler.crawl("AI")

# 결과 저장
crawler.save_to_json(results)
```

### 다중 검색어 사용 예시

```python
import douzone_crawl

# 검색어 리스트
search_queries = ["더존빵돌이", "뉴스", "AI"]

crawler = douzone_crawl.DouzoneCrawler(max_results=2)

for query in search_queries:
    
    # 검색 실행
    results = crawler.crawl(query)
    
    # 결과 저장 (검색어별로 다른 파일에 저장)
    file_path = crawler.save_to_json(results, search_query=query)

print("모든 검색이 완료되었습니다.")
```

### 사용자 지정 경로 저장 예시

```python
import douzone_crawl

# 크롤러 생성
crawler = douzone_crawl.DouzoneCrawler(max_results=2)

# 검색 실행
results = crawler.crawl("AI")

# 결과 저장 (사용자 지정 디렉토리에)
crawler.save_to_json(results, directory="./data/search_results")

# 또는 파일명과 디렉토리를 모두 지정할 수도 있습니다.
crawler.save_to_json(results, filename="douzone_search.json", directory="C:/Users/username/Documents")
```

## 기여하기

- 버그 신고나 기능 제안은 이슈 트래커를 이용해 주세요. 풀 리퀘스트도 환영합니다!

