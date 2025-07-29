import aiohttp
import typing

async def get_image(image: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        result = await session.get(
            url=f"https://chat-img.jwznb.com/{image}",
            headers={
                "Referer": "https://www.yhchat.com"
            }
        )
        imc = await result.read()
    return imc

async def send_text_message(
        token: str,
        recvType: typing.Literal["user", "group"],
        recvId: str,
        message: str,
        messageType: typing.Literal["text", "markdown", "html"],
        buttons: list[dict]
    ) -> str:
    async with aiohttp.ClientSession() as session:
        result = await session.post(
            url=f"https://chat-go.jwzhd.com/open-apis/v1/bot/send?token={token}",
            json={
                "recvId": recvId,
                "recvType": recvType,
                "contentType": messageType,
                "content": {
                    "text": message,
                    "buttons": buttons
                }
            }
        )
        jsond = await result.json()
    return jsond["data"]["messageInfo"]["msgId"]

async def modify_text_message(
        token: str,
        msgId: str,
        recvType: typing.Literal["user", "group"],
        recvId: str,
        message: str,
        messageType: typing.Literal["text", "markdown", "html"],
        buttons: list[dict]
    ):
    async with aiohttp.ClientSession() as session:
        await session.post(
            url=f"https://chat-go.jwzhd.com/open-apis/v1/bot/edit?token={token}",
            json={
                "msgId": msgId,
                "recvId": recvId,
                "recvType": recvType,
                "contentType": messageType,
                "content": {
                    "text": message,
                    "buttons": buttons
                }
            }
        )

async def recall_message(
        token: str,
        msgId: str,
        recvType: typing.Literal["user", "group"],
        recvId: str, 
    ):
    async with aiohttp.ClientSession() as session:
        await session.post(
            url=f"https://chat-go.jwzhd.com/open-apis/v1/bot/recall?token={token}",
            json={
                "msgId": msgId,
                "chatId": recvId,
                "chatType": recvType
            }
        )

async def send_stream_message(
        token: str,
        recvType: typing.Literal["user", "group"],
        recvId: str,
        message: typing.AsyncIterable[str],
        messageType: typing.Literal["text", "markdown", "html"]
    ) -> str:
    async def __decorator():
        async for c in message:
            yield c.encode("utf-8")
    async with aiohttp.ClientSession() as session:
        result = await session.post(
            url=f"https://chat-go.jwzhd.com/open-apis/v1/bot/send-stream?token={token}&recvId={recvId}&recvType={recvType}&contentType={messageType}",
            headers={
                "Content-Type": "text/html" if messageType == "html" else "text/plain"
            },
            data=__decorator()
        )
        jsond = await result.json()
        msgid = jsond["data"]["messageInfo"]["msgId"]
    return msgid

async def send_image_message(
        token: str,
        recvType: typing.Literal["user", "group"],
        recvId: str,
        image: bytes
    ) -> str:
    async with aiohttp.ClientSession() as session:
        FD = aiohttp.FormData()
        FD.add_field("image", image, filename='c.png')
        W = await (await session.post(
            url=f"https://chat-go.jwzhd.com/open-apis/v1/image/upload?token={token}",
            data=FD
        )).json()
        print(W)
        imageKey = W["data"]["imageKey"]
        result = await session.post(
            url=f"https://chat-go.jwzhd.com/open-apis/v1/bot/send?token={token}",
            json={
                "recvId": recvId,
                "recvType": recvType,
                "contentType": "image",
                "content": {
                    "imageKey": imageKey
                }
            }
        )
        jsond = await result.json()
    return jsond["data"]["messageInfo"]["msgId"]