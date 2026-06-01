# Mantle Alpha Trading Agent

An explainable AI trading agent MVP for the Mantle Turing Test Hackathon.

The agent generates crypto alpha signals, applies conservative risk controls, executes paper trades in dry-run mode, and records every decision in audit logs. It is built for reproducibility first, then future Mantle-based verification.

## Quick Demo

```bash
pip install -e ".[dev]"
python -m mantle_agent --demo
pytest -v
```

The demo runs fully offline with deterministic mock market data. No API keys, network access, or real funds are required.

## What It Shows

The MVP demonstrates a complete trading-agent loop:

```text
mock market data -> signal engine -> risk policy -> dry-run trader -> audit log -> dashboard
```

The current demo scans BTC, ETH, and SOL market data, generates explainable signals, applies risk checks, simulates trades, and writes JSONL audit records.

## Core Features

- Deterministic mock data for BTC-USD, ETH-USD, and SOL-USD.
- Momentum, mean reversion, and volatility breakout signal generators.
- Conservative risk policy with edge, confidence, exposure, and Kelly-style sizing.
- Dry-run execution only by default.
- JSONL audit logs for every run.
- Terminal dashboard for a simple hackathon demo.
- 37 passing tests across signals, risk, engine, and end-to-end flow.

## Architecture

```text
MarketData
  -> Signal Engine
  -> Risk Policy
  -> Paper Trader
  -> Audit Logger
  -> Terminal Dashboard
```

## Module Map

| Module | Purpose |
| --- | --- |
| `data/mock_market.py` | Deterministic mock crypto data. |
| `strategy/signals.py` | Momentum, mean reversion, and volatility breakout signals. |
| `strategy/risk.py` | Edge, confidence, exposure, and Kelly-style risk checks. |
| `strategy/engine.py` | Orchestrates data and signal generation. |
| `execution/trader.py` | Paper-trading execution, dry-run only. |
| `reporting/dashboard.py` | ASCII-safe terminal dashboard. |
| `reporting/logger.py` | JSONL audit logs. |
| `__main__.py` | CLI entry point for `python -m mantle_agent --demo`. |

## Signal Strategies

| Signal | Trigger | Direction |
| --- | --- | --- |
| Momentum | Short moving average diverges from long moving average with volume support. | BUY or SELL with trend. |
| Mean reversion | Price moves toward Bollinger band extremes. | BUY near lower band, SELL near upper band. |
| Volatility breakout | Realized volatility expands with volume confirmation. | Follows short-term trend. |

## Risk Policy

Every signal must pass:

- Minimum edge threshold.
- Minimum confidence threshold.
- Maximum trade amount.
- Maximum exposure per symbol.
- Kelly-style conservative sizing.
- Dry-run-only execution.

## Example Output

```text
[Mantle Agent] Mode: DRY RUN
[Mantle Agent] Generating mock market data for 3 symbols...
[Mantle Agent] Running strategy engine...
[Mantle Agent] Generated 3 signals
[Mantle Agent] Approved: 3, Rejected: 0
[Mantle Agent] Dry-run trades: 3, Rejected: 0
```

## Mantle Integration Roadmap

The MVP is intentionally local and deterministic. The integration path has two tracks: Mantle for on-chain verification and Bybit for live market data (when ready).

### Mantle On-Chain Verification

Each phase builds on the audit trail already in place:

**Phase 1 — Identity (MVP-ready)**
- Sign agent run summaries with a Mantle wallet.
- Publish agent identity on Mantle so verifiers can confirm which agent produced which decisions.
- No trading changes needed — just add a signature to the existing JSONL log.

**Phase 2 — Anchoring (post-MVP)**
- Hash each signal, risk decision, and trade record into a Merkle tree.
- Post the Merkle root to Mantle at configurable intervals (every run, hourly, daily).
- The on-chain root anchors the full off-chain audit trail — anyone with the log can verify it against the root.

**Phase 3 — Reputation (post-MVP)**
- Build a Mantle smart contract that tracks agent performance over time.
- Metrics: Sharpe ratio, win rate, max drawdown, signal accuracy, risk compliance.
- Reputation is non-transferable and cryptographically tied to the agent identity from Phase 1.

**Phase 4 — Marketplace (vision)**
- Agents with verified reputation can list strategies on Mantle.
- Strategy composability: agents can consume each other's signals as inputs.
- Decentralized signal marketplace with on-chain settlement and reputation slashing.

### Bybit API Integration (Architecture Plan)

The agent is designed with a clean seam for live data. No live trading until fully tested.

```text
                    +------------------+
                    |   Bybit API v5   |
                    +--------+---------+
                             |
                    +--------v---------+
                    |  bybit_adapter.py |  <- NEW (not built yet)
                    +--------+---------+
                             |
              +--------------+--------------+
              |                             |
     +--------v---------+         +---------v--------+
     |  MarketData       |         |  Trade Execution  |
     |  (live prices,    |         |  (Bybit order API) |
     |   order book,     |         |                    |
     |   funding rate)   |         |  DRY_RUN guard     |
     +------------------+         +-------------------+
```

**What changes:**
1. New `data/bybit_adapter.py` — fetches live OHLCV, funding rates, and order book data from Bybit API v5.
2. New `execution/bybit_trader.py` — places real orders only when `DRY_RUN=false`.
3. `config.py` gets `BYBIT_API_KEY` and `BYBIT_API_SECRET` env vars.

**What does NOT change:**
- Signal generators stay pure functions (MarketData in, Signal out).
- Risk policy stays identical (it operates on Signal, not on data source).
- Audit logger stays identical.
- The mock data path remains the default for testing and demo.

**Safety guard:** Live trading requires an explicit `DRY_RUN=false` environment variable. Without it, all execution paths default to paper trading — even if Bybit API keys are present.

## Why It Fits The Hackathon

This is not a black-box trading chatbot. It is a small, auditable trading-agent harness:

- The strategy layer is deterministic.
- The AI layer can explain decisions without secretly making trades.
- The paper-trading loop is safe by default.
- The audit trail is ready to be anchored on-chain.

## Commands

```bash
# Run the default demo
python -m mantle_agent --demo

# Custom risk parameters
python -m mantle_agent --demo --max-trade 500 --min-edge 0.03

# Run all tests
pytest -v

# Run coverage
pytest --cov=mantle_agent --cov-report=term-missing
```

## Project Structure

```text
src/mantle_agent/
|-- __init__.py
|-- __main__.py
|-- config.py
|-- types.py
|-- data/
|   `-- mock_market.py
|-- strategy/
|   |-- engine.py
|   |-- signals.py
|   `-- risk.py
|-- execution/
|   `-- trader.py
`-- reporting/
    |-- dashboard.py
    `-- logger.py

tests/
|-- test_engine.py
|-- test_risk.py
`-- test_signals.py
```
