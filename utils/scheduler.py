import time
import asyncio
from utils.time import tsFormat
from . import log

logger = log.createLogger("定时器")

running_event = asyncio.Event()
tasks = []


class SchedulerTaskWrapper:
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
            self.latest_execute = int(time.time())
            logger.info(
                f"进程 {self.name} 运行成功, 下次执行: {tsFormat(self.interval + self.latest_execute)}"
            )
        except Exception as e:
            logger.error(f"进程 {self.name} 运行失败: {e}", exc_info=True)

    def __str__(self):
        return f'SchedulerTaskWrapper(name="{self.name}", interval={self.interval}, function={self.function}, args={self.args}, latest_execute={self.latest_execute})'


def append(name, task, interval=86400, args={}):
    wrapper = SchedulerTaskWrapper(name, task, interval, args)
    logger.debug(f"新进程 ({name}) 注册")
    return tasks.append(wrapper)


async def thread_runner():
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
    logger.debug("定时线程启动...")
    asyncio.create_task(thread_runner())
    logger.debug("定时线程停止")
