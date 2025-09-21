import time
import asyncio
from utils.time import tsFormat
from . import log

logger = log.createLogger("scheduler")

running_event = asyncio.Event()

global tasks

tasks = []


class taskWrapper:
    def __init__(self, name, function, interval=86400, args={}, latest_execute=0):
        self.function = function
        self.interval = interval
        self.name = name
        self.latest_execute = latest_execute
        self.args = args

    def check_available(self):
        return (time.time() - self.latest_execute) >= self.interval

    async def run(self):
        try:
            logger.info(f"task {self.name} run start")
            await self.function(**self.args)
            logger.info(
                f"task {self.name} run success, next execute: {tsFormat(self.interval + self.latest_execute)}"
            )
        except Exception:
            logger.error(f"task {self.name} run failed, waiting for next execute...")

    def __str__(self):
        return f'SchedulerTaskWrapper(name="{self.name}", interval={self.interval}, function={self.function}, args={self.args}, latest_execute={self.latest_execute})'


def append(name, task, interval=86400, args={}):
    global tasks
    wrapper = taskWrapper(name, task, interval, args)
    logger.debug(f"new task ({name}) registered")
    return tasks.append(wrapper)


# 在 thread_runner 函数中修改循环逻辑
async def thread_runner():
    global tasks, running_event
    while not running_event.is_set():
        tasks_runner = []
        for t in tasks:
            if t.check_available() and not running_event.is_set():
                t.latest_execute = int(time.time())
                tasks_runner.append(t.run())
        if tasks_runner:
            await asyncio.gather(*tasks_runner)
        await asyncio.sleep(1)


async def run():
    logger.debug("scheduler thread starting...")
    task = asyncio.create_task(thread_runner())
    logger.debug("schedluer thread load success")
