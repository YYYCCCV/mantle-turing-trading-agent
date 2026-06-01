# CC Handoff: Mantle Turing Test Hackathon

Project path:

```text
C:\Users\14817\Desktop\hackathons\mantle-turing-trading-agent
```

Objective:

Build the first MVP for a Mantle Turing Test Hackathon submission. The project should be an explainable AI trading/alpha agent, reusing the NBA bot's architecture but switching the domain from NBA prediction markets to crypto market signals.

Primary track:

- AI Trading Strategy

Backup track:

- AI Alpha Data

Use Python unless there is a strong reason not to.

## MVP Scope

Create a runnable paper-trading agent with:

1. Mock crypto market data
2. Signal generation
3. Risk policy
4. Dry-run execution
5. Audit logs
6. Terminal dashboard
7. Tests
8. README with demo commands

## Core Design

Use deterministic, testable strategy logic. The AI layer should explain decisions, not secretly decide trades.

Suggested flow:

```text
market data -> signal engine -> risk policy -> dry-run executor -> audit logs -> dashboard
```

## Signals

Implement at least:

- Momentum signal
- Mean reversion signal

Optional if fast:

- Volatility breakout signal
- Funding divergence signal

## Risk Policy

Implement:

- Minimum edge threshold
- Minimum confidence threshold
- Max trade amount
- Max exposure per symbol
- Kelly-style conservative sizing
- Dry-run only by default

## Demo Command

The final demo should support a command similar to:

```bash
python -m mantle_agent --demo
```

Expected demo output should include:

- Symbols scanned
- Signals generated
- Trades simulated
- Risk rejections if any
- Audit log path

## Tests

Start with focused tests:

- Momentum signal triggers in an upward trend
- Mean reversion signal triggers on large deviation
- Risk rejects weak signals
- Risk caps oversized trades
- Engine produces deterministic demo output

## Constraints

- Do not use live funds.
- Do not require Bybit API keys for MVP.
- Do not make network access required for the demo.
- Do not build frontend yet.
- Keep it ready for a 3-minute demo video.

## Useful Reference

NBA project to reuse concepts from:

```text
C:\Users\14817\Desktop\hackathons\nba-prediction-market
```

The reusable idea is the structure, not the NBA-specific code.
