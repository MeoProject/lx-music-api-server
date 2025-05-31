import os
import time
import atexit
import threading
import ujson as json


class StatisticsManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        if os.path.exists("statistics.json"):
            with open("statistics.json", "r", encoding="utf8") as f:
                self.data = dict(json.loads(f.read()))
        else:
            self.data = {
                "all_request": 0,
                "kw": {
                    "success": 0,
                    "error": 0,
                },
                "kg": {
                    "success": 0,
                    "error": 0,
                },
                "tx": {
                    "success": 0,
                    "error": 0,
                },
                "wy": {
                    "success": 0,
                    "error": 0,
                },
                "mg": {
                    "success": 0,
                    "error": 0,
                },
            }

        self.filename = "statistics.json"
        self._save_lock = threading.Lock()
        self._running = False
        self._thread = None
        atexit.register(self._on_exit)

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._save_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
        self._SaveData()

    def _save_loop(self):
        while self._running:
            self._SaveData()
            time.sleep(1)

    def _SaveData(self):
        with self._save_lock:
            try:
                with open(self.filename, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=2)
            except Exception as e:
                print(f"统计保存失败: {str(e)}")

    def _on_exit(self):
        self.stop()
        print("已执行退出统计保存")

    def increment(self, platform, success=True):
        with self._save_lock:
            try:
                if platform == "all_request":
                    self.data[platform] += 1
                else:
                    key = "success" if success else "error"
                    self.data[platform][key] += 1
            except KeyError:
                print(f"无效统计项: {platform}")
