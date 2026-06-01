# Mantle Alpha Trading Agent — BUIDL Submission

**Mantle Turing Test Hackathon 2026**

## Project

| Field | Value |
|-------|-------|
| **Name** | Mantle Alpha Trading Agent |
| **Primary Track** | AI Trading Strategy |
| **Backup Track** | AI Alpha Data |
| **Repo** | https://github.com/YYYCCCV/mantle-turing-trading-agent |
| **Stack** | Python 3.10+, pytest, zero external API dependencies for demo |

## One-Liner

An explainable AI trading agent that generates crypto alpha signals from deterministic strategies, applies conservative risk controls, and records every decision for future on-chain verification on Mantle.

## The Problem

Most "AI trading agents" fall into two camps:
1. **Black-box chatbots** that claim AI makes trade decisions, with no way to verify, audit, or reproduce results.
2. **Unverified signal scripts** that post trade ideas with no risk management, no execution trail, and no accountability.

Neither is suitable for Mantle's vision of verifiable on-chain agents.

## Our Approach

We built a **small, complete, auditable trading-agent harness** where:
- The strategy layer is **deterministic** — same inputs always produce the same outputs.
- The AI layer can **explain** decisions without secretly making trades.
- Every decision is **logged** in JSONL format for future Mantle anchoring.
- The agent runs **paper-trading only** by default — safe to demo, safe to iterate.

```text
mock market data -> signal engine -> risk policy -> dry-run trader -> audit log -> dashboard
```

## What It Does

### Signals (3 strategies)

| Signal | Logic | Direction |
|--------|-------|-----------|
| **Momentum** | SMA(10) vs SMA(30) crossover + volume expansion | BUY if short > long, SELL if short < long |
| **Mean Reversion** | Price deviation from Bollinger Bands (20, 2σ) | BUY near lower band, SELL near upper band |
| **Volatility Breakout** | Realized vol > 80% annualized + volume > 1.2x average | Follows short-term SMA trend |

### Risk Policy (6 checks)

1. Minimum edge threshold (default: 0.02)
2. Minimum confidence threshold (default: 0.30)
3. Maximum trade amount (default: $1,000)
4. Maximum exposure per symbol (default: $5,000)
5. Kelly-style conservative sizing (quarter-Kelly)
6. Dry-run-only execution (no real funds)

### Audit Trail

Every run produces a JSONL audit log with:
- Run metadata (timestamp, symbols scanned, counts)
- Every signal generated (type, direction, edge, confidence, reason)
- Every risk decision (approved/rejected, adjusted amount, rationale)
- Every trade executed (status, amount, price, details)

## Demo

```bash
# Install
pip install -e ".[dev]"

# Run the full demo (no network, no API keys, no real funds)
python -m mantle_agent --demo

# Run 37 tests
pytest -v
```

### Demo Output

```text
[Mantle Agent] Mode: DRY RUN
[Mantle Agent] Generating mock market data for 3 symbols...
  BTC-USD: price=$99709.86, SMA10=100935.06, SMA30=99641.02
  ETH-USD: price=$3014.03, SMA10=3117.08, SMA30=3120.54
  SOL-USD: price=$169.73, SMA10=178.50, SMA30=177.68

[Mantle Agent] Running strategy engine...
[Mantle Agent] Generated 3 signals

[Mantle Agent] Evaluating risk policy...
[Mantle Agent] Approved: 3, Rejected: 0

[Mantle Agent] Executing trades (DRY RUN)...
[Mantle Agent] Dry-run trades: 3, Rejected: 0
```

## Test Coverage

37 tests across 3 files, all passing:

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_signals.py` | 11 | Momentum, mean reversion, volatility breakout, edge cases |
| `test_risk.py` | 11 | Edge/confidence thresholds, exposure caps, Kelly sizing |
| `test_engine.py` | 15 | Determinism, E2E pipeline, demo symbols, dry-run enforcement |

## Architecture

```text
src/mantle_agent/
|-- __init__.py
|-- __main__.py            # python -m mantle_agent --demo
|-- config.py              # Environment-based configuration
|-- types.py               # 11 immutable dataclasses
|-- data/
|   |-- mock_market.py     # Deterministic mock data (BTC/ETH/SOL)
|-- strategy/
|   |-- engine.py          # Strategy orchestrator
|   |-- signals.py         # 3 signal generators
|   |-- risk.py            # Risk evaluator (Kelly sizing)
|-- execution/
|   |-- trader.py          # Dry-run paper trading
|-- reporting/
|   |-- dashboard.py       # ASCII-safe terminal dashboard
|   |-- logger.py          # JSONL audit logger
```

## Mantle Integration Path

The MVP is intentionally local-first. The Mantle integration path:

1. **Identity**: Sign agent decisions with a Mantle wallet — proving which agent made which call.
2. **Verification**: Record decision hashes on Mantle for immutable audit trail.
3. **Reputation**: Build on-chain reputation from verified, time-stamped performance records.
4. **Marketplace**: Enable decentralized strategy composability — agents that can coordinate, compete, or compose.

## Key Differentiator

Not "AI makes the trades." **Every trade is deterministic, explainable, and auditable.** The AI layer can explain *why* a signal fired, but the signal itself is a pure function — reproducible by anyone running the same code.

## What We Did NOT Build (On Purpose)

- No live trading or real funds
- No Bybit API integration (MVP is fully offline)
- No frontend (terminal dashboard for demo)
- No LLM in the trading decision path (explainability layer only)
- No black-box AI decision-making

## Team

Mantle Turing Test Team — solo contributor.

## License

MIT
