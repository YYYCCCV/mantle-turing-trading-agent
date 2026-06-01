# BUIDL Submission — DoraHacks

> Copy-paste ready for the DoraHacks BUIDL form.

---

## Project Name

**Mantle Alpha Trading Agent**

## Tagline / Short Description

An explainable AI trading agent that generates crypto alpha signals from deterministic strategies, applies conservative risk controls, and records every decision — built for auditability and future on-chain verification on Mantle.

## Project Description

A runnable, testable, paper-trading agent that demonstrates the full trading-agent loop without black-box AI decision-making.

**Three Signal Strategies:**

1. **Momentum** — SMA(10) vs SMA(30) crossover with volume expansion confirmation. BUY on bullish crossover, SELL on bearish crossover.

2. **Mean Reversion** — Bollinger Band (20, 2σ) deviation. BUY near lower band (oversold), SELL near upper band (overbought).

3. **Volatility Breakout** — Realized volatility > 80% annualized with volume > 1.2x average. Follows short-term trend direction.

**Conservative Risk Layer (6 Checks):**

Every signal must pass: minimum edge threshold, minimum confidence threshold, maximum trade amount, maximum exposure per symbol, quarter-Kelly position sizing, and dry-run-only execution.

**Full Audit Trail:**

JSONL audit logs record every signal generated, every risk decision (approved or rejected with rationale), and every trade executed. The log is machine-readable and ready for Mantle on-chain anchoring.

**Architecture:**

```text
mock market data -> signal engine -> risk policy -> dry-run trader -> audit log -> dashboard
```

All strategy modules are pure functions with zero external dependencies — fully reusable across data sources and trading platforms.

## How It Works

1. **Data**: Deterministic mock market data for BTC-USD, ETH-USD, SOL-USD. Generates 60-bar OHLCV series with computed SMA, Bollinger Bands, volume profile, and annualized volatility. No network required for demo.

2. **Signal Generation**: Three independent signal generators run on each symbol. Each signal is a pure function — same input always produces the same output. Signals include edge (statistical alpha), confidence, and a human-readable reason string.

3. **Risk Evaluation**: Quarter-Kelly formula: `position = max_trade × edge × kelly_fraction × confidence`. Enforces per-symbol exposure caps. Rejected signals are logged with rejection reasons.

4. **Execution**: Dry-run paper trading only by default. `DRY_RUN=false` must be explicitly set to enable live execution — even with API keys present.

5. **Audit Logging**: JSONL format. Each run appends a run_start entry, all signal entries, all trade entries. Timestamped and machine-readable.

6. **Dashboard**: ASCII-safe terminal output showing run summary, signals with edge/confidence, trades with amounts, risk rejections, audit log path, and Mantle on-chain roadmap.

## Source Code URL

https://github.com/YYYCCCV/mantle-turing-trading-agent

## Demo Video URL

[TBD — upload to YouTube and paste URL here]

## Documentation / Setup Instructions

```bash
git clone https://github.com/YYYCCCV/mantle-turing-trading-agent.git
cd mantle-turing-trading-agent
pip install -e ".[dev]"

# Run all tests (37/37)
pytest -v

# Run demo (no network, no API keys, no real funds)
python -m mantle_agent --demo

# Custom risk parameters
python -m mantle_agent --demo --max-trade 500 --min-edge 0.03

# Coverage report
pytest --cov=mantle_agent --cov-report=term-missing
```

**Environment variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| DRY_RUN | true | Dry-run mode (no real money) |
| MAX_TRADE_AMOUNT | 1000 | Max USD per trade |
| MIN_EDGE_THRESHOLD | 0.02 | Minimum edge to trigger |
| MIN_CONFIDENCE_THRESHOLD | 0.30 | Minimum confidence to execute |
| MAX_EXPOSURE_PER_SYMBOL | 5000 | Max exposure per symbol |
| KELLY_FRACTION | 0.25 | Kelly fraction (0.25 = quarter-Kelly) |

## Technologies Used

