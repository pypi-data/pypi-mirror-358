#!/usr/bin/env python3

import logging
import time

import daemon_metrics
from prometheus_client import Gauge, start_http_server
from the_conf import TheConf
from yfinance import Ticker

metaconf = {
    "source_order": ["env", "files"],
    "config_files": [
        "~/.config/yfinance-exporter.json",
        "/etc/yfinance-exporter/yfinance-exporter.json",
    ],
    "parameters": [
        {"name": {"default": "yfinance-exporter"}},
        {
            "type": "list",
            "stocks": [
                {"name": {"type": str}},
                {"isin": {"type": str}},
                {"ycode": {"type": str}},
            ],
        },
        {"loop": [{"interval": {"type": int, "default": 240}}]},
        {
            "prometheus": [
                {"port": {"type": int, "default": 9100}},
                {"namespace": {"type": str, "default": ""}},
            ]
        },
        {"logging": [{"level": {"default": "WARNING"}}]},
    ],
}
conf = TheConf(metaconf)
logger = logging.getLogger("yfinance-exporter")
try:
    logger.setLevel(getattr(logging, conf.logging.level))
    logger.addHandler(logging.StreamHandler())
except AttributeError as error:
    raise AttributeError(
        f"{conf.logging.level} isn't accepted, only DEBUG, INFO, WARNING, "
        "ERROR and FATAL are accepted"
    ) from error

STOCK = Gauge(
    "financial_positions",
    "",
    [
        "bank",
        "account_type",
        "account_name",
        "account_id",
        "line_name",
        "line_id",
        "value_type",  # par-value, shares-value, gain, gain-percent, quantity
    ],
    namespace=conf.prometheus.namespace,
)


def collect(stock) -> bool:
    logger.debug("%r: Collecting", stock.name)
    labels = [
        stock.ycode.split(".")[1] if "." in stock.ycode else "",
        "stocks",
        "market",
        "market",
        stock.name,
        stock.isin,
        "par-value",
    ]
    ticker = Ticker(stock.ycode)
    try:
        value = ticker.fast_info["last_price"]
    except (KeyError, AttributeError):
        logger.warning("%r: no value from yfinance", stock.name)
        value = None
    if not isinstance(value, (int, float)):
        try:
            STOCK.remove(*labels)
        except KeyError:
            pass
        logger.debug("%r: found no value", stock.name)
        return False
    logger.debug("%r: found value %r", stock.name, value)
    STOCK.labels(*labels).set(value)
    return True


def main():
    info = {
        "loop-perid": conf.loop.interval,
        "item-count": len(conf.stocks),
    }
    daemon_metrics.init(conf.name, info)

    in_loop_interval = int(conf.loop.interval / (len(conf.stocks) + 1)) or 1
    while True:
        loop_context = daemon_metrics.LoopContext(conf.name)
        with loop_context:
            for stock in conf.stocks:
                result = collect(stock)
                daemon_metrics.item_result(conf.name, result, stock.isin)
                logger.debug("Wating computed interval %r", in_loop_interval)
                time.sleep(in_loop_interval)

        if (interval := conf.loop.interval - loop_context.exec_interval) > 0:
            logger.debug("Waiting %d to complete the loop interval", interval)
            time.sleep(interval)


if __name__ == "__main__":
    logger.info(
        "Starting yfinance exporter with %d stocks to watch", len(conf.stocks)
    )
    start_http_server(conf.prometheus.port)
    main()
