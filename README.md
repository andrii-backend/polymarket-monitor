# Polymarket Monitor

Python backend service for monitoring prediction markets and sending alerts.

## Features
- External API integration (Polymarket Gamma)
- Price, liquidity and 24h volume tracking
- Extreme condition detection (YES <= 0.01 or YES >= 0.99)
- Stateful alerting with anti-spam protection
- Telegram notifications with market context

## Tech stack
- Python
- REST APIs
- JSON data normalization
- Long-running background service
- VPS deployment

## How it works
- Periodically fetches market data from external API
- Normalizes inconsistent API fields
- Applies alerting rules
- Sends notifications to Telegram
- Stores state to prevent duplicate alerts

## Status
Running in production
