[![PyPI - Version](https://img.shields.io/pypi/v/yfinance-exporter)](https://pypi.org/project/yfinance-exporter/) [![Docker Image Version](https://img.shields.io/docker/v/jaesivsm/yfinance-exporter)](https://hub.docker.com/r/jaesivsm/yfinance-exporter/tags)

# YFinance Exporter


## Metrics served


```json
{
    "stocks": [
        {"isin": "FR0000120073", "name": "AIR LIQUIDE", "ycode": "AI.PA"}
    ]
}
```

## Running it

For the next few bits of code, we'll suppose you have a working configuration above in `~/.config/yfinance-exporter.json`.

### ... with python:

```shell
pip install yfinance-exporter
python -m yfinance_exporter
```

### ... with docker:

```shell
 docker run -v ~/.config/:/etc/yfinance-exporter/:ro -p 9100:9100 yfinance-exporter:main
```

You'll then be able retrieve some values:

```shell
curl localhost:9100/metrics

# HELP yfinance_exporter
# TYPE yfinance_exporter gauge
yfinance_exporter{status="loop"} 1.0
yfinance_exporter{status="loop-time"} 10.179875
yfinance_exporter{status="ok-stock"} 45.0
yfinance_exporter{status="ko-stock"} 2.0
[...]
```
