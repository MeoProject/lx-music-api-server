# ----------------------------------------
# - mode: python - 
# - author: helloplhm-qwq - 
# - name: scheduler.py - 
# - project: lx-music-api-server - 
# - license: MIT - 
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.
# Do not edit except you know what you are doing.

# 一个简单的循环任务调度器

import time
import threading
from .variable import running
from . import log

logger = log.log("scheduler")

global tasks
tasks = []

class taskWrapper:
    def __init__(self, name, function, interval = 86400, latest_execute = 0):
        self.function = function
        self.interval = interval
        self.name = name
        self.latest_execute = latest_execute

    def check_available(self):
        return (time.time() - self.latest_execute) >= self.interval

    def run(self):
        try:
            logger.info(f"task {self.name} run start")
            self.function()
        except Exception as e:
            logger.error(f"task {self.name} run failed, waiting for next execute...")

def append(name, task, interval = 86400):
    global tasks
    logger.debug(f"new task ({name}) registered")
    wrapper = taskWrapper(name, task, interval)
    return tasks.append(wrapper)

def thread_runner():
    global tasks
    while True:
        if not running:
            return
        for t in tasks:
            if t.check_available():
                t.latest_execute = int(time.time())
                threading.Thread(target = t.run).start()
        time.sleep(5)

def run():
    logger.debug("scheduler thread starting...")
    threading.Thread(target = thread_runner).start()
    logger.debug("schedluer thread load success")