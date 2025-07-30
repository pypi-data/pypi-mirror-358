import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import daemon_metrics
import requests
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from the_conf import TheConf

conf = TheConf(
    {
        "source_order": ["env", "files"],
        "config_files": [
            "/etc/updownio-exporter/updownio-exporter.json",
            "~/.config/updownio-exporter.json",
        ],
        "parameters": [
            {"name": {"default": "updownio-exporter"}},
            {"type": "list", "apikeys": {"type": str}},
            {
                "loop": [
                    {"interval": {"default": 240, "help": "seconds"}},
                    {
                        "reset": {
                            "default": 7 * 24,
                            "help": "in hours, the time between two reset of t"
                            "he time frame at which we are looking at",
                        }
                    },
                    {
                        "lookback": {
                            "default": 24,
                            "help": "in hours, updownio will not serve statist"
                            "ics on low frequency checks for period of times t"
                            "oo short (say for a check every 30mn, you'll need"
                            " 24h lookback)",
                        }
                    },
                ]
            },
            {
                "prometheus": [
                    {"port": {"type": "int", "default": 9100}},
                    {"namespace": {"default": "updownio"}},
                ]
            },
            {"logging": [{"level": {"default": "WARNING"}}]},
        ],
    }
)

logger = logging.getLogger("updownio-exporter")
try:
    logger.setLevel(getattr(logging, conf.logging.level.upper()))
    logger.addHandler(logging.StreamHandler())
except AttributeError as error:
    raise AttributeError(
        f"{conf.logging.level} isn't accepted, only DEBUG, INFO, WARNING, "
        "ERROR and FATAL are accepted"
    ) from error


URL = "https://updown.io/api/%s?api-key=%s"
RESPONSE_TIME_BUCKETS = [125, 250, 500, 1000, 2000, 4000, 8000, 16000, 32000]
APDEX = Gauge(
    "apdex",
    "apdex",
    ["alias"],
    namespace=conf.prometheus.namespace,
)
TIMINGS = Gauge(
    "timings",
    "timings",
    ["alias", "step"],
    namespace=conf.prometheus.namespace,
)
REQUEST_COUNT = Counter(
    "request",
    "request",
    ["alias", "tag"],
    namespace=conf.prometheus.namespace,
)
RESPONSE_TIME = Histogram(
    "response_time",
    "Response time",
    ["alias"],
    buckets=RESPONSE_TIME_BUCKETS,
    namespace=conf.prometheus.namespace,
)
SSL_REMAING = Gauge(
    "ssl_remaining",
    "Seconds until ssl expiration",
    ["alias"],
    namespace=conf.prometheus.namespace,
)


class Cache:
    _cache: Dict[str, Dict[str, Optional[int]]] = defaultdict(
        lambda: defaultdict(lambda: None)
    )
    clear = _cache.clear

    @classmethod
    def get_diff(cls, key1: str, key2: str, value: int):
        cached_value = cls._cache[key1][key2]
        cls._cache[key1][key2] = value
        if cached_value is None:
            return cached_value, 0
        if cached_value > value:
            return cached_value, None
        return cached_value, value - cached_value


def set_response_time_histogram(metrics: dict, alias: str):
    histogram = RESPONSE_TIME.labels(alias)
    to_observe: List[float] = []
    previous_bucket_value = 0
    for bucket in RESPONSE_TIME_BUCKETS:
        value_to_observe = bucket - ((bucket - previous_bucket_value) / 2)
        value = metrics["requests"]["by_response_time"][f"under{bucket}"]
        cached, diff = Cache.get_diff(alias, str(bucket), value)
        if diff is None:
            msg = (
                "%s/%s by_response_time decreased (from %d to %d), "
                "ignoring this loop and reseting"
            )
            logger.warning(msg, alias, bucket, cached, value)
            RESPONSE_TIME.remove(alias)
            return
        to_add = diff - len(to_observe)
        if to_add > 0:
            msg = "%s/%s observing %d constructed values"
            logger.info(msg, alias, bucket, to_add)
            to_observe.extend([value_to_observe for _ in range(to_add)])
        previous_bucket_value = bucket

    for value_to_observe in to_observe:
        histogram.observe(value_to_observe)

    _, new_sample_cnt = Cache.get_diff(
        alias, "samples", metrics["requests"]["samples"]
    )

    if len(to_observe) < new_sample_cnt:
        for _ in range(new_sample_cnt - len(to_observe)):
            histogram.observe(RESPONSE_TIME_BUCKETS[-1] * 2)


