from fastapi import FastAPI
import uvicorn
from trending_news import crawl_trending_news

app = FastAPI()

@app.get("/breadkun_treding_news")
async def get_news(count: int = 4):
    news_list = crawl_trending_news(count)
    return news_list

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    
# 뉴스 개수를 지정하고 싶다면 http://localhost:8000/news?count=10 사용.
# 지금은 4개로 고정.