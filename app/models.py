from pydantic import BaseModel
from typing import List


class ChannelRequest(BaseModel):
    channel_link: str


class ChannelResponse(BaseModel):
    id: str
    channel_link: str
    channel_id: str
    channel_vector: List[float]
    related_channels: List[str] = []


class AddRelatedChannelRequest(BaseModel):
    related_channel_id: str
