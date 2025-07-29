import yunhulink.functional as F
import typing
import copy
import asyncio
from yunhulink.streamkit import TextIterationClient

class Yunhu:
    def __init__(self, token: str):
        self.__token = token
    @property
    def token(self):
        return self.__token
    def get_user(self, uid: str):
        return YunhuUser(self, uid)
    def get_group(self, gid: str):
        return YunhuGroup(self, gid)

class YunhuImageMessage:
    def __init__(self, api: Yunhu, msgid: str, recvId: str, recvType: typing.Literal["user", "group"]):
        self.__api = api
        self.__msgid = msgid
        self.__is_canceled = False
        self.__rt = recvType
        self.__ri = recvId
    @property
    def recvId(self):
        if self.__is_canceled:
            raise ReferenceError("Message Recalled!")
        return self.__ri
    @property
    def recvType(self) -> typing.Literal["user", "group"]:
        if self.__is_canceled:
            raise ReferenceError("Message Recalled!")
        return self.__rt
    async def recall(self):
        if self.__is_canceled:
            raise ReferenceError("Message Recalled!")
        self.__is_canceled = True
        await F.recall_message(self.__api.token, self.__msgid, self.__rt, self.__ri)

class YunhuUser:
    def __init__(self, api: Yunhu, uid: str):
        self.__api = api
        self.__uid = uid
    @property
    def uid(self):
        return self.__uid
    def create_text_message(self, msgType: typing.Literal["text", "markdown", "html"]="text"):
        return YunhuTextMessage(self.__api, "user", self.__uid, msgType)
    async def send_text_message(self, content: str, msgType: typing.Literal["text", "markdown", "html"]="text", buttons: list[dict]=[]):
        m = YunhuTextMessage(self.__api, "user", self.__uid, msgType)
        await m.attach_button(buttons)
        await m.attach_content(content, stream=False)
        return m
    async def send_image_message(self, image: bytes):
        pid = await F.send_image_message(self.__api.token, "user", self.__uid, image)
        return YunhuImageMessage(self.__api, pid, self.__uid, "user")
    def __eq__(self, c):
        if not isinstance(c, YunhuUser):
            return False
        return c.uid == self.__uid

class YunhuGroup:
    def __init__(self, api: Yunhu, gid: str):
        self.__api = api
        self.__gid = gid
    @property
    def gid(self):
        return self.__gid
    def create_text_message(self, msgType: typing.Literal["text", "markdown", "html"]="text"):
        return YunhuTextMessage(self.__api, "group", self.__gid, msgType)
    async def send_text_message(self, content: str, msgType: typing.Literal["text", "markdown", "html"]="text", buttons: list[dict]=[]):
        m = YunhuTextMessage(self.__api, "user", self.__uid, msgType)
        await m.attach_button(buttons)
        await m.attach_content(content, stream=False)
        return m
    async def send_image_message(self, image: bytes):
        pid = await F.send_image_message(self.__api.token, "group", self.__gid, image)
        return YunhuImageMessage(self.__api, pid, self.__gid, "group")
    def __eq__(self, c):
        if not isinstance(c, YunhuGroup):
            return False
        return c.gid == self.__gid

