"""
Polymarket Gamma API connector.

Responsible for fetching market data from Polymarket Gamma API
and converting it into unified MarketQuote objects.

Design goals:
- no secrets in code
- tolerant to missing fields
- safe float parsing
- easy to extend (CLOB / orderbook fields)
"""

import os
import time
from typing import Any, Dict, List, Optional

import requests

from schema import MarketQuote


# ===== Configuration =====

GAMMA_BASE_URL = os.getenv(
    "POLYMARKET_GAMMA_BASE_URL",
    "https://gamma-api.polymarket.com",
)

HTTP_TIMEOUT = float(os.getenv("POLYMARKET_HTTP_TIMEOUT", "20"))

# Optional proxy support (e.g. residential proxies)
HTTP_PROXY = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
HTTPS_PROXY = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")

PROXIES = None
if HTTP_PROXY or HTTPS_PROXY:
    PROXIES = {
        "http": HTTP_PROXY,
        "https": HTTPS_PROXY or HTTP_PROXY,
    }

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
}

# =========================


def _get_float(d: Dict[str, Any], *keys: str) -> Optional[float]:
    """
    Try to extract and convert the first existing key to float.
    """
    for k in keys:
        if k in d and d[k] is not None:
            try:
                return float(d[k])
            except Exception:
                pass
    return None


def _calc_spread(bid: Optional[float], ask: Optional[float]) -> Optional[float]:
    """
    Spread = (ask - bid) / ask
    """
    if bid is None or ask is None:
        return None
    if bid <= 0 or ask <= 0 or ask < bid:
        return None
    return (ask - bid) / ask


def _mid_price(bid: Optional[float], ask: Optional[float]) -> Optional[float]:
    """
    Mid-price from bid/ask.
    """
    if bid is None or ask is None:
        return None
    if bid <= 0 or ask <= 0:
        return None
    return (bid + ask) / 2.0


def _safe_get_json(url: str, params: Dict[str, Any]) -> Any:
    """
    GET request with minimal retry logic.
    """
    for attempt in range(2):
        try:
            r = requests.get(
                url,
                params=params,
                headers=DEFAULT_HEADERS,
                timeout=HTTP_TIMEOUT,
                proxies=PROXIES,
            )
            r.raise_for_status()
            return r.json()
        except Exception:
            if attempt == 0:
                time.sleep(1.0)
                continue
            raise


def fetch_polymarket_gamma_quotes(
    limit: int = 200,
    offset: int = 0,
) -> List[MarketQuote]:
    """
    Fetch active Polymarket markets from Gamma API
    and return them as MarketQuote objects.
    """
    url = f"{GAMMA_BASE_URL}/markets"
    params = {
        "active": "true",
        "closed": "false",
        "archived": "false",
        "limit": int(limit),
        "offset": int(offset),
    }

    data = _safe_get_json(url, params)

    if isinstance(data, list):
        markets = data
    elif isinstance(data, dict) and isinstance(data.get("data"), list):
        markets = data["data"]
    else:
        return []

    quotes: List[MarketQuote] = []

    for m in markets:
        if not isinstance(m, dict):
            continue

        market_id = str(
            m.get("id")
            or m.get("marketId")
            or m.get("market_id")
            or ""
        )

        slug = m.get("slug")
        raw_url = m.get("url")
        url_market = raw_url or (
            f"https://polymarket.com/market/{slug}"
            if slug
            else None
        )

        # Prices
        yes_price = _get_float(
            m, "yesPrice", "yes_price", "bestYesPrice"
        )
        no_price = _get_float(
            m, "noPrice", "no_price", "bestNoPrice"
        )

        # Liquidity & volume
        liquidity = _get_float(
            m, "liquidityNum", "liquidity", "liquidityClob"
        )
        volume_24h = _get_float(
            m, "volume24hr", "volume24hrClob", "volume_24h"
        )

        # Orderbook (CLOB)
        best_yes_bid = _get_float(
            m, "bestYesBid", "bestBid", "yesBestBid"
        )
        best_yes_ask = _get_float(
            m, "bestYesAsk", "bestAsk", "yesBestAsk"
        )

        best_no_bid = _get_float(
            m, "bestNoBid", "noBestBid"
        )
        best_no_ask = _get_float(
            m, "bestNoAsk", "noBestAsk"
        )

        spread_yes = _calc_spread(best_yes_bid, best_yes_ask)
        spread_no = _calc_spread(best_no_bid, best_no_ask)

        # Derive mid-price if direct price is missing
        if yes_price is None:
            yes_price = _mid_price(best_yes_bid, best_yes_ask)
        if no_price is None:
            no_price = _mid_price(best_no_bid, best_no_ask)

        quotes.append(
            MarketQuote(
                platform="polymarket",
                market_id=market_id,
                slug=slug,
                url=url_market,
                yes_price=yes_price,
                no_price=no_price,
                liquidity=liquidity,
                volume_24h=volume_24h,
                best_yes_bid=best_yes_bid,
                best_yes_ask=best_yes_ask,
                best_no_bid=best_no_bid,
                best_no_ask=best_no_ask,
                spread_yes=spread_yes,
                spread_no=spread_no,
            )
        )

    return quotes
