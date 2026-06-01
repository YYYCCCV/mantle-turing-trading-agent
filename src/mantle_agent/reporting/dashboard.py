"""Terminal dashboard — renders run summary for demo.

Port of the NBA bot's printDashboard(): RunSummary → styled terminal output.
Designed for a 3-minute demo video: clear, visual, scannable.

Note: Uses ASCII-safe characters only — Windows GBK terminal cannot render emoji.
"""

from ..types import RunSummary, TradeStatus


def print_dashboard(summary: RunSummary) -> None:
    """Print a styled terminal dashboard for a run summary."""
    SEP = "-" * 62

    print()
    print("=" * 60)
    print("  [M]  MANTLE ALPHA TRADING AGENT  [M]")
    print("       Mantle Turing Test Hackathon -- MVP")
    print("=" * 60)
    print()
    print(f"{SEP}")
    print("  [*]  RUN SUMMARY")
    print(f"{SEP}")
    print(f"  Timestamp         : {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Symbols Scanned   : {summary.symbols_scanned}")
    print(f"  Signals Generated : {len(summary.signals_generated)}")
    print(f"  Signals Rejected  : {len(summary.signals_rejected)}")
    print(f"  Trades Executed   : {len(summary.trades_executed)}")
    print(f"{SEP}")

    # Signals section
    if summary.signals_generated:
        print("  [>>]  SIGNALS GENERATED")
        print(f"{SEP}")
        for s in summary.signals_generated:
            direction_icon = "[BUY]" if s.direction.value == "BUY" else "[SELL]"
            print(f"  {direction_icon} [{s.type.value:20s}] {s.symbol:8s} "
                  f"{s.direction.value:4s} | "
                  f"edge={s.edge:.4f} | conf={s.confidence:.2f} | "
                  f"price=${s.market_price:.2f}")
            print(f"       |-- {s.reason}")
            print()
    else:
        print("  [!!]  No signals generated this run.")
        print()

    # Risk rejections
    if summary.signals_rejected:
        print(f"  [!!]  RISK REJECTIONS ({len(summary.signals_rejected)})")
        print(f"{SEP}")
        for s in summary.signals_rejected:
            direction_icon = "[BUY]" if s.direction.value == "BUY" else "[SELL]"
            print(f"  [X] [{s.type.value:20s}] {s.symbol:8s} "
                  f"{s.direction.value:4s} | "
                  f"edge={s.edge:.4f} | conf={s.confidence:.2f}")
            print(f"       |-- {s.reason}")
            print()

    # Trades section
    if summary.trades_executed:
        print(f"  [$]  TRADES ({len(summary.trades_executed)})")
        print(f"{SEP}")
        for t in summary.trades_executed:
            if t.status == TradeStatus.DRY_RUN:
                status_label = "[DRY RUN]"
            elif t.status == TradeStatus.EXECUTED:
                status_label = "[LIVE]"
            elif t.status == TradeStatus.REJECTED:
                status_label = "[REJECTED]"
            else:
                status_label = f"[{t.status.value}]"

            print(f"  {status_label:14s} {t.direction.value:4s} "
                  f"${t.amount:>8.2f} @ ${t.price:.2f} "
                  f"on {t.signal.symbol}")
            reason_short = t.details[:80] + "..." if len(t.details) > 80 else t.details
            print(f"       |-- {reason_short}")
            print()

    # Audit log
    if summary.audit_log_path:
        print(f"{SEP}")
        print(f"  [@]  Audit Log: {summary.audit_log_path}")
        print(f"{SEP}")

    # Mantle roadmap
    print(f"  [M]  Mantle On-Chain Roadmap:")
    print(f"      1. Sign agent decisions with Mantle identity")
    print(f"      2. Record trade hashes on Mantle for auditability")
    print(f"      3. Build on-chain reputation from verified performance")
    print(f"      4. Enable decentralized strategy marketplace")
    print(f"{SEP}")
    print()
