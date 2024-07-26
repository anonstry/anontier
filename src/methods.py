from hydrogram.client import Client
from hydrogram.types import (
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
)
from hydrogram.types.messages_and_media.animation import Animation
from hydrogram.types.messages_and_media.audio import Audio
from hydrogram.types.messages_and_media.document import Document
from hydrogram.types.messages_and_media.photo import Photo
from hydrogram.types.messages_and_media.video import Video


def return_thumbnail_file_id(message_media) -> str:
    try:
        file_id = (message_media.thumbs[0].file_id,)
        assert isinstance(file_id, str)
        return file_id
    except (IndexError, AttributeError, AssertionError):
        return str()  # Empty string


async def mount_input_media(client: Client, from_message: Message, message_media):
    if isinstance(message_media, Audio):
        return InputMediaAudio(
            media=message_media.file_id,
            thumb=return_thumbnail_file_id(message_media),
            caption=from_message.caption,
            parse_mode=client.parse_mode,
            caption_entities=from_message.caption_entities,
            duration=message_media.duration,
            performer=message_media.performer or str(),
            title=message_media.title or str(),
        )
    elif isinstance(message_media, Photo):
        return InputMediaPhoto(
            media=message_media.file_id,
            caption=from_message.caption,
            parse_mode=client.parse_mode,
            caption_entities=from_message.caption_entities,
            has_spoiler=from_message.has_media_spoiler,
        )
    elif isinstance(message_media, Video):
        return InputMediaVideo(
            media=message_media.file_id,
            thumb=return_thumbnail_file_id(message_media),
            caption=from_message.caption,
            parse_mode=client.parse_mode,
            caption_entities=from_message.caption_entities,
            width=message_media.width,
            height=message_media.height,
            duration=message_media.duration,
            supports_streaming=bool(message_media.supports_streaming),
            has_spoiler=from_message.has_media_spoiler,
        )
    elif isinstance(message_media, Document):
        return InputMediaDocument(
            media=message_media.file_id,
            thumb=return_thumbnail_file_id(message_media),
            caption=from_message.caption,
            parse_mode=client.parse_mode,
            caption_entities=from_message.caption_entities,
        )
    elif isinstance(message_media, Animation):
        return InputMediaAnimation(
            media=message_media.file_id,
            thumb=return_thumbnail_file_id(message_media),
            caption=from_message.caption,
            parse_mode=client.parse_mode,
            caption_entities=from_message.caption_entities,
            width=message_media.width,
            height=message_media.height,
            duration=message_media.duration,
            has_spoiler=from_message.has_media_spoiler,
        )
    else:  # Message type is unknown and can be send as document
        return None
