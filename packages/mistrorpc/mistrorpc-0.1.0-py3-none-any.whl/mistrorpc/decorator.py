import asyncio

class Decorators:
    @staticmethod
    def asynclize(fn):
        async def __dec(*args, **kwargs):
            return fn(*args, **kwargs)
        return __dec
    @staticmethod
    def run_in_executor(fn):
        async def __dec(*args, **kwargs):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda a, b: fn(*a, **b), args, kwargs)
        return __dec