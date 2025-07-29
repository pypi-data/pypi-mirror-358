
import asyncio
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context, set_start_method
from typing import Optional
from abc import ABC, abstractmethod


class MutClass(ABC):

    def __call__(self, *args, **kwargs):
        return self

    @abstractmethod
    def start(self, *args, **kwargs):
        ...


run: Optional[MutClass] = None


def init_model(cls: MutClass, *args, **kwargs):
    global run
    run = cls(*args, **kwargs)


def run_model(*args, **kwargs):
    global run
    return run.start(*args, **kwargs)


class AsyncMultiProcess:

    def __init__(self):
        self.pool = None

    def init(self, max_workers: int, init_class: MutClass, init_args = (), ctx=None, ):
        if not ctx:
            set_start_method("spawn", force=True)
            ctx = get_context("spawn")
        self.pool = ProcessPoolExecutor(max_workers=max_workers,
                                        mp_context=ctx,
                                        initializer=init_model,
                                        initargs=(init_class, *init_args))

    async def async_run(self, *args) -> asyncio.Future:
        f = asyncio.get_event_loop().run_in_executor(self.pool, run_model, *args)
        return f
