# Mantle Turing Test Hackathon Plan

## Positioning

Build a verifiable AI trading and alpha agent for the Mantle Turing Test Hackathon.

Primary track:

- AI Trading Strategy

Backup track:

- AI Alpha Data

The project should reuse the strongest parts of the NBA prediction market bot: signal generation, conservative risk sizing, dry-run execution, audit logs, tests, dashboard, and demo workflow.

## Product Thesis

Most trading agents are either black-box chatbots or unverified signal scripts. This project should present a small but complete trading agent loop:

```text
market data -> alpha signals -> risk policy -> dry-run execution -> audit log -> performance report
```

The key differentiator is not "AI makes trades." The key differentiator is that every decision is explainable, logged, and reproducible.

## MVP

Name:

- Mantle Alpha Trading Agent

One-line description:

- An explainable AI trading agent that generates crypto alpha signals, applies conservative risk controls, and records every decision for auditability and future on-chain verification.

Core modules:

- `data/`: market prices, funding rates, volume, volatility, and mock fallback data
- `signals/`: momentum, mean reversion, volatility breakout, and alpha-news placeholders
- `risk/`: max position, max drawdown, confidence threshold, Kelly-style sizing
- `execution/`: dry-run paper trading first, optional Bybit execution later
- `audit/`: JSONL decision logs, performance summary, reproducible runs
- `dashboard/`: terminal dashboard for demo

## Reuse From NBA Project

Directly reusable:

- Strategy engine shape
- Signal interface
- Risk evaluator pattern
- Dry-run trader pattern
- Dashboard/reporting style
- Demo video structure

Needs replacement:

- ESPN data -> crypto market data
- Polymarket data -> Bybit/CEX/DEX market data
- NBA injury signals -> crypto alpha signals

## Signal Ideas

Start with deterministic, explainable signals:

1. Momentum signal
   - If short moving average crosses above long moving average and volume expands, generate BUY.

2. Mean reversion signal
   - If price deviates strongly from rolling mean and volatility is normal, generate counter-trend signal.

3. Funding/market stress signal
   - If funding rate and price momentum diverge, mark crowded positioning risk.

4. Volatility breakout signal
   - If realized volatility expands above threshold with volume confirmation, generate breakout signal.

AI layer:

- Use an LLM only to summarize signals and produce a human-readable trade rationale.
- Keep the actual trade decision deterministic and testable.

## Demo Requirements

The demo should show:

- Tests passing
- Data loading
- Signal generation
- Risk checks
- Dry-run trades
- Audit logs
- Performance summary
- Mantle/on-chain verification roadmap

## Submission Story

Judges should understand this as:

- A practical trading agent, not a chatbot
- Safe by default through dry-run mode
- Built for auditability
- Ready to connect to Mantle for identity, reputation, or performance records

## Do Not Do Yet

- Do not connect real funds.
- Do not implement live trading first.
- Do not overbuild frontend.
- Do not make the LLM the source of trading truth.
- Do not start three hackathons at once.
