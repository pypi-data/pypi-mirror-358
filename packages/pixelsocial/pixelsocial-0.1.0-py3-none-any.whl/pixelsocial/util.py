"""utilities"""

import base64
import json
from pathlib import Path

from deltachat2 import Bot, MessageViewtype, SpecialContactId
from sqlalchemy.future import select

from .orm import Post, session_scope

APP_VERSION = "0.4.0"
XDC_PATH = str(Path(__file__).parent / "app.xdc")


def upgrade_app(
    bot: Bot, accid: int, admin_chatid: int, chatid: int, msgid: int
) -> int:
    enc_data = bot.rpc.get_webxdc_blob(accid, msgid, "manifest.toml")
    version = ""
    for line in decode_base64(enc_data).decode().splitlines():
        if line.startswith("version"):
            version = line.replace('"', "").split("=")[1].strip()
            break
    if version != APP_VERSION:
        return send_app(bot, accid, admin_chatid, chatid)
    return 0


def send_app(bot: Bot, accid: int, admin_chatid: int, chatid: int) -> int:
    msgids = bot.rpc.get_chat_media(accid, chatid, MessageViewtype.WEBXDC, None, None)
    for msgid in msgids:
        msg = bot.rpc.get_message(accid, msgid)
        if msg.from_id == SpecialContactId.SELF:
            bot.rpc.delete_messages_for_all(accid, [msgid])

    bot.rpc.misc_set_draft(accid, chatid, None, XDC_PATH, None, None, None)
    msgid = bot.rpc.get_draft(accid, chatid).id
    isadmin = chatid == admin_chatid
    mode = {"selfId": str(chatid), "isAdmin": isadmin}
    if isadmin:
        chat = bot.rpc.get_basic_chat_info(accid, admin_chatid)
        mode["selfName"] = chat.name
    send_update(
        bot,
        accid,
        msgid,
        {"botMode": mode},
    )

    stmt = select(Post).order_by(Post.active).limit(100)
    with session_scope() as session:
        for post in session.execute(stmt).scalars():
            data = {
                "id": post.id,
                "authorName": post.authorname,
                "authorId": post.authorid,
                "isAdmin": post.isadmin,
                "date": post.date,
                "active": post.active,
                "text": post.text,
                "image": post.image,
                "style": post.style,
                "likes": 0,
                "replies": 0,
            }
            send_update(bot, accid, msgid, {"post": data})

            for reply in post.replies[:-100]:
                data = {
                    "id": reply.id,
                    "postId": reply.postid,
                    "authorName": reply.authorname,
                    "authorId": reply.authorid,
                    "isAdmin": reply.isadmin,
                    "date": reply.date,
                    "text": reply.text,
                }
                send_update(bot, accid, msgid, {"reply": data})

            for like in post.likes:
                data = {
                    "postId": like.postid,
                    "userId": like.userid,
                }
                send_update(bot, accid, msgid, {"like": data})

    bot.rpc.misc_send_draft(accid, chatid)
    return msgid


def send_update(bot: Bot, accid: int, msgid: int, payload: dict) -> None:
    payload["is_bot"] = True
    update = json.dumps({"payload": payload})
    bot.rpc.send_webxdc_status_update(accid, msgid, update, "")


def decode_base64(input_string: str) -> bytes:
    """Decode an unpadded standard or urlsafe base64 string to bytes."""

    input_bytes = input_string.encode("ascii")
    input_len = len(input_bytes)
    padding = b"=" * (3 - ((input_len + 3) % 4))

    # Passing altchars here allows decoding both standard and urlsafe base64
    output_bytes = base64.b64decode(input_bytes + padding, altchars=b"-_")
    return output_bytes
