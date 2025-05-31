import time
import asyncio
import traceback
from .log import log
from .utils import timestamp_format

logger = log("Scheduler")

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
            logger.info(f"进程 {self.name} 开始运行")
            await self.function(**self.args)
            logger.info(
                f"进程 {self.name} 成功运行, 下次执行时间: {timestamp_format(self.interval + self.latest_execute)}"
            )
        except Exception as e:
            logger.error(f"进程 {self.name} 运行失败, 等待下次执行...")
            logger.error(traceback.format_exc())

    def __str__(self):
        return f'SchedulerTaskWrapper(name="{self.name}", interval={self.interval}, function={self.function}, args={self.args}, latest_execute={self.latest_execute})'


def append(name, task, interval=86400, args={}):
    global tasks
    wrapper = taskWrapper(name, task, interval, args)
    logger.info(f"new task ({name}) registered")
    return tasks.append(wrapper)


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
    logger.info("定时器加载中...")
    task = asyncio.create_task(thread_runner())
    logger.info("定时器加载成功")
