# @Kakashi_HTK(tg)/@ashwinstr(gh)/@applled


from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import (
    InputPeerUserFromMessage,
    InputReportReasonPornography,
    InputReportReasonSpam,
)


# capitalise
def capitaled(query: str):
    query_split = query.split()
    cap_text = []
    for word_ in query_split:
        word_cap = word_.capitalize()
        cap_text.append(word_cap)
    cap_query = " ".join(cap_text)
    return cap_query


# Report para denunciar spam/conteúdo adulto
def report_user(chat: int, user_id: int, msg: dict, msg_id: int, reason: str):
    if ("nsfw" or "porn") in reason:
        reason_ = InputReportReasonPornography()
        for_ = "<b>Conteúdo</b> adulto"
    else:
        reason_ = InputReportReasonSpam()
        for_ = "Mensagem de <b>Spam</b>"
    peer_ = (
        InputPeerUserFromMessage(
            peer=chat,
            msg_id=msg_id,
            user_id=user_id,
        ),
    )
    ReportPeer(
        peer=peer_,
        reason=reason_,
        message=msg,
    )
    return for_
