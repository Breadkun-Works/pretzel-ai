from fastapi import FastAPI
import keyword_search.ai_crawl_keyword as ai_crawl_keyword
import uvicorn

app = FastAPI()

@app.get("/newsletter")
async def get_newsletter():
    ai_crawl_keyword.main()
    return {"message": "Newsletter generated successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)