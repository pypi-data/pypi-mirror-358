from prometheus_client import Gauge, Info, Histogram
from importlib.metadata import version
from datetime import datetime

DAEMON_CONFIG = Info("daemon_config", "", ["name"])
DAEMON_TIME = Histogram(
    "daemon_time", "", ["name", "status"], buckets=list(range(0, 60, 5))
)
DAEMON = Gauge("daemon", "", ["name", "status"])

_ITEMS: dict[str, bool] = {}


def init(daemon_name: str, info: dict):
    info["version"] = version(daemon_name)
    DAEMON_CONFIG.labels(name=daemon_name).info(info)
    DAEMON.labels(name=daemon_name, status="items-ok").set(0)
    DAEMON.labels(name=daemon_name, status="items-ko").set(0)


def item_result(daemon_name: str, is_ok: bool, item_id: str):
    ok_gauge = DAEMON.labels(name=daemon_name, status="items-ok")
    ko_gauge = DAEMON.labels(name=daemon_name, status="items-ko")
    if is_ok and _ITEMS.get(item_id):
        pass
    elif is_ok and not _ITEMS.get(item_id):
        if item_id in _ITEMS:
            ko_gauge.dec()
        ok_gauge.inc()
        _ITEMS[item_id] = True
    elif not is_ok and not _ITEMS.get(item_id):
        pass
    elif not is_ok and _ITEMS.get(item_id):
        if item_id in _ITEMS:
            ok_gauge.dec()
        ko_gauge.inc()
        _ITEMS[item_id] = False


def mark_loop_end(daemon_name: str, interval: float):
    DAEMON_TIME.labels(name=daemon_name, status="loop-time").observe(interval)


class LoopContext:

    def __init__(self, daemon_name):
        self.daemon_name = daemon_name
        self.result = None
        self.start = None
        self.exec_interval = None

    def set_result(self, result: bool):
        self.result = result

    def __enter__(self):
        self.start = datetime.now()
        return self

    def __exit__(self, rtype, rvalue, traceback):
        self.exec_interval = (datetime.now() - self.start).total_seconds()
        mark_loop_end(self.daemon_name, self.exec_interval)
