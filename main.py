from fastapi import FastAPI
import uvicorn
from trending_news import crawl_trending_news
from pymongo import MongoClient
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import pytz

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# MongoDB 연결
MONGODB_URL = "mongodb+srv://hjcho1027:breadkun12@breadkun.9dcyorh.mongodb.net/?retryWrites=true&w=majority&appName=breadkun"
client = MongoClient(MONGODB_URL)
db = client["breadkun_db"]
collection = db["trending_news"]

# 스케줄러 초기화
scheduler = AsyncIOScheduler()

async def auto_crawl_news():
    """매일 오전 9시에 자동으로 뉴스 크롤링"""
    try:
        logger.info("자동 뉴스 크롤링 시작...")
        news_list = crawl_trending_news(10)  # 10개 뉴스 크롤링
        
        if news_list:
            news_for_db = []
            for news in news_list:
                news_copy = news.copy()
                news_copy['created_at'] = datetime.now()
                news_for_db.append(news_copy)
            
            collection.insert_many(news_for_db)
            logger.info(f"자동 크롤링으로 {len(news_for_db)}개 뉴스 저장 완료")
        else:
            logger.warning("자동 크롤링에서 뉴스를 찾을 수 없음")
            
    except Exception as e:
        logger.error(f"자동 크롤링 중 오류 발생: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 스케줄러 시작"""
    try:
        # 한국 시간 기준으로 설정
        kst = pytz.timezone('Asia/Seoul')
        # 매일 오전 9시에 실행
        scheduler.add_job(
            auto_crawl_news,
            trigger=CronTrigger(hour=9, minute=0),
            id='daily_news_crawl',
            name='매일 오전 9시 뉴스 크롤링',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("스케줄러 시작: 매일 오전 9시에 뉴스를 자동 크롤링합니다.")
        
    except Exception as e:
        logger.error(f"스케줄러 시작 중 오류 발생: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료 시 스케줄러 종료"""
    scheduler.shutdown()
    logger.info("스케줄러 종료됨")

@app.get("/breadkun_treding_news")
async def get_news(count: int = 4):
    # 뉴스 크롤링
    news_list = crawl_trending_news(count)
    
    # MongoDB에 저장
    if news_list:
        # 저장용 데이터 복사 (원본 데이터 보존)
        news_for_db = []
        for news in news_list:
            news_copy = news.copy()
            news_copy['created_at'] = datetime.now()
            news_for_db.append(news_copy)
        
        collection.insert_many(news_for_db)
    
    # 원본 데이터 반환 (ObjectId 없음)
    return news_list

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)