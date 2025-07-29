import inspect, asyncio, typing

def tokens(str: str) -> int:
    return len(str)

async def asyncgen(chat: typing.Callable, kvargs: dict) -> typing.AsyncGenerator[str, None]:
    '''Convert a chat/complete function to an async generator.'''
    if inspect.isasyncgenfunction(chat):
        result = await asyncio.to_thread(chat, **kvargs)
        async for message in result:
            yield message
    elif inspect.isgeneratorfunction(chat):
        result = await asyncio.to_thread(chat, **kvargs)
        for message in result:
            yield message
    elif 'callback' not in inspect.signature(chat).parameters:
        result = await asyncio.to_thread(chat, **kvargs)
        yield await result if inspect.iscoroutine(result) else result
    else:
        sentinel = object()
        queue = asyncio.Queue()
        def callback(chunk: str):
            queue.put_nowait(chunk)
        kvargs['callback'] = callback

        async def async_chat():
            result = await asyncio.to_thread(chat, **kvargs)
            result = await result if inspect.iscoroutine(result) else result
            if result is not None:
                queue.put_nowait(result)
            queue.put_nowait(sentinel)

        asyncio.create_task(async_chat())
        while True:
            chunk = await queue.get()
            if chunk is sentinel:
                break
            yield chunk
