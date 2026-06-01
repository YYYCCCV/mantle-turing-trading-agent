"""Strategy engine — orchestrates signal generation and risk evaluation.

Port of the NBA bot's runStrategy(): takes data + config, outputs signals + summary.
100% reusable pattern: MarketData → Signal[] → RiskDecision[].
"""

from ..types import MarketData, RiskParams, Signal
from .risk import evaluate_risk, RiskDecision
from .signals import generate_all_signals


def run_strategy(
    market_data: dict[str, MarketData],
    risk_params: RiskParams,
) -> list[Signal]:
    """Run strategy engine on market data.

    Args:
        market_data: Dict mapping symbol → MarketData snapshot.
        risk_params: Risk configuration.

    Returns:
        List of Signals sorted by edge (strongest first).
    """
    if not market_data:
        return []

    all_signals: list[Signal] = []

    for symbol, data in market_data.items():
        signals = generate_all_signals(data, min_edge=risk_params.min_edge_threshold)
        all_signals.extend(signals)

    # Sort by edge descending
    all_signals.sort(key=lambda s: s.edge, reverse=True)
    return all_signals


def evaluate_signals(
    signals: list[Signal],
    current_positions: list,
    risk_params: RiskParams,
) -> list[tuple[Signal, RiskDecision]]:
    """Evaluate all signals through risk policy.

    Returns list of (signal, risk_decision) pairs — both approved and rejected.
    """
    results: list[tuple[Signal, RiskDecision]] = []
    for signal in signals:
        decision = evaluate_risk(signal, current_positions, risk_params)
        results.append((signal, decision))
    return results
