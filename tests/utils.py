from homebot import Formatter


class CoWorkingFormatter(Formatter):
    def __call__(self, payload):
        return super().__call__(f"S{payload}E")
