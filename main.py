from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

from fastapi import FastAPI
from backend.app.api.endpoints import router

app = FastAPI()
app.include_router(router)