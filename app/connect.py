from mongoengine import connect


connect(db='telegram_channels', host='mongodb://localhost:27017/')