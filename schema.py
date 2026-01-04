from dataclasses import dataclass
from typing import Optional


@dataclass
class MarketQuote:
    """
    Unified market snapshot for Polymarket (Gamma / CLOB).

    This dataclass represents a single market state at a given moment
    and is designed to be:
    - serializable
    - easy to extend
    - safe for partially missing data (Optionals)

    Used by scanners, filters, and alerting logic.
    """

    # --- Identity ---
    platform: str                 # e.g. "polymarket"
    market_id: str                # unique market id from API
    slug: Optional[str] = None    # human-readable market slug
    url: Optional[str] = None     # direct link to market page

    # --- Prices ---
    yes_price: Optional[float] = None  # YES price (or mid-price if derived)
    no_price: Optional[float] = None   # NO price (or mid-price if derived)

    # --- Liquidity & volume ---
    liquidity: Optional[float] = None   # total market liquidity (USD)
    volume_24h: Optional[float] = None  # 24h traded volume (USD)

    # --- Orderbook (CLOB) ---
    best_yes_bid: Optional[float] = None  # best bid for YES
    best_yes_ask: Optional[float] = None  # best ask for YES
    best_no_bid: Optional[float] = None   # best bid for NO
    best_no_ask: Optional[float] = None   # best ask for NO

    # --- Derived metrics ---
    spread_yes: Optional[float] = None  # (ask - bid) / ask for YES
    spread_no: Optional[float] = None   # (ask - bid) / ask for NO
