import asyncio

def to_sync_generator (asyncgen, loop):
    # https://stackoverflow.com/questions/76991812/convert-sync-generator-function-that-takes-a-sync-iterable-to-async-generator-fu
    async_it = asyncgen.__aiter__ ()
    while True:
        try:
            yield asyncio.run_coroutine_threadsafe (async_it.__anext__ (), loop).result ()
        except StopAsyncIteration:
            return

async def to_async_generator (syncgen):
    it = syncgen.__iter ()
    done = object ()
    def safe_next ():
        try:
            return it.__next__ ()
        except StopIteration:
            return done
    while True:
        value = await asyncio.to_thread (safe_next)
        if value is done:
            break
        yield value


class AIO:
    def carryout (self, coro, close = True):
        loop = asyncio.get_event_loop ()
        loop.run_until_complete (coro)
        close and loop.close ()

    def ensure_future (self, *coro):
        return asyncio.ensure_future (coro) # Task

    async def map (self, func, iterable):
        futures = [self.submit (func (item)) for item in iterable]
        results = await asyncio.gather (*futures)

    async def threaded (self, func, *args, **karg):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor (None, func, *args, **karg) # Future
