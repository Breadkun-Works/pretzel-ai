import feedparser
import datetime
import os
from dotenv import load_dotenv
from pydantic.v1 import BaseSettings
from openai import AzureOpenAI
import requests

from selenium import webdriver 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By

load_dotenv()

class Settings(BaseSettings):
    debug: bool = False
    environment: str = "OPENAI_API_KEY"

    DOBBY_OPENAI_API_KEY: str
    DOBBY_OPENAI_API_BASE: str
    DOBBY_OPENAI_API_TYPE: str
    DOBBY_OPENAI_API_VERSION: str
    DOBBY_OPENAI_DEPLOYMENT_NAME: str
    DOBBY_OPENAI_EMBEDDING_DEPLOYMENT_NAME: str

    class Config:
        env_file = ".env"

settings = Settings()

os.environ["AZURE_OPENAI_API_KEY"] = getattr(settings, f"DOBBY_OPENAI_API_KEY")
os.environ["AZURE_OPENAI_ENDPOINT"] = getattr(settings, f"DOBBY_OPENAI_API_BASE")
os.environ["OPENAI_API_TYPE"] = getattr(settings, f"DOBBY_OPENAI_API_TYPE")
os.environ["OPENAI_API_VERSION"] = getattr(settings, f"DOBBY_OPENAI_API_VERSION")
os.environ["OPENAI_DEPLOYMENT_NAME"] = getattr(settings, f"DOBBY_OPENAI_DEPLOYMENT_NAME")
os.environ["OPENAI_EMBEDDING_DEPLOYMENT_NAME"] = getattr(settings, f"DOBBY_OPENAI_EMBEDDING_DEPLOYMENT_NAME")

release = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
version = requests.get(release).text


# ============================ 매개 변수 설정 ============================
"""후보 기사들 중 관련도 높은 top_k개 기사를 추출"""

# 후보 기사에서 가져올 최종 기사 개수
top_k = 5
# api가 가져올 후보 기사의 개수
all_arti = 30    
#======================================================================

def genAI(srcText):
    articles = create_title_link_list(srcText, all_arti)
    # title과 url을 딕셔너리 형태로 변환
    dict_articles = [{"title": title, "url": url, "date": date} for title, url, date in articles] 
    # title만 추출
    titles = [item["title"] for item in dict_articles] 

    print(f'------------------------------- [정렬 전 기사 리스트 {all_arti}개] -------------------------------')
    print(titles)

    # GPT 4o 
    client = AzureOpenAI(azure_deployment=os.getenv("OPENAI_DEPLOYMENT_NAME"), default_headers={"Ocp-Apim-Subscription-Key": os.environ["AZURE_OPENAI_API_KEY"]})

    rel_sort_prompt = """
                # 출력 작성 형식 예시
                ```python
                ['titleA', 'titleB', 'titleC', ...]
                ```
                파이썬 리스트 형태의 이 출력 작성 형식을 유지해줘. 
                'title'의 양쪽 끝에는 항상 [ ] 이 중괄호로 닫혀있어야 한다. 
                전체 기사의 제목을 보고 'AI','최신 기술','인공지능','기업' 키워드와 가장 관련도가 높은 순으로 정렬해서 중복된 내용이 아닌 10개의 기사를 출력해줘.
                관련도가 높은 10개의 기사는 서로 중복되지 않아야 한다.
                """
    
    # 관련도 순으로 정렬
    response = client.chat.completions.create(        
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "넌 뉴스레터 어시스턴트야. '최신 기술', '인공지능', '개발', '" + srcText + "' 등 AI 기술 소식 위주의 뉴스를 정렬해줘."},
            {"role": "user", "content": "# 타이틀 리스트: \n" + str(titles) + rel_sort_prompt}
        ],
        max_tokens=4096,
        temperature= 0.3
    )
    
    # 관련도 순으로 정렬된 결과
    assistant = response.choices[0].message.content
    return assistant

def create_title_link_list(srcText, all_arti):

    url = f"https://news.google.com/rss/search?q={srcText}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)

    title_link_list = []

    # 기사 제목, 링크 추출 (최신순)
    for i, entry in enumerate(feed.entries[:all_arti], 1):   
        title_link_list.append((entry.title, entry.link, entry.published))  # 제목, 링크, 발행일

    return title_link_list

