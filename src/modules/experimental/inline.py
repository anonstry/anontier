# from hydrogram.types import Message
# from loguru import logger
# from hydrogram import filters
from hydrogram.client import Client
from hydrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

# The max size for a url parameter is 64


@Client.on_inline_query()
async def answer(client, inline_query):
    await inline_query.answer(
        results=[
            InlineQueryResultArticle(
                title="Send a invite to your room",
                input_message_content=InputTextMessageContent(
                    "Here's how to install **Pyrogram**"
                ),
                # url="https://docs.pyrogram.org/intro/install",
                description="Drop a mail with a sweet invite",
                # reply_markup=InlineKeyboardMarkup(
                #     [
                #         [
                #             InlineKeyboardButton(
                #                 "Open website",
                #                 url="https://docs.pyrogram.org/intro/install",
                #             )
                #         ]
                #     ]
                # ),
                thumb_url="https://i.pinimg.com/564x/c6/1e/f6/c61ef693861205434c339369c8b0fca9.jpg",
            ),
            InlineQueryResultArticle(
                title="Invite people to use the bot",
                input_message_content=InputTextMessageContent(
                    "Here's how to install **Pyrogram**"
                ),
                # url="https://docs.pyrogram.org/intro/install",
                description="Share the access for more ghosts",
                # reply_markup=InlineKeyboardMarkup(
                #     [
                #         [
                #             InlineKeyboardButton(
                #                 "Open website",
                #                 url="https://docs.pyrogram.org/intro/install",
                #             )
                #         ]
                #     ]
                # ),
                thumb_url="https://i.pinimg.com/564x/bf/c3/5c/bfc35c79b830f564b8b92105f23ff106.jpg",
            ),
            InlineQueryResultArticle(
                title="Usage",
                input_message_content=InputTextMessageContent(
                    "Here's how to use **Pyrogram**"
                ),
                url="https://docs.pyrogram.org/start/invoking",
                description="How to use Pyrogram",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Open website",
                                url="https://docs.pyrogram.org/start/invoking",
                            )
                        ]
                    ]
                ),
            ),
        ],
        cache_time=1,
    )
