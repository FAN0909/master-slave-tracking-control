"""简单的线程安全单例日志，由界面定时读取。"""

from collections import deque
from datetime import datetime
from threading import Lock


class Logger:
    _instance = None
    _instance_lock = Lock()

    @classmethod
    def instance(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def __init__(self):
        self._messages = deque(maxlen=2000)
        self._lock = Lock()

    def info(self, message):
        self._write("INFO", message)

    def error(self, message):
        self._write("ERROR", message)

    def _write(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        with self._lock:
            self._messages.append(f"[{timestamp}] [{level}] {message}")

    def take_messages(self):
        with self._lock:
            messages = list(self._messages)
            self._messages.clear()
            return messages

    def clear(self):
        with self._lock:
            self._messages.clear()
