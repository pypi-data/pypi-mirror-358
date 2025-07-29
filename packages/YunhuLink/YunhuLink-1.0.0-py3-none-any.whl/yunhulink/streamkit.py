import asyncio

class TextIterationClient:
    def __init__(self):
        self.__queue: asyncio.Queue[str] = asyncio.Queue()
        self.__is_eol = False
    def __aiter__(self):
        return self
    async def __anext__(self):
        if self.__is_eol:
            try:
                r = self.__queue.get_nowait()
            except asyncio.QueueEmpty:
                raise StopAsyncIteration()
        else:
            r = await self.__queue.get()
        return r
    async def put(self, c):
        await self.__queue.put(c)
    async def eol(self):
        self.__is_eol = True