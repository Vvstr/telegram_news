import os
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")
MODEL_NAME = os.getenv("cointegrated/rubert-tiny2")
