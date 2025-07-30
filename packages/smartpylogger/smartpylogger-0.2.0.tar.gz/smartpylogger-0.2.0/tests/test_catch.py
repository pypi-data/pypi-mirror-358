from smartpylogger import LoggingMiddleware
from fastapi import FastAPI, Request
import requests
import os
import dotenv

dotenv.load_dotenv()

app = FastAPI()
print(os.getenv("API_KEY"))

# Get the absolute path to the banned words file
current_dir = os.path.dirname(os.path.abspath(__file__))
banned_words_path = os.path.join(current_dir, "my_banned_words.txt")

app.add_middleware(
    LoggingMiddleware,
    api_key=os.getenv("API_KEY"),  # This is where the middleware would forward, but the app itself runs on 8500
    allowed_origins=["127.0.0.1"],
    api_limit_daily=1000,
    banned_words_path=banned_words_path
)

API_URL = "http://localhost:8500"

@app.post("/mock")
async def mock_post(request: Request):
    data = await request.json()
    return {"received": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8500)