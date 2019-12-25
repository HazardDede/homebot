from homebot import Formatter


class CoWorkingFormatter(Formatter):
    async def __call__(self, payload):
        return await super().__call__(f"S{payload}E")
