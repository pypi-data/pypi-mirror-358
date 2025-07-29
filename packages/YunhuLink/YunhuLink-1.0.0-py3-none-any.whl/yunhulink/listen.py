from fastapi import FastAPI, Request
from yunhulink.orm import Yunhu, YunhuGroup, YunhuUser
import yunhulink.functional as F
import typing
import asyncio
import uvicorn

class YunhuTextReqModel:
    def __init__(self, content: str, msgType: typing.Literal["text", "html", "markdown"], instruct: int=0):
        self.__t = msgType
        self.__c = content
        self.__i = instruct
    @property
    def instruct(self) -> str:
        return self.__i
    @property
    def content(self) -> str:
        return self.__c
    @property
    def msgType(self) -> typing.Literal["text", "html", "markdown"]:
        return self.__t

class YunhuButtonClickModel:
    def __init__(self, aid: str):
        self.__a = aid
    @property
    def msgType(self) -> typing.Literal["button"]:
        return "button"
    @property
    def action(self) -> str:
        return self.__a

class YunhuImageModel:
    def __init__(self, image: bytes):
        self.__image = image
    @property
    def msgType(self) -> typing.Literal["image"]:
        return "image"
    @property
    def image(self) -> bytes:
        return self.__image

class YunhuActionModel:
    def __init__(self, event: typing.Literal["follow", "unfollow", "join", "exit"]):
        self.__event: typing.Literal["follow", "unfollow", "join", "exit"] = event
    @property
    def msgType(self) -> typing.Literal["event.follow", "event.unfollow", "event.join", "event.exit"]:
        return "event."+self.__event

class YunhuMessageModel:
    def __init__(
            self,
            author: YunhuUser,
            session: typing.Union[YunhuGroup, YunhuUser],
            message: typing.Union[YunhuTextReqModel, YunhuButtonClickModel, YunhuImageModel]
        ):
        self.__author = author
        self.__session = session
        self.__message = message
    @property
    def message(self):
        return self.__message
    @property
    def author(self):
        return self.__author
    @property
    def session(self):
        return self.__session

class YunhuListener(Yunhu, FastAPI):
    def __init__(
            self,
            token: str,
            webhook_password: str="",
            webhook_endpoint: str="/webhook"
        ):
        Yunhu.__init__(self, token)
        FastAPI.__init__(self)
        self.__webhook_password = webhook_password
        self.post(webhook_endpoint)(self.__hookapi)
        self.__hooks: list[typing.Callable[[YunhuMessageModel], typing.Coroutine]] = []
    async def __hookapi(self, req: Request, password: str=""):
        if self.__webhook_password != password:
            return {'msg': "access denied."}
        try:
            cjson: dict = await req.json()
            author = None
            session = None
            # Message Event
            if cjson["header"]["eventType"] == "message.receive.normal":
                if cjson["event"]["message"]["contentType"] in ["text", "html", "markdown"]:
                    message = YunhuTextReqModel(cjson["event"]["message"]["content"]["text"], cjson["event"]["message"]["contentType"])
                elif cjson["event"]["message"]["contentType"] == "image":
                    message = YunhuImageModel(await F.get_image(cjson["event"]["message"]["content"]["imageName"]))
                else:
                    return
            elif cjson["header"]["eventType"] == "message.receive.instruction":
                if cjson["event"]["message"].get("contentType", "text") in ["text", "html", "markdown"]:
                    message = YunhuTextReqModel(
                        cjson["event"]["message"]["content"]["text"],
                        cjson["event"]["message"].get("contentType", "text"),
                        instruct=cjson["event"]["message"]["commandId"]
                    )
                else:
                    return
            # Button Report Event
            elif cjson["header"]["eventType"] == "button.report.inline":
                message = YunhuButtonClickModel(cjson["event"]["value"])
                author = self.get_user(cjson["event"]["userId"])
                if cjson["event"]["recvType"] == "group":
                    session = self.get_group(cjson["event"]["recvId"])
                else:
                    session = author
            # Action Event
            elif cjson["header"]["eventType"] == "group.join":
                message = YunhuActionModel("join")
                author = self.get_user(cjson["event"]["userId"])
                session = self.get_group(cjson["event"]["chatId"])
            elif cjson["header"]["eventType"] == "group.leave":
                message = YunhuActionModel("join")
                author = self.get_user(cjson["event"]["userId"])
                session = self.get_group(cjson["event"]["chatId"])
            elif cjson["header"]["eventType"] == "bot.followed":
                message = YunhuActionModel("follow")
                author = self.get_user(cjson["event"]["userId"])
                session = author
            elif cjson["header"]["eventType"] == "bot.unfollowed":
                message = YunhuActionModel("unfollow")
                author = self.get_user(cjson["event"]["userId"])
                session = author
            else:
                return
            # Configure author & session
            if author is None:
                author = self.get_user(cjson["event"]["sender"]["senderId"])
            if session is None:
                if cjson["event"]["chat"]["chatType"] == "group":
                    session = self.get_group(cjson["event"]["chat"]["chatId"])
                else:
                    session = author
            for hook in self.__hooks:
                asyncio.create_task(hook(YunhuMessageModel(author, session, message)))
        except Exception:
            return
    def msghook(
            self,
            *eventType: typing.Literal[
                "text", "html", "markdown", "button", "image", "event.follow", "event.unfollow", "event.join", "event.exit"
            ]
        ):
        etype = set(eventType)
        async def _constructor(fn: typing.Callable[[YunhuMessageModel], typing.Coroutine]):
            if len(etype) == 0:
                self.__hooks.append(fn)
            else:
                async def _filter(message: YunhuMessageModel):
                    if message.message.msgType in etype:
                        await fn
                self.__hooks.append(_filter)
            return fn
        return _constructor
    async def start_server(self, host="0.0.0.0", port=4417):
        await uvicorn.Server(uvicorn.Config(self, host=host, port=port)).serve()