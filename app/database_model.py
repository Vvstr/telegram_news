from mongoengine import Document, StringField, DictField, ListField


class Channel(Document):
    channel_id = StringField(required=True, unique=True)
    channel_link = StringField(required=True, unique=True)
    channel_name = StringField(required=True)
    channel_vector = DictField(default={})
    related_channels = ListField(StringField(), default=[])

    meta = {'collection': 'channels'}
