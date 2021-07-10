from userge import Config, Message, userge

@userge.on_cmd("repo", about={"header": "Link do Repo"})
async def see_repo(message: Message):
    """ Repo do AppleBot """    
    photo = "https://telegra.ph/file/a1876d2c20937b9e5e78e.png"
    texto = f"• **Tchamram!**: [AppleBot]({Config.UPSTREAM_REPO})"
    await message.client.send_animation(
                         message.chat.id, 
                         animation=photo, 
                         caption=texto,
    )
