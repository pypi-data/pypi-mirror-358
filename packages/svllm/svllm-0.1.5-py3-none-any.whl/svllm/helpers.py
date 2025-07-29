import inspect, asyncio, time, typing

def tokens(str: str) -> int:
    return len(str)

async def asyncgen(
        func: typing.Callable,
        kvargs: dict,
    ) -> typing.AsyncGenerator[str, None]:

    '''Convert a chat/complete function to an async generator.'''
    sentinel = object()
    queue = asyncio.Queue()

    async def async_func():
        sig = inspect.signature(func)
        if 'callback' in sig.parameters:
            def callback(chunk: str):
                queue.put_nowait(chunk)
            kvargs['callback'] = callback

        result = func(**kvargs)
        if inspect.isasyncgen(result):
            async for chunk in result:
                queue.put_nowait(chunk)
        elif inspect.isgenerator(result):
            for chunk in result:
                queue.put_nowait(chunk)
        elif inspect.iscoroutine(result):
            queue.put_nowait(await result)
        else:
            queue.put_nowait(result)

    def sync_run():
        try:
            asyncio.run(async_func())
        finally:
            queue.put_nowait(sentinel)

    co = asyncio.to_thread(sync_run)
    asyncio.create_task(co)

    while True:
        chunk = await queue.get()
        if chunk is sentinel:
            break
        yield chunk

async def agg(ag: typing.AsyncGenerator, interval: float = 0.05):
    '''Aggregate async generator chunks into a single string.'''
    content, timestamp = '', time.time()
    async for chunk in ag:
        content += chunk
        if time.time() - timestamp > interval:
            yield content
            content, timestamp = '', time.time()
    if content:
        yield content
