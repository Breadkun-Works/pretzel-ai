from fastapi import FastAPI
import keyword_based_pretzel_ai
import uvicorn

app = FastAPI()

@app.get("/newsletter")
async def get_newsletter():
    keyword_based_pretzel_ai.main()
    return {"message": "Newsletter generated successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)