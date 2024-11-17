import re
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from fastapi import HTTPException
from loguru import logger
from .config import MODEL_NAME

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)


def preprocess_text(text):
    """
    Функция для удаления специальных символов и приведение к нижнему регистру
    :param text:
    :return text:
    """
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    return text


def get_channel_message(bot, channel_link):
    """
    Функция для парсинга 100 последних сообщений из телеграм канала
    :param bot:
    :param channel_link:
    :return messages:
    """
    try:
        chat_id = channel_link.split('/')[-1]
        updates = bot.get_chat_history(chat_id, limit=100)
        messages = [update.message.text for update in updates if update.message and update.message.text]
        return messages
    except Exception as e:
        logger.error(f"Не получилось извлечь сообщения из канала {channel_link}: {e}")
        raise HTTPException(status_code=500, detail=f"Не получилось извлечь сообщения из канала {channel_link}")


def get_channel_vector(messages):
    """
    Делаем вектор канала основываясь ТОЛЬКО на 100 последних сообщениях
    :param messages:
    :return pooled_output:
    """
    if not messages:
        return np.zeros(model.config.hidden_size)

    preproc_messages = [preprocess_text(message) for message in messages]
    all_texts = " ".join(preproc_messages)

    inputs = tokenizer(all_texts, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.nograd():
        outputs = model(**inputs)

    last_hidden_states = outputs.last_hidden_state
    pooled_output = last_hidden_states.mean(dim=1).squeeze().numpy()
    return pooled_output
