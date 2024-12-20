from hydrogram.types import Message

from src.database import (
    get_document_user_username,
    get_document_user_visibility,
    get_document_user_premium_status,
)


async def add_message_header(message: Message):  # _parser
    caption = message.caption or message.text
    if caption and caption.html:
        return f"**Unknown user** — hidden.\n{caption.html}"
    else:
        return "**Unknown user** — hidden."
    # username = await get_document_user_username(message.from_user.id)
    # user_visible = await get_document_user_visibility(message.from_user.id)
    # user_premium = await get_document_user_premium_status(message.from_user.id)
    
    # if not user_premium:
    #     symbol = "❖"
    # else:
    #     symbol = "✰"
    # if not user_visible:
    #     if not username:
    #         username =  "Edited by Unknown-user"
    #     if not caption or not caption.html:
    #         return f"**{symbol} {username}**"
    #     else:
    #         return f"**{symbol} {username}**\n{caption.html}"
    # else:
    #     if not caption or not caption.html:
    #         return f"{symbol} **Unknown user** — hidden."
    #     else:
    #         return f"{symbol} **Unknown user** — hidden.\n{caption.html}"
