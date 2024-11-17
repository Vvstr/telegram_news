from typing import Any

from fastapi import HTTPException, FastAPI
from telegram import Bot
from bson import ObjectId
from .config import TELEGRAM_BOT_TOKEN
from .models import ChannelRequest, ChannelResponse, AddRelatedChannelRequest
from .utils import get_channel_message, get_channel_vector
from .database import save_channel, get_channel_by_id, get_all_channels, get_channel_by_link, update_channel
from loguru import logger

app = FastAPI()

bot = Bot(token=TELEGRAM_BOT_TOKEN)


@app.post("/parse_channel/", response_model=ChannelResponse)
async def parse_channel(request: ChannelRequest):
    try:
        messages = get_channel_message(bot, request.channel_link)
        channel_vector = get_channel_vector(messages)

        chat_id = request.channel_link.split('/')[-1]
        chat = bot.get_chat(chat_id)
        channel_name = chat.title

        existing_channel = get_channel_by_link(request.channel_link)
        if existing_channel:
            update_data = {
                "channel_vector": channel_vector.to_list(),
                "related_channels": existing_channel.get("related_channels", [])
            }
            update_channel(ObjectId(existing_channel["_id"]), update_data)
            return {
                "id": str(existing_channel["_id"]),
                "channel_link": request.channel_link,
                "channel_name": channel_name,
                "channel_vector": channel_vector.to_list(),
                "related_channels": existing_channel.get("related_channels", [])
            }

        # Сохраняем новый канал в базу данных
        channel_data = {
            "channel_link": request.channel_link,
            "channel_name": channel_name,
            "channel_vector": channel_vector.to_list(),
            "related_channels": []
        }
        channel_id = save_channel(channel_data)

        return {
            "id": channel_id,
            "channel_link": request.channel_link,
            "channel_name": channel_name,
            "channel_vector": channel_vector.tolist(),
            "related_channels": []
        }

    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        raise HTTPException(status_code=500, detail="Неожиданная внутрення ошибка сервера")


@app.get("/channels/{channel_id}", response_model=ChannelResponse)
async def get_channel(channel_id: str):
    """
    Функция для получения всей инфы о кнаале по его id
    :param channel_id:
    :return ChannelResponse:
    """
    try:
        channel = get_channel_by_id(ObjectId(channel_id))
        if channel is None:
            raise HTTPException(status_code=404, detail="Канала с таким id не существует")

        return {
            "id": str(channel["_id"]),
            "channel_link": channel["channel_link"],
            "channel_name": channel["channel_name"],
            "channel_vector": channel["channel_vector"],
            "related_channels": channel.get("related_channels", [])
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Рандом ошибка xD {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.get("/channels", response_model=list[ChannelResponse])
async def get_all_channels():
    """
    Функция для получения всех каналов из БД
    :return Список объектов со всей информацией о каналах:
    """
    try:
        channels = get_all_channels()
        return [
            {
                "id": str(channel["_id"]),
                "channel_link": channel["channel_link"],
                "channel_name": channel["channel_name"],
                "channel_vector": channel["channel_vector"],
                "related_channels": channel.get("related_channels", [])
            }
            for channel in channels
        ]
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise HTTPException(status_code=500)


@app.put("/channels/{channel_id}/add_related/", response_model=ChannelResponse)
async def add_related_channels(channel_id: str, request: AddRelatedChannelRequest) -> dict[str, str | Any]:
    """
    Добавляет 'связанные' каналы к уже существующему
    :param channel_id: ID канала
    :param request: Запрос с ID связанного канала
    :return: Обновление данных канала*
    :raises HTTPException: В случае рандомных ошибок БД, ну или если канала не существует
    """
    try:
        channel = get_channel_by_id(ObjectId(channel_id))
        if channel is None:
            raise HTTPException(status_code=404, detail=f"Канала с id {channel_id} не существует")
        related_channel_id = request.related_channel_id
        related_channel = get_channel_by_id(ObjectId(related_channel_id))

        # Проверка наличия связанного канал в списке связанных каналов
        related_channels = channel.get("related_channels", [])
        if related_channel_id in related_channels:
            raise HTTPException(status_code=500, detail=f"Связанный канал с таким id уже добавлен")

        related_channels.append(related_channel_id)
        updated_data = {
            "related_channels": related_channel
        }

        update_channel(channel_id, updated_data)

        return {
            "id": str(channel["_id"]),
            "channel_link": channel["channel_link"],
            "channel_name": channel["channel_name"],
            "channel_vector": channel["channel_vector"],
            "related_channels": related_channels
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Рандом ошибка xD {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
