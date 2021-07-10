# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

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