def set_metrics(check: dict, api_key: str, from_: datetime, utcnow: datetime):
    alias = check["alias"].lower().replace(" ", "-")
    uri = f"checks/{check['token']}/metrics"
    url = URL % (uri, api_key) + f"&from={from_.isoformat()}"
    logger.debug("querying for checks on %r", check["token"])
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    metrics = response.json()
    try:
        ssl_expire = datetime.fromisoformat(check["ssl"]["expires_at"])
        if (remaining := (ssl_expire - utcnow).total_seconds()) > 0:
            SSL_REMAING.labels(alias).set(remaining)
    except KeyError:
        pass
    APDEX.labels(alias=alias).set(metrics["apdex"])
    # filling histogram
    set_response_time_histogram(metrics, alias)
    # counting request
    for key, value in metrics.get("requests", {}).items():
        if isinstance(value, int):
            cached, diff = Cache.get_diff(alias, key, value)
            if diff is None:
                msg = (
                    "%s/%s count decreased (from %d to %d), "
                    "ignoring this loop and reseting"
                )
                logger.warning(msg, alias, key, cached, value)
                try:
                    REQUEST_COUNT.remove(alias, key)
                except KeyError:
                    continue
            elif diff > 0:
                msg = "%s/%s %d->%d (+%d)"
                logger.info(msg, alias, key, cached, value, diff)
                REQUEST_COUNT.labels(alias, key).inc(diff)
    for step, timing in metrics["timings"].items():
        TIMINGS.labels(alias=alias, step=step).set(timing)


def get_checks(api_key, from_):
    logger.debug("listing checks from %r", from_)
    response = requests.get(URL % ("checks", api_key), timeout=60)
    response.raise_for_status()
    return response.json()


def reset(from_):
    new_from = datetime.now(timezone.utc) - timedelta(hours=conf.loop.lookback)
    msg = "from (%r) is more that %dh ago, reseting to %r"
    logger.warning(msg, from_, conf.loop.reset, new_from)
    Cache.clear()
    daemon_metrics.DAEMON.labels(name=conf.name, status="loop-reset").inc()
    REQUEST_COUNT.clear()
    RESPONSE_TIME.clear()
    return new_from


def main():
    info = {
        "loop-period": conf.loop.interval,
        "loop-lookback": conf.loop.lookback,
        "item-count": len(conf.apikeys),
    }
    daemon_metrics.init(conf.name, info)

    from_ = datetime.now(timezone.utc) - timedelta(hours=conf.loop.lookback)
    reset_interval = timedelta(hours=conf.loop.reset)
    while True:
        loop_context = daemon_metrics.LoopContext(conf.name)
        with loop_context:
            if datetime.now(timezone.utc) - reset_interval > from_:
                from_ = reset(from_)
            for api_key in conf.apikeys:
                utcnow = datetime.now(timezone.utc)
                try:
                    checks = get_checks(api_key, from_)
                except Exception:
                    logger.exception("something went wrong when collecting")
                    daemon_metrics.item_result(conf.name, False, api_key)
                    continue
                for check in checks:
                    try:
                        set_metrics(check, api_key, from_, utcnow)
                    except Exception:
                        logger.exception("processing checks went wrong")
                        daemon_metrics.item_result(conf.name, False, api_key)
                        break
                else:
                    daemon_metrics.item_result(conf.name, True, api_key)

        if (interval := conf.loop.interval - loop_context.exec_interval) > 0:
            time.sleep(interval)


if __name__ == "__main__":
    logger.info("starting %s", conf.name)
    start_http_server(conf.prometheus.port)
    main()
