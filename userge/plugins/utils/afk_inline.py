from userge import Message, userge


async def send_inline_afk(message: Message):
    bot = await userge.bot.get_me()
    x = await userge.get_inline_bot_results(bot.username, "afk")
    await userge.send_inline_bot_result(
        chat_id=message.chat.id,
        query_id=x.query_id,
        result_id=x.results[0].id,
        hide_via=True,
    )


async def send_inline_afk_(message: Message):
    bot_ = await userge.bot.get_me()
    x_ = await userge.get_inline_bot_results(bot_.username, "afk_")
    await userge.send_inline_bot_result(
        chat_id=message.chat.id,
        query_id=x_.query_id,
        result_id=x_.results[0].id,
        hide_via=True,
    )


async def _send_inline_afk_(message: Message):
    _bot = await userge.bot.get_me()
    _x = await userge.get_inline_bot_results(_bot.username, "_afk_")
    await userge.send_inline_bot_result(
        chat_id=message.chat.id,
        query_id=_x.query_id,
        result_id=_x.results[0].id,
        hide_via=True,
    )
