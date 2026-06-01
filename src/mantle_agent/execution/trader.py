"""Dry-run execution — simulates trades without real funds.

Port of the NBA bot's processSignals(): RiskDecision → Trade (dry_run).
No Bybit API keys needed. No real money at risk.
"""

from datetime import datetime

from ..strategy.risk import RiskDecision
from ..types import Direction, RiskParams, Signal, Trade, TradeStatus


def execute_trade(
    signal: Signal,
    decision: RiskDecision,
    dry_run: bool = True,
) -> Trade:
    """Execute a trade based on a risk-approved signal.

    In dry-run mode, no actual order is placed.
    The trade is recorded for audit and dashboard display.
    """
    if not decision.approved:
        return Trade(
            trade_id="",
            signal=signal,
            direction=signal.direction,
            amount=0.0,
            price=signal.market_price,
            status=TradeStatus.REJECTED,
            timestamp=datetime.now(),
            details=f"Rejected: {decision.reason}",
        )

    trade_id = f"{signal.type.value}_{signal.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

    if dry_run:
        status = TradeStatus.DRY_RUN
        details = f"DRY RUN: {decision.reason}"
    else:
        # Live execution would call Bybit API here
        # For MVP, live trading is disabled
        status = TradeStatus.EXECUTED
        details = f"LIVE: {decision.reason}"

    return Trade(
        trade_id=trade_id,
        signal=signal,
        direction=signal.direction,
        amount=decision.adjusted_amount,
        price=signal.market_price,
        status=status,
        timestamp=datetime.now(),
        details=details,
    )


def process_signals(
    signal_decisions: list[tuple[Signal, RiskDecision]],
    dry_run: bool = True,
) -> list[Trade]:
    """Process all signal-risk pairs into trades.

    Approved signals become trades (dry-run or live).
    Rejected signals are recorded as REJECTED trades for audit trail.
    """
    trades: list[Trade] = []

    for signal, decision in signal_decisions:
        trade = execute_trade(signal, decision, dry_run=dry_run)
        trades.append(trade)

    return trades
