from userge import Config, Message, userge


@userge.on_cmd("repo", about={"título": "Link do Repo"})
async def see_repo(message: Message):
    """Repo do AppleBot"""
    photo = "https://telegra.ph/file/7bb8468e6287512183459.gif"
    texto = f"• **Tchamram!**: [AppleBot]({Config.UPSTREAM_REPO})"
    await message.client.send_animation(
        message.chat.id,
        animation=photo,
        caption=texto,
    )