- **Python 3.10+** — Full type annotations, immutable dataclasses
- **pytest** — 37 tests across 3 test files, all passing
- **Deterministic Mock Data** — Sine-trend model with fixed seed, no network required
- **Quarter-Kelly Criterion** — Conservative position sizing
- **JSONL Audit Logs** — Machine-readable, append-only decision trail
- **Pure Function Architecture** — All strategy modules: MarketData → Signal, zero side effects

## Hackathon Tracks / Themes Covered

- **AI Trading Strategy** (primary) — Complete trading agent with explainable signal generation and risk management
- **AI Alpha Data** (backup) — Signal engine produces structured alpha data with edge, confidence, and rationale
- **On-Chain Verification** — JSONL audit trail designed for Mantle anchoring (identity → hashing → reputation → marketplace)
- **Safe by Default** — Dry-run only. Real execution requires explicit opt-in. No real funds at risk.

## What Makes It Different

- **Not a chatbot**: The AI layer explains decisions — it doesn't secretly make them. Every signal is a deterministic pure function.
- **Reproducible**: Same mock data, same seed, same output — every time. Judges can clone and verify.
- **Auditable**: JSONL logs capture every decision. Ready to hash and anchor on Mantle for immutable verification.
- **Zero network dependency**: Demo runs fully offline. No API keys, no VPN, no real funds.
- **Architecture designed for migration**: Core strategy modules (signals.py, risk.py, engine.py) accept generic MarketData and output generic Signals — swap the data source without touching the logic.
- **37/37 tests passing**: Signals, risk, engine, end-to-end pipeline — all covered.

## Automation Logs

Sample execution from `python -m mantle_agent --demo`:

```text
[Mantle Agent] Mode: DRY RUN
[Mantle Agent] Max trade: $1000 | Min edge: 0.02 | Min confidence: 0.3
[Mantle Agent] Kelly fraction: 0.25

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

============================================================
  [M]  MANTLE ALPHA TRADING AGENT  [M]
       Mantle Turing Test Hackathon -- MVP
============================================================

--------------------------------------------------------------
  [*]  RUN SUMMARY
--------------------------------------------------------------
  Timestamp         : 2026-06-01 16:49:48
  Symbols Scanned   : 3
  Signals Generated : 3
  Signals Rejected  : 0
  Trades Executed   : 3
--------------------------------------------------------------
  [>>]  SIGNALS GENERATED
--------------------------------------------------------------
  [BUY] [mean_reversion      ] ETH-USD  BUY  | edge=0.6734 | conf=0.90 | price=$3014.03
       |-- MeanReversion: price=3014.03 near lower band (16.3%)

  [BUY] [mean_reversion      ] SOL-USD  BUY  | edge=0.6297 | conf=0.90 | price=$169.73
       |-- MeanReversion: price=169.73 near lower band (18.5%)

  [BUY] [mean_reversion      ] BTC-USD  BUY  | edge=0.3554 | conf=0.71 | price=$99709.86
       |-- MeanReversion: price=99709.86 near lower band (32.2%)

  [$]  TRADES (3)
--------------------------------------------------------------
  [DRY RUN]      BUY  $  151.51 @ $3014.03 on ETH-USD
  [DRY RUN]      BUY  $  141.68 @ $169.73 on SOL-USD
  [DRY RUN]      BUY  $   63.16 @ $99709.86 on BTC-USD

--------------------------------------------------------------
  [@]  Audit Log: .../logs/run_2026-06-01.jsonl
--------------------------------------------------------------
  [M]  Mantle On-Chain Roadmap:
      1. Sign agent decisions with Mantle identity
      2. Record trade hashes on Mantle for auditability
      3. Build on-chain reputation from verified performance
      4. Enable decentralized strategy marketplace
```

## Judge Cues

- Code is clean, well-typed, and fully tested (37/37 passing)
- Architecture designed for Mantle integration: audit trail ready for on-chain anchoring
- Built with real-world constraints in mind (deterministic, reproducible, Windows GBK terminal compatible)
- Risk management is serious: quarter-Kelly + exposure caps + edge/confidence thresholds + dry-run default
- Not a black-box chatbot: AI explains, pure functions decide
- Zero network dependency: clone, install, run — that's it

## Team

Mantle Turing Test Team — solo contributor.

## License

MIT
