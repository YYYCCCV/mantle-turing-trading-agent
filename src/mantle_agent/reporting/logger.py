"""JSONL audit logger — records every decision for reproducibility.

Port of the NBA bot's writeRunLog(): RunSummary → JSONL file.
Every signal, risk decision, and trade is logged for auditability.
"""

import json
import os
from datetime import datetime

from ..types import RunSummary, Signal, Trade


def get_log_dir() -> str:
    """Get the logs directory path (alongside package)."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_dir = os.path.join(project_root, "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def write_run_log(summary: RunSummary) -> str:
    """Write run summary as JSONL audit log.

    Returns the path to the written log file.
    """
    log_dir = get_log_dir()
    date_str = summary.timestamp.strftime("%Y-%m-%d")
    log_path = os.path.join(log_dir, f"run_{date_str}.jsonl")

    entries = []

    # Header entry
    entries.append({
        "type": "run_start",
        "timestamp": summary.timestamp.isoformat(),
        "symbols_scanned": summary.symbols_scanned,
        "signals_generated": len(summary.signals_generated),
        "signals_rejected": len(summary.signals_rejected),
        "trades_executed": len(summary.trades_executed),
    })

    # Signal entries
    for s in summary.signals_generated:
        entries.append(_signal_to_dict(s))

    # Rejected signal entries
    for s in summary.signals_rejected:
        entry = _signal_to_dict(s)
        entry["type"] = "signal_rejected"
        entries.append(entry)

    # Trade entries
    for t in summary.trades_executed:
        entries.append(_trade_to_dict(t))

    # Write JSONL
    with open(log_path, "a", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return log_path


def _signal_to_dict(s: Signal) -> dict:
    return {
        "type": "signal",
        "signal_type": s.type.value,
        "symbol": s.symbol,
        "direction": s.direction.value,
        "estimated_probability": s.estimated_probability,
        "market_price": s.market_price,
        "edge": s.edge,
        "confidence": s.confidence,
        "reason": s.reason,
        "timestamp": s.timestamp.isoformat(),
    }


def _trade_to_dict(t: Trade) -> dict:
    return {
        "type": "trade",
        "trade_id": t.trade_id,
        "symbol": t.signal.symbol,
        "direction": t.direction.value,
        "amount": t.amount,
        "price": t.price,
        "status": t.status.value,
        "details": t.details,
        "timestamp": t.timestamp.isoformat(),
    }
