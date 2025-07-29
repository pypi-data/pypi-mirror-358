
import functools
import time
from typing import Callable, Any, Coroutine


def async_logging_decorator(logging):
    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            has_time = time.time() - start_time
            # todo 如果参数太长，待处理
            logging.info(f"func:{func.__name__},执行时间: {has_time:.2f}秒, 入参:{args}{kwargs}，出参：{result}")
            return result
        return wrapper
    return decorator


def logging_decorator(logging):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            has_time = time.time() - start_time
            # todo 如果参数太长，待处理
            logging.info(f"func:{func.__name__},执行时间: {has_time:.2f}秒, 入参:{args}{kwargs}，出参：{result}")
            return result
        return wrapper
    return decorator
