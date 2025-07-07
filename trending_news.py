import requests
from bs4 import BeautifulSoup

def crawl_trending_news(num_results):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    url = "https://news.google.com/?hl=ko&gl=KR&ceid=KR:ko"  # 한국어 Google News 메인 페이지
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    news_list = []
    for i, item in enumerate(soup.find_all("div", class_="KDoq1")): # article 태그와 클래스명으로 변경 m5k28
        if i > num_results:
            break

        a_tag = item.find("a", class_="gPFEn") # a 태그와 클래스명으로 변경
        if a_tag:
            title = a_tag.text.strip()
            link = a_tag["href"]

            if link.startswith("./"):
                link = "https://news.google.com" + link[1:]
                
            news_list.append({"title": title, "link": link})

    for i, item in enumerate(soup.find_all("div", class_="m5k28")): 
        if i > num_results:
            break

        a_tag = item.find("a", class_="JtKRv") # a 태그와 클래스명으로 변경
        if a_tag:
            title = a_tag.text.strip()
            link = a_tag["href"]

            if link.startswith("./"):
                link = "https://news.google.com" + link[1:]
                
            news_list.append({"title": title, "link": link})

    return news_list