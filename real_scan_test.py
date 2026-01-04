import time
import os
from dotenv import load_dotenv

from connectors.polymarket_gamma import fetch_polymarket_gamma_quotes
from schema import MarketQuote

SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL_SECONDS", 300))


def main():
    load_dotenv()

    print("Polymarket monitor started")

    while True:
        try:
            quotes = fetch_polymarket_gamma_quotes(limit=5)

            for q in quotes:
                if not isinstance(q, MarketQuote):
                    continue

                if q.yes_price is not None and (q.yes_price <= 0.01 or q.yes_price >= 0.99):
                    print(
                        f"[ALERT] {q.slug} | YES={q.yes_price} | "
                        f"liq={q.liquidity} | vol24h={q.volume_24h}"
                    )

        except Exception as e:
            print(f"[ERROR] {e}")

        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main()
