"""Entry point: python -m mantle_agent --demo

Wires together the full trading agent pipeline:
market data → signal engine → risk policy → dry-run executor → audit logs → dashboard
"""

import argparse
import sys
from datetime import datetime

from .config import DEMO_SYMBOLS, load_risk_params
from .data.mock_market import generate_demo_data
from .execution.trader import process_signals
from .reporting.dashboard import print_dashboard
from .reporting.logger import write_run_log
from .strategy.engine import evaluate_signals, run_strategy
from .types import RunSummary


def run_demo() -> RunSummary:
    """Run a complete demo trading cycle with mock data.

    This is the primary demo command for the hackathon submission.
    """
    risk_params = load_risk_params()

    print(f"\n[Mantle Agent] Mode: {'DRY RUN' if risk_params.dry_run else 'LIVE'}")
    print(f"[Mantle Agent] Max trade: ${risk_params.max_trade_amount:.0f} | "
          f"Min edge: {risk_params.min_edge_threshold} | "
          f"Min confidence: {risk_params.min_confidence_threshold}")
    print(f"[Mantle Agent] Kelly fraction: {risk_params.kelly_fraction}")

    # Step 1: Generate mock market data
    print(f"\n[Mantle Agent] Generating mock market data for {len(DEMO_SYMBOLS)} symbols...")
    market_data = generate_demo_data()
    for symbol, data in market_data.items():
        print(f"  {symbol}: price=${data.price:.2f}, "
              f"SMA10={data.sma_short:.2f}, SMA30={data.sma_long:.2f}, "
              f"BB=[{data.bb_lower:.2f},{data.bb_upper:.2f}], "
              f"vol={data.volatility:.1%}")

    # Step 2: Run strategy engine
    print(f"\n[Mantle Agent] Running strategy engine...")
    signals = run_strategy(market_data, risk_params)
    print(f"[Mantle Agent] Generated {len(signals)} signals")

    # Step 3: Evaluate risk
    print(f"\n[Mantle Agent] Evaluating risk policy...")
    signal_decisions = evaluate_signals(signals, [], risk_params)

    approved_count = sum(1 for _, d in signal_decisions if d.approved)
    rejected_count = len(signal_decisions) - approved_count
    print(f"[Mantle Agent] Approved: {approved_count}, Rejected: {rejected_count}")

    # Step 4: Execute trades (dry-run)
    print(f"\n[Mantle Agent] Executing trades (DRY RUN)...")
    trades = process_signals(signal_decisions, dry_run=risk_params.dry_run)

    dry_run_trades = [t for t in trades if t.status.value == "dry_run"]
    rejected_trades = [t for t in trades if t.status.value == "rejected"]
    print(f"[Mantle Agent] Dry-run trades: {len(dry_run_trades)}, "
          f"Rejected: {len(rejected_trades)}")

    # Step 5: Build summary
    approved_signals = [s for s, d in signal_decisions if d.approved]
    rejected_signals = [s for s, d in signal_decisions if not d.approved]

    summary = RunSummary(
        timestamp=datetime.now(),
        symbols_scanned=len(market_data),
        signals_generated=approved_signals,
        signals_rejected=rejected_signals,
        trades_executed=trades,
    )

    # Step 6: Write audit log
    log_path = write_run_log(summary)
    summary = RunSummary(
        timestamp=summary.timestamp,
        symbols_scanned=summary.symbols_scanned,
        signals_generated=summary.signals_generated,
        signals_rejected=summary.signals_rejected,
        trades_executed=summary.trades_executed,
        audit_log_path=log_path,
    )

    # Step 7: Print dashboard
    print_dashboard(summary)

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mantle Alpha Trading Agent — Turing Test Hackathon MVP"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        default=True,
        help="Run demo with mock market data (default)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Dry-run mode — no real trades (default)",
    )
    parser.add_argument(
        "--max-trade",
        type=float,
        default=1000.0,
        help="Max trade amount in USD",
    )
    parser.add_argument(
        "--min-edge",
        type=float,
        default=0.02,
        help="Minimum edge threshold",
    )
    args = parser.parse_args()

    # Override env vars with CLI args
    import os
    os.environ["MAX_TRADE_AMOUNT"] = str(args.max_trade)
    os.environ["MIN_EDGE_THRESHOLD"] = str(args.min_edge)

    summary = run_demo()

    # Print summary for scripting
    print(f"\n[Mantle Agent] Demo complete.")
    print(f"  Symbols scanned:     {summary.symbols_scanned}")
    print(f"  Signals generated:   {len(summary.signals_generated)}")
    print(f"  Signals rejected:    {len(summary.signals_rejected)}")
    print(f"  Trades executed:     {len(summary.trades_executed)}")
    print(f"  Audit log:           {summary.audit_log_path}")


if __name__ == "__main__":
    main()