def extract_news_content(url):
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless=new') # 크롬 창이 보이지 않게
    chrome_options.add_argument('--no-sandbox') # 샌드박스 비활성화로 성능 향상
    chrome_options.add_argument('--disable-dev-shm-usage') # 메모리 사용 최적화
    chrome_options.add_argument('--disable-gpu') # GPU 가속 비활성화
    chrome_options.add_argument('--window-size=1920x1080') # 가상 브라우저 창 크기 설정
    chrome_options.add_argument("--disable-notifications") # 알림 비활성화

    driver= webdriver.Chrome(service=Service(), options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(10)

    # 뉴스 사이트별 본문 CSS 선택자 매핑
    content_selectors = {
        "articletxt": "id",  # 한국경제
        "article-body": "class",  # 조선일보
        "story-news article": "class",  # 연합뉴스
        "article-view-content-div": "class",  # 법률저널, 포춘코리아
        "next-news-contents news-highlight-box": "class",  # 위시켓
        "art_body": "class",  # 경향신문
        "article_txt": "class",  # 전자신문
        "article_content": "class",  # 디지털데일리
        "read-news-main-contents": "class",  # 딜사이트
        "article_body": "class",  # 이코노미스트
        "articleView": "class",  # 이투데이
        "news-contents": "class",  # 뉴스핌
        "content": "class",  # nvidia
        "detail_editor": "class",  # 비즈니스포스트
        "article_con": "class",  # 아주경제
        "articleBody": "class",  # 아주경제 대체
        "detail-body font-size": "class",  # KBS
        "article-text": "class",  # 한겨례
        "news_detail_cont": "class",  # 내손안에 서울
        "cnt_view news_body_area": "class",  # 더구루
        "contents": "class",  # 뉴스핌
        "postContent": "class",  # 비즈니스포스트
        "conPost": "class",  # 비즈니스포스트
        "view_cont": "class"  # ZD넷 코리아
    }
    
    article_text = []

    try:
        # 각 선택자를 순회하며 본문 찾기
        for selector, selector_type in content_selectors.items():
            if selector_type == "id":
                article = driver.find_elements(By.ID, selector)
            else:  # class
                article = driver.find_elements(By.CLASS_NAME, selector)
            
            if article:
                # 본문을 찾았으면 텍스트 추출 후 반복 종료
                for articles in article:
                    article_text.append(articles.text)
                break
        
        if not article_text:
            print('해당 언론사는 뉴스레터에 정의되어 있지 않기 때문에 기사 본문 내용을 읽어올 수 없습니다.')

    except Exception as e:
        print(f"본문 가져오기 실패: {str(e)}")
        import pdb; pdb.set_trace()
    
    finally:
        driver.quit()

    return article_text

def create_newsletter(srcText):

    articles = create_title_link_list(srcText, all_arti)
    assistant = genAI(srcText)
    dict_articles = [{"title": title, "url": url, "date": date} for title, url, date in articles]

    # 정규화
    output_string = assistant.replace("```python", "").replace("```", "").replace("\n", "").replace("･", "").replace("…", "")

    print('************* 정규화 진행한 후 *************')
    print(output_string) 

    try:
        article = eval(output_string) # str to list

    except:
        print('포맷 ERROR')
        assistant_re = genAI(srcText)
        output_string_re = assistant_re.replace("```python", "").replace("```", "").replace("\n", "").replace("･", "").replace("…", "")
            
        article = eval(output_string_re)
        print(output_string_re)
        print(article)
    
    print('************* 리스트로 변환 후 *************')
    print(article)
    print('************* 출력된 두 내용이 같은지 확인하세요. 이 문장이 출력되면 정상입니다 d^o^b *************\n\n')

    new_list = []
    for title in article:
        for item in dict_articles:
            if title == item['title']:
                new_entry = {"title": title, "url": item['url'], "date": item['date']}
                new_list.append(new_entry)
                break
    article = [(item['title'], item['url'], item['date']) for item in new_list]

    # 뉴스레터 생성
    newsletter = f"======================== '{srcText.upper()}' 관련 최신 뉴스 (RSS ver.) ========================\n\n"
    newsletter += f"뉴스 레터 생성 시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # 기사 추가
    # 관련도 순으로 정렬된 기사 중 상위 n개 기사만 출력
    for title, link, date in article[:top_k]:  
        newsletter += f" 제목 : {title}\n"
        newsletter += f" 링크 : {link}\n"
        newsletter += f" 발행일 : {date}\n"
        
        # 본문 top_k만큼 가져오기
        summary = extract_news_content(link) 
        
        client = AzureOpenAI(azure_deployment=os.getenv("OPENAI_DEPLOYMENT_NAME"), default_headers={"Ocp-Apim-Subscription-Key": os.environ["AZURE_OPENAI_API_KEY"]})
        response2 = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[    # 뉴스 본문에 대한 3줄 요약문.
                        {"role": "system", "content": "넌 뉴스레터 어시스턴트야."},
                        {"role": "user", "content": str(summary) + "해당 내용을 중요한 3문장으로 요약해줘. 요약문은 한문장씩 줄바꿈하여 출력해줘. 기사의 본문이 존재하지 않는 경우, '기사 본문 확인 불가' 라고 1회 출력해줘."}
                    ],
                    temperature=0.1
                )
        assistant2 = response2.choices[0].message.content

        if assistant2 == '기사 본문 확인 불가':  
            pass 
        else:
            newsletter += f" 본문 요약 : {assistant2}\n\n\n"

    return newsletter

def save_newsletter(content, filename):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(content)

def main():

    srcText_list = ["AI"]   # 검색어
    for srcText in srcText_list:
        print('[' +srcText+ '] 에 대한 뉴스 검색을 진행합니다.')
        news = create_newsletter(srcText)
        
        save_newsletter(news, "ai_뉴스레터 " + srcText +"_" + datetime.datetime.now().strftime('%Y-%m-%d') + ".txt")
        print(news) 
        print("=" * 100)

if __name__ == "__main__":
    main()