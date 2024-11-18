from pymongo.errors import PyMongoError
from loguru import logger
from fastapi import HTTPException
from database_model import Channel
from bson import ObjectId


def save_channel(channel_data):
    try:
        channel= Channel(
            channel_id=str(ObjectId()),
            channel_link=channel_data['channel_link'],
            channel_name=channel_data['channel_name'],
            channel_vector=channel_data['channel_vector'],
            related_channels=channel_data.get('related_channels', [])
        )
        Channel.save()
        return {"id": str(channel.id), "channel_id": str(channel.channel_id)}
    except Exception as e:
        logger.error(f"Ошибка базы данных {e}")
        return HTTPException(status_code=500, detail="Ошибка базы данных")


def get_channel_by_id(channel_id):
    try:
        channel = Channel.objects(channel_id=channel_id).first()
        return channel
    except Exception as e:
        logger.error(f"Ошибка базы данных {e}")
        raise HTTPException(status_code=500, detail="Ошибка базы данных")


def get_channel_by_link(channel_link):
    try:
        channel = Channel.objects(channel_link=channel_link).first()
        return channel
    except Exception as e:
        logger.error(f"Ошибка базы данных {e}")
        raise HTTPException(status_code=500, detail="Ошибка базы данных")


def get_all_channels():
    try:
        channels = Channel.objects.all()
        return channels
    except Exception as e:
        logger.error(f"Ошибка базы данных {e}")
        raise HTTPException(status_code=500, detail="Ошибка базы данных")


def update_channel(channel_id, update_data):
    try:
        channel = Channel.objects(channel_id=channel_id).first()
        if channel is None:
            return False
        for key, value in enumerate(update_data):
            setattr(channel, key, value)
        channel.save()
        return True
    except Exception as e:
        logger.error(f"Ошибка базы данных {e}")
        raise HTTPException(status_code=500, detail="Ошибка базы данных")
