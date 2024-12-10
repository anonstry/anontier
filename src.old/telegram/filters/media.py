# Talvez, se a mídia for um story, ela possa ser baixada e enviada

from hydrogram import filters

async def filter_media_copiable(_, __, message):
    if (
        not message.photo
        or not message.audio
        or not message.audio.file_id
        or not message.document
        or not message.video
    ):
        return False  # The media is not copiable
    else:
        return True

filter_copiable = filters.create(filter_media_copiable)