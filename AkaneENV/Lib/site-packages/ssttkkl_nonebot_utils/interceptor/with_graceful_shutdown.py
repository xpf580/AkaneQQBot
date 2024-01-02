from asyncio import create_task, gather, shield
from functools import wraps

from nonebot import get_driver

tasks = []


def with_graceful_shutdown():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            task = shield(create_task(func(*args, **kwargs)))

            @task.add_done_callback
            def _(*arg):
                tasks.remove(task)

            tasks.append(task)
            return await task

        return wrapper

    return decorator


@get_driver().on_shutdown
async def wait_uncompleted():
    await gather(*tasks)
