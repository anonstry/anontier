# @client.on_message(filters.private & filters.command("bomb"))
# async def registra_mensagem_bomba(client: Client, message: Message):
#     # pessoa clicar num botão que dê acesso ao bot, talvez como um link de afiliado
#     # apenas uma midia por pessoa e por vez
#     username = int(message.command[1])
#     message_address = make_message_address(message.chat.id, message.id)
#     criar_sessao.mensagens_bombas[username] = message_address

# @client.on_message(filters.private & filters.command("explode"))
# async def pega_mensagem_bomba(client: Client, message: Message):
#     # pessoa clicar num botão que dê acesso ao bot, talvez como um link de afiliado
#     # apenas uma midia por pessoa e por vez
#     receive_message_address = criar_sessao.mensagens_bombas[message.from_user.id]
#     criar_sessao.mensagens_bombas[message.from_user.id] = None
#     try:
#         chat_id, message_id = resolve_message_address(receive_message_address)
#         receive_message = await client.copy_message(message.from_user.id, chat_id, message_id, protect_content=True)
#         a = await receive_message.reply("Here is a dropped media for you")
#         await sleep(60*1.5)
#         await receive_message.delete()
#         await a.delete()
#     except:
#         ...