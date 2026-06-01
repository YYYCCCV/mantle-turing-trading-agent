# 3-Minute Demo Video Script

**Mantle Turing Test Hackathon — Mantle Alpha Trading Agent**

Total target: 3 minutes (180 seconds). Each section has a timing budget.

---

## Scene 1: Hook & Problem (0:00 — 0:25) [25s]

**Visual**: Terminal showing a black-box trading bot with gibberish output, then crossfade to our clean terminal.

**Narration**:
"Most AI trading agents are black boxes. You can't verify their decisions, you can't audit their trades, and you definitely can't reproduce their results. For the Mantle Turing Test Hackathon, I built something different."

---

## Scene 2: What It Is (0:25 — 0:50) [25s]

**Visual**: Architecture diagram (simple text flow in terminal or a slide).

**Narration**:
"Mantle Alpha Trading Agent is an explainable trading harness. Mock market data feeds into a deterministic signal engine. Signals go through a conservative risk policy. Trades execute in dry-run mode only. Every decision is logged. Every run is reproducible."

**Visual**: Show the README architecture section.

---

## Scene 3: Tests Passing (0:50 — 1:10) [20s]

**Visual**: Run `pytest -v` in terminal, scroll through green dots.

**Narration**:
"37 tests. All passing. Signal generation, risk evaluation, end-to-end pipeline. Every strategy is a pure function — same input, same output, every time. No randomness. No hidden state."

**Commands to show**:
```bash
pytest -v
```

---

## Scene 4: Code Walkthrough (1:10 — 1:40) [30s]

**Visual**: Quick cuts through key source files.

**Narration**:
"The code is organized into clean modules. Types are immutable dataclasses — frozen, no mutation. Signals are pure functions that take market data and return optional signals. Risk is a chain of checks: edge threshold, confidence threshold, exposure caps, then Kelly-style position sizing. The trader executes paper trades only — no API keys, no real money."

**Files to flash**:
- `types.py` — frozen dataclasses
- `signals.py` — momentum, mean reversion, volatility breakout
- `risk.py` — Kelly sizing, exposure caps
- `trader.py` — dry-run execution

---

## Scene 5: Live Demo (1:40 — 2:20) [40s]

**Visual**: Run `python -m mantle_agent --demo` and scroll through output.

**Narration**:
"Let me run the full demo. It generates deterministic mock market data for BTC, ETH, and SOL — no network required. The strategy engine fires three signals. The risk policy approves all three. Three paper trades execute with conservative sizing — see the amounts: $151, $142, $63 from a $1,000 max. That's quarter-Kelly at work."

**Commands to show**:
```bash
python -m mantle_agent --demo
```

**Key moments to pause on**:
- Market data output (symbols, prices, indicators)
- Signal generation (edge, confidence, reason)
- Trade execution (amounts, status DRY RUN)

---

## Scene 6: Audit Log & Mantle Roadmap (2:20 — 2:50) [30s]

**Visual**: Open the JSONL audit log file, then show the roadmap section from the dashboard.

**Narration**:
"Every run writes a JSONL audit log — signals, risk decisions, trades, all time-stamped and machine-readable. This is the foundation for Mantle integration. Step one: sign agent decisions with a Mantle wallet. Step two: record decision hashes on-chain for immutable verification. Step three: build reputation from verified performance. Step four: enable a decentralized strategy marketplace where agents compose and compete."

**Show**:
- JSONL audit log file contents
- Dashboard roadmap section

---

## Scene 7: Close (2:50 — 3:00) [10s]

**Visual**: Back to the terminal showing the full dashboard.

**Narration**:
"Mantle Alpha Trading Agent. Deterministic. Auditable. Ready for on-chain verification. Thank you."

---

## Recording Notes

- Terminal font: use a readable monospace (Cascadia Code, JetBrains Mono, or Fira Code).
- Terminal background: dark theme for contrast.
- Record at 1080p, 30fps.
- No face cam needed — screen recording with voiceover is sufficient.
- Keep typing to a minimum — prefer running commands that produce immediate output.
- If the terminal output scrolls too fast, use `| head -20` or similar to keep key content visible.

## Pre-Recording Checklist

- [ ] Fresh terminal, clean background
- [ ] `pip install -e ".[dev]"` already done
- [ ] `pytest -v` runs clean (37 passed)
- [ ] `python -m mantle_agent --demo` produces clean output
- [ ] JSONL audit log exists from a previous run
- [ ] README architecture section ready to show
- [ ] Microphone tested