class YunhuTextMessage:
    def __init__(self, api: Yunhu, recvType: typing.Literal["user", "group"], recvId: str, msgType: typing.Literal["text", "markdown", "html"]="text"):
        self.__state: typing.Literal[
            "unsended",
            "stream-sending",
            "sended",
            "recalled"
        ] = "unsended"
        self.__token = api.token
        self.__msgId = ""
        self.__msgType = msgType
        self.__content = ""
        self.__buttons: list[dict] = []
        self.__recvType = recvType
        self.__recvId = recvId
        self.__stream_sender: typing.Optional[TextIterationClient] = None
        self.__stream_signal = None
    @property
    def yunhu(self):
        return Yunhu(self.__token)
    @property
    def session(self):
        if self.__recvType == "group":
            return YunhuGroup(Yunhu(self.__token), self.__recvId)
        return YunhuUser(Yunhu(self.__token), self.__recvId)
    @property
    def msgType(self):
        if self.__state == "recalled":
            raise ReferenceError("Message Recalled!")
        return self.__msgType
    @property
    def content(self):
        if self.__state == "recalled":
            raise ReferenceError("Message Recalled!")
        return self.__content
    @property
    def buttons(self):
        if self.__state == "recalled":
            raise ReferenceError("Message Recalled!")
        return copy.deepcopy(self.__buttons)
    @property
    def recvType(self):
        if self.__state == "recalled":
            raise ReferenceError("Message Recalled!")
        return self.__recvType
    @property
    def recvId(self):
        if self.__state == "recalled":
            raise ReferenceError("Message Recalled!")
        return self.__recvId
    async def attach_content(self, content: str, stream: bool=True):
        if self.__state == "recalled":
            raise ReferenceError("Message Recalled!")
        if self.__state == "stream-sending":
            await self.__stream_sender.put(content)
        elif self.__state == "sended":
            F.modify_text_message(
                token=self.__token,
                msgId=self.__msgId,
                recvId=self.__recvId,
                recvType=self.__recvType,
                message=self.content + content,
                buttons=self.__buttons,
                messageType=self.__msgType
            )
        elif self.__state == "unsended":
            if stream:
                self.__stream_sender = TextIterationClient()
                self.__stream_signal = asyncio.Queue()
                async def _cd():
                    await self.__stream_signal.put(await F.send_stream_message(
                        token=self.__token,
                        recvId=self.__recvId,
                        recvType=self.__recvType,
                        message=self.__stream_sender,
                        messageType=self.__msgType
                    ))
                coro = _cd()
                asyncio.create_task(coro)
                await self.__stream_sender.put(content)
                self.__state = "stream-sending"
            else:
                self.__msgId = await F.send_text_message(
                    token=self.__token,
                    recvId=self.__recvId,
                    recvType=self.__recvType,
                    message=content,
                    buttons=self.__buttons,
                    messageType=self.__msgType
                )
                self.__state = "sended"
        self.__content += content
    async def set_button_list(self, button: list[dict]):
        if self.__state == "recalled":
            raise ReferenceError("Message Recalled!")
        self.__buttons = copy.deepcopy(button)
        if self.__state == "sended":
            await F.modify_text_message(
                token=self.__token,
                msgId=self.__msgId,
                recvId=self.__recvId,
                recvType=self.__recvType,
                message=self.content,
                buttons=self.__buttons,
                messageType=self.__msgType
            )
    async def attach_button(self, button: typing.Union[dict, list[dict]]):
        if self.__state == "recalled":
            raise ReferenceError("Message Recalled!")
        if isinstance(button, dict):
            button = [ button ]
        self.__buttons.extend(copy.deepcopy(button))
        if self.__state == "sended":
            await F.modify_text_message(
                token=self.__token,
                msgId=self.__msgId,
                recvId=self.__recvId,
                recvType=self.__recvType,
                message=self.content,
                buttons=self.__buttons,
                messageType=self.__msgType
            )
    async def close_stream(self):
        if self.__state != "stream-sending":
            return
        await self.__stream_sender.eol()
        self.__msgId = await self.__stream_signal.get()
        self.__state = "sended"
        if len(self.__buttons) >= 1:
            await F.modify_text_message(
                token=self.__token,
                msgId=self.__msgId,
                recvId=self.__recvId,
                recvType=self.__recvType,
                message=self.content,
                buttons=self.__buttons,
                messageType=self.__msgType
            )
    async def modify_content(
            self,
            content: str,
            msgType: typing.Literal["text", "markdown", "html"]
        ):
        if self.__state == "recalled":
            raise ReferenceError("Message Recalled!")
        if content.startswith(self.__content) and msgType == self.msgType:
            A = content[len(self.__content):]
            await self.attach_content(A)
        elif self.__state == "unsended":
            self.__msgId = await F.send_text_message(
                token=self.__token,
                recvId=self.__recvId,
                recvType=self.__recvType,
                message=content,
                buttons=self.__buttons,
                messageType=self.__msgType
            )
            self.__state = "sended"
            self.__content = content
        else:
            await self.close_stream()
            self.__content = content
            self.__msgType = msgType
            await F.modify_text_message(
                token=self.__token,
                msgId=self.__msgId,
                recvId=self.__recvId,
                recvType=self.__recvType,
                message=self.content,
                buttons=self.__buttons,
                messageType=self.__msgType
            )
    async def recall(self):
        if self.__state == "recalled":
            raise ReferenceError("Message Recalled!")
        if self.__state == "unsended":
            self.__state = "recalled"
            return
        if self.__state == "stream-sending":
            await self.close_stream()
        await F.recall_message(
            token=self.__token,
            msgId=self.__msgId,
            recvType=self.__recvType,
            recvId=self.__recvId
        )
        self.__state = "recalled"