<p align="center"> <img src="https://raw.githubusercontent.com/gunthardeniro/gunbot-sdk-python/main/assets/logo.svg" width="96" alt="Gunbot SDK logo"></p>

# Gunbot SDK for **Python**

**Python client for the Gunbot REST API for automated crypto‑/ETF‑/stock trading**

[![PyPI](https://img.shields.io/pypi/v/gunbot-sdk-python.svg)](https://pypi.org/project/gunbot-sdk-python)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> Programmatically control **Gunbot** – the self‑hosted automated trading bot – from Python scripts, notebooks, CI jobs or serverless functions.

---

## Key Features

* **100 % OpenAPI 3.0 generated** – every endpoint stays in sync with Gunbot Core
* **Typed models & services** – PEP 561 compliant type hints for better IDE experience
* Single source that works in **CPython ≥ 3.9** and **PyPy**
* **Zero dynamic dependencies** beyond the auto‑generated `urllib3` stack
* MIT‑licensed – free for commercial and open‑source use

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Supported Exchanges](#supported-exchanges)
5. [API Coverage](#api-coverage)
6. [Type Hints](#type-hints)
7. [Authentication](#authentication)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)
11. [License](#license)

---

## Installation

```bash
# pip
to install: pip install gunbot-sdk-python
# poetry
poetry add gunbot-sdk-python
# pipenv
pipenv install gunbot-sdk-python
```

The distribution installs an **import package** named `gunbot_sdk`.

---

## Quick Start

```python
from datetime import datetime, timedelta
from gunbot_sdk import ApiClient, GunbotApi

# 1 – configure the shared ApiClient
api = ApiClient(
    base_path="http://localhost:3000/api/v1",   # ← REST base
    bearer_token="<JWT‑TOKEN>"                   # ← your bearer token
)

# 2 – create a service wrapper
gunbot = GunbotApi(api)

# 3 – call an endpoint
print("orders:", gunbot.orders("binance/USDT-BTC"))
```

> Replace `base_path` and `bearer_token` with values from your own Gunbot deployment.

Documentation for every method is generated under `docs/`, and available on github pages: [documentation](https://gunthardeniro.github.io/gunbot-python-js/).

---

## Configuration

| Option                                 | Default                        | Description                                           |
| -------------------------------------- | ------------------------------ | ----------------------------------------------------- |
| `base_path` (parameter of `ApiClient`) | `http://localhost:3000/api/v1` | Gunbot REST base path                                 |
| `bearer_token`                         | –                              | JWT from GUI localStorage or `/auth/login` |
| `timeout` (`ApiClient` kwarg)          | `60_000` ms                    | Request timeout                                       |
| `user_agent` (`ApiClient` kwarg)       | `gunbot-sdk-python/<version>`  | Custom UA header                                      |

---

## Supported Exchanges

> Gunbot ships with native connectors for **25 + exchanges**.

| Exchange                     | Spot |       Futures / Perps      | DeFi (on‑chain) | Extra notes         |
| ---------------------------- | :--: | :------------------------: | :-------------: | ------------------- |
| **Binance**                  |  ✔️  |     ✔️ (USD‑M & COIN‑M)    |                 | Largest liquidity   |
| **Binance US**               |  ✔️  |                            |                 | US‑regulated arm    |
| **Bitget**                   |  ✔️  |    ✔️ (USDT & UM perps)    |                 |                     |
| **Bybit**                    |  ✔️  |  ✔️ (USDT & inverse perps) |                 |                     |
| **OKX**                      |  ✔️  | ✔️ (Perps & dated futures) |                 |                     |
| **Kraken**                   |  ✔️  |   ✔️ (via Kraken Futures)  |                 |                     |
| **KuCoin**                   |  ✔️  |                            |                 |                     |
| **Gate.io**                  |  ✔️  |                            |                 |                     |
| **MEXC**                     |  ✔️  |                            |                 |                     |
| **BingX**                    |  ✔️  |                            |                 |                     |
| **Crypto.com**               |  ✔️  |                            |                 |                     |
| **Huobi Global**             |  ✔️  |                            |                 |                     |
| **Bitfinex**                 |  ✔️  |                            |                 |                     |
| **HitBTC**                   |  ✔️  |                            |                 |                     |
| **Coinbase Advanced Trade**  |  ✔️  |                            |                 | Former Coinbase Pro |
| **CEX.io**                   |  ✔️  |                            |                 |                     |
| **Poloniex**                 |  ✔️  |                            |                 |                     |
| **Alpaca** (stocks & crypto) |  ✔️  |                            |                 |                     |
| **dYdX (v3/v4)**             |      |             ✔️             |        ✔️       | Perpetual DEX       |
| **HyperLiquid**              |  ✔️  |             ✔️             |        ✔️       | DeFi perps          |
| **PancakeSwap**              |      |             ✔️             |        ✔️       | BSC DEX             |
| **Bitmex / Bitmex Testnet**  |      |             ✔️             |                 |                     |

---

## API Coverage

This SDK targets **Gunbot REST v1** (`/api/v1`), built from the official OpenAPI spec.

| Tag / Section | Status |
| ------------- | ------ |
| Auth          | ✅      |
| Market Data   | ✅      |
| Orders        | ✅      |
| Strategy      | ✅      |
| Wallet        | ✅      |
| Exchange Mgmt | ✅      |

---

## Type Hints

The wheel ships PEP 561 metadata so editors such as **VS Code**, **PyCharm** or **Neovim (pylsp)** show inline completions and docstrings.

---

## Authentication

* **Bearer Token** – easiest: copy from Gunbot GUI `localStorage.jwtToken`.
* **Password Encryption** – To fetch a token programmatically, follow the [Gunbot docs](https://www.gunbot.com/support/docs/rest-api/api-auth/#encryption-helpers).
* Always use **HTTPS** when connecting over public networks.

---

## Examples

The code sets up the SDK client, creates a `GunbotApi` instance, and calls most of the available endpoints, so you can run it once to verify connectivity and see the expected argument patterns and raw responses. Use it as a reference checklist when integrating the SDK.

``` python
#!/usr/bin/env python3
"""
run_examples.py – complete parity demo for the Gunbot Python SDK
Requires:  pip install gunbot-sdk   (your renamed package)

HOW IT WORKS ------------------------------------------------------
1.  ApiClient sets REST base + Bearer token in one call.
2.  Every endpoint uses snake_case.
3.  POST/PUT endpoints take the JSON payload as 1st arg **body=...**.
4.  Path/query-only endpoints map exactly to their URL params.
-------------------------------------------------------------------
"""

from datetime import datetime, timedelta
from gunbot_sdk import ApiClient, GunbotApi


def ts(*, days: int = 0, hours: int = 0) -> int:
    """Return a UTC Unix timestamp in **milliseconds** with offset."""
    return int((datetime.utcnow() + timedelta(days=days, hours=hours)).timestamp() * 1000)


def main() -> None:
    # ───────────────── 1. CLIENT CONFIG ─────────────────
    api_client = ApiClient(
        base_path="http://localhost:3000/api/v1",
        bearer_token="<YOUR-JWT-HERE>",
    )

    # ───────────────── 2. SERVICE WRAPPER ───────────────
    gunbot = GunbotApi(api_client)

    # ───────────────── 3. EXAMPLES ──────────────────────
    # ---------- SYSTEM / AUTH ----------
    print("auth_status:", gunbot.auth_status())
    print("time:", gunbot.time())
    print("system_start:", gunbot.system_start())
    print("system_stop:", gunbot.system_stop())

    # ---------- CONFIGURATION ----------
    print("config_full:", gunbot.config_full())

    print("config_update:", gunbot.config_update(body={
        "data": {}      # full Gunbot config object
    }))

    print("config_pair_add:", gunbot.config_pair_add(body={
        "pair": "USDT-BTC",
        "exchange": "binance",
        "settings": {
            "strategy": "stepgrid",
            "enabled": True,
            "override": {
                "BUY_METHOD": "stepgrid",
                "SELL_METHOD": "stepgrid",
                "GAIN": "2",
            },
        },
    }))

    print("config_pair_remove:", gunbot.config_pair_remove(body={
        "pair": "USDT-BTC",
        "exchange": "binance",
    }))

    print("config_strategy_add:", gunbot.config_strategy_add(body={
        "name": "MY-STRATEGY",
        "settings": {"SOME_PARAM": True, "MORE_PARAMS": 2},
    }))

    print("config_strategy_remove:", gunbot.config_strategy_remove(body={
        "name": "MY-STRATEGY",
    }))

    # ---------- MARKET DATA ----------
    print("assets_total:", gunbot.assets_total(body={
        "exchange": "binance",
        "base": "USDT",
        "start": ts(days=-1),
        "end": ts(),
    }))

    print("chart_data:", gunbot.chart_data(body={
        "exchange": "binance",
        "pair": "USDT-BTC",
        "interval": "1h",
        "start": ts(days=-3),
        "end": ts(),
    }))

    print("chart_marks:", gunbot.chart_marks(
        "binance", "USDT-BTC", "1h", ts(days=-1), ts()
    ))

    print("market_candles:", gunbot.market_candles("binance/USDT-BTC"))
    print("market_orderbook:", gunbot.market_orderbook("binance/USDT-BTC"))

    # ---------- CORE MEMORY ----------
    print("coremem:", gunbot.coremem())

    print("coremem_request:", gunbot.coremem_request(body={
        "exchange": "binance",
        "pair": "USDT-BTC",
        "elements": [],
    }))

    print("coremem_single:", gunbot.coremem_single(body={
        "exchange": "binance",
        "pair": "USDT-BTC",
    }))

    # ---------- ORDERS ----------
    print("orders:", gunbot.orders("binance/USDT-BTC"))
    print("orders_page:", gunbot.orders_page("binance/USDT-BTC", 0, 50))
    print("orders_page_multi:", gunbot.orders_page_multi(
        ["binance/USDT-BTC", "binance/USDT-BTC"], 0, 100
    ))
    print("orders_day:", gunbot.orders_day("Europe/Berlin", ["binance/USDT-BTC"]))

    # ---------- BALANCES & PAIRS ----------
    print("balances:", gunbot.balances())
    print("pairs:", gunbot.pairs("binance"))
    print("pairs_detailed:", gunbot.pairs_detailed("binance"))

    # ---------- PNL ----------
    print("pnl_daily:", gunbot.pnl_daily("binance/USDT-BTC", ts(days=-1), ts()))
    print("pnl_daily_paginated:", gunbot.pnl_daily_paginated(
        "binance/USDT-BTC", 1, 30, ts()
    ))
    print("pnl_sum:", gunbot.pnl_sum("binance", ts(days=-7), ts()))
    print("pnl_total:", gunbot.pnl_total("binance/USDT-BTC"))

    print("pnl_overview:", gunbot.pnl_overview(body={
        "timezone": "Europe/Berlin",
        "keys": ["binance/USDT-BTC"],
    }))

    # ---------- FILES ----------
    print("files_state:", gunbot.files_state())
    print("files_strategy:", gunbot.files_strategy())

    print("files_strategy_write:", gunbot.files_strategy_write(body={
        "filename": "apistrat.js",
        "document": "full strategy as string",
    }))

    print("files_strategy_delete:", gunbot.files_strategy_delete(body={
        "filename": "apistrat.js",
    }))

    print("files_strategy_get:", gunbot.files_strategy_get(body={
        "filename": "mfi.js",
    }))

    print("files_acvar_get:", gunbot.files_acvar_get(body={
        "filename": "autoconfig-variables.json",
    }))

    print("files_acvar:", gunbot.files_acvar())

    print("files_autoconfig_write:", gunbot.files_autoconfig_write(body={
        # "document": {...}
    }))

    print("files_custom_editor_write:", gunbot.files_custom_editor_write(body={
        "document": {"test": True},
    }))

    print("files_custom_editor_get:", gunbot.files_custom_editor_get())
    print("files_backup:", gunbot.files_backup())

    print("files_backup_get:", gunbot.files_backup_get(body={
        "filename": "autoconfig.json.1623252417412",
    }))

    # ---------- TRADING ----------
    print("trade_buy:", gunbot.trade_buy(body={
        "exch": "binance",
        "pair": "USDT-BTC",
        "price": 100000,
        "amt": 0.001,
    }))

    print("trade_sell:", gunbot.trade_sell(body={
        "exch": "binance",
        "pair": "USDT-BTC",
        "price": 100000,
        "amt": 0.001,
    }))

    print("trade_buy_market:", gunbot.trade_buy_market(body={
        "exch": "binance",
        "pair": "USDT-BTC",
        "price": 100000,     # 0 if live trading
        "amt": 0.001,
    }))

    print("trade_sell_market:", gunbot.trade_sell_market(body={
        "exch": "binance",
        "pair": "USDT-BTC",
        "price": 100000,
        "amt": 0.001,
    }))


if __name__ == "__main__":
    main()

```

---

## Troubleshooting

| Symptom             | Checklist                                          |
| ------------------- | -------------------------------------------------- |
| 401 Unauthorized    | ✓ Valid token? ✓ Correct `base_path`?              |
| 400 Bad Request     | ✓ Payload shape vs spec? ✓ Missing required param? |
| `ConnectionRefused` | ✓ Gunbot core running? ✓ Port forwarded/open?      |

Set environment variable `GUNBOT_SDK_DEBUG=1` for verbose request/response logs.

---

## Contributing

1. Fork → PR
2. Follow Conventional Commits for commits & PR titles

---

## License

MIT – see [`LICENSE`](./LICENSE).
