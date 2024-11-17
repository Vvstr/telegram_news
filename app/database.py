from pymongo import MongoClient
from pymongo.errors import PyMongoError
from loguru import logger
from .config import MONGODB_URI
from fastapi import HTTPException


client = MongoClient(MONGODB_URI)
db = client["telegram_channels"]
collection = db['channels']


def save_channel(channel_data):
    try:
        result = collection.insert_one(channel_data)
        return str(result)
    except Exception as e:
        logger.error(f"Ошибка базы данных {e}")
        raise HTTPException(status_code=500, detail="Ошибка базы данных")


def get_channel_by_id(channel_id):
    try:
        channel = collection.find_one({"channel_id": channel_id})
        return channel
    except Exception as e:
        logger.error(f"Ошибка базы данных {e}")
        raise HTTPException(status_code=500, detail="Ошибка базы данных")


def get_channel_by_link(channel_link):
    try:
        channel = collection.find_one({"channel_link": {channel_link}})
        return channel
    except Exception as e:
        logger.error(f"Ошибка базы данных {e}")
        raise HTTPException(status_code=500, detail="Ошибка базы данных")


def get_all_channels():
    try:
        channels = collection.find()
        return list(channels)
    except Exception as e:
        logger.error(f"Ошибка базы данных {e}")
        raise HTTPException(status_code=500, detail="Ошибка базы данных")


def update_channel(channel_id, update_data):
    try:
        result = collection.find_one({"channel_id": {channel_id}})
        return result.modified_count > 0
    except PyMongoError as e:
        logger.error(f"Ошибка базы данных {e}")
        raise HTTPException(status_code=500, detail="Ошибка базы данных")
