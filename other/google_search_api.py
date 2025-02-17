import requests

def crawl_google_search(keywords, api_key, engine_id, num_results=3):
    """
    구글 검색 API를 사용하여 검색 결과를 크롤링하는 함수

    Args:
        keyword (str): 검색어
        api_key (str): 발급받은 API 키
        engine_id (str): 생성한 검색 엔진 ID
        num_results (int, optional): 검색 결과 개수. Defaults to 10.

    Returns:
        list: 검색 결과 (제목, 링크) 목록
    """

    results = {}
    for keyword in keywords:
        
        # 전체 검색
        # url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={engine_id}&q={keyword}&num={num_results}" 

        # 뉴스만 검색
        url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={engine_id}&q={keyword}&num={num_results}&tbm=nws" 

        response = requests.get(url)
        data = response.json()

        keyword_results = []
        if data.get("items"):
            for item in data["items"]:
                title = item["title"]
                link = item["link"]
                # snippet = item["snippet"]
                keyword_results.append({"title": title, "link": link})

        results[keyword] = keyword_results

    return results

if __name__ == "__main__":
    keywords = ["더존비즈온", "AI", "정치"] 
    api_key = "AIzaSyCLuz-F_YF2xRPoWSZxfYlIZpVTikqjmRY"  # 발급받은 API 키를 입력하세요 / 하루에 100 검색어 무료
    engine_id = "069b08dd3f3e24678"  # 생성한 검색 엔진 ID를 입력하세요

    results = crawl_google_search(keywords, api_key, engine_id)

    for keyword, keyword_results in results.items():
        if keyword_results:
            print(f"'{keyword}' 검색 결과:")
            for result in keyword_results:
                print(f"- {result['title']}")
                print(f"  {result['link']}")
                # print(f"  {result['snippet']}")
        else:
            print(f"'{keyword}' 검색 결과가 없습니다.")


