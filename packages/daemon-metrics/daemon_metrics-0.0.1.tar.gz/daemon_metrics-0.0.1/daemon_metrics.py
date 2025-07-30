from prometheus_client import Gauge, Info

DAEMON_CONFIG = Info("daemon_config", "", ["name"])
DAEMON = Gauge("daemon", "", ["name", "status"])


_ITEMS_OK: dict[str, bool] = {}


def set_daemon_item(is_ok: bool, item_id: str):
    ok_metric = DAEMON.labels(name=conf.name, status="items-ok")
    ko_metric = DAEMON.labels(name=conf.name, status="items-ko")
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
