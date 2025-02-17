import requests
from bs4 import BeautifulSoup

def crawl_news(keyword, num_results):
    """
    구글링 검색 연산자를 활용하여 뉴스 기사를 크롤링하는 함수

    Args:
        keyword (str): 검색어
        num_results (int, optional): 검색 결과 개수

    Returns:
        list: 뉴스 기사 제목과 링크 목록
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    query = keyword

    url = f"https://www.google.com/search?q={query}&tbm=nws" # 뉴스
    print(url)

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    news_list = []
    for i, item in enumerate(soup.find_all("div", class_="Gx5Zad")):
        if i > num_results:
            break  # 원하는 개수만큼만 추출

        a_tag = item.find("a")
        if a_tag:
            title_div = a_tag.find("div", class_="vvjwJb")
            if title_div:
                title = title_div.text.strip()
                link = a_tag["href"]
                news_list.append({"title": title, "link": link}) 

    return news_list

if __name__ == "__main__":
    keyword = input("검색어를 입력하세요: ")
    num_results = int(input("검색 결과 개수를 입력하세요: "))  # 검색 결과 개수 입력 받기
    news_list = crawl_news(keyword, num_results)  # 검색 결과 개수 전달

    if news_list:
        print(f"'{keyword}' 검색 결과 ({len(news_list)}개):")
        for news in news_list:
            print(f"- {news['title']}")
            print(f"  {news['link']}")
    else:
        print("검색 결과가 없습니다.")