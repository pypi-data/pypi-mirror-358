from prometheus_client import Gauge, Info, Histogram
from typing import Optional
from datetime import datetime

DAEMON_CONFIG = Info("daemon_config", "", ["name"])
DAEMON_TIME = Histogram("daemon_time", "", ["name", "status"])
DAEMON = Gauge("daemon", "", ["name", "status"])

_ITEMS_OK: dict[str, bool] = {}


def set_daemon_item(is_ok: bool, item_id: str, daemon_name: str):
    ok_metric = DAEMON.labels(name=daemon_name, status="items-ok")
    ko_metric = DAEMON.labels(name=daemon_name, status="items-ko")
    if is_ok and _ITEMS_OK.get(item_id):
        pass
    elif is_ok and not _ITEMS_OK.get(item_id):
        _ITEMS_OK[item_id] = True
        ok_metric.inc()
        ko_metric.dec()
    elif not is_ok and not _ITEMS_OK.get(item_id):
        pass
    elif not is_ok and _ITEMS_OK.get(item_id):
        _ITEMS_OK[item_id] = False
        ko_metric.inc()
        ok_metric.dec()


def mark_loop_end(daemon_name: str, result: bool, interval: float):
    DAEMON_TIME.labels(
        name=daemon_name, status=f"{'ok' if result else 'ko'}-loop"
    ).observe(interval)


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
        if isinstance(rvalue, Exception) or not self.result:
            result = False
        else:
            result = True
        mark_loop_end(self.daemon_name, result, self.exec_interval)
