"""Risk policy — evaluates signals against risk parameters.

100% reusable from NBA bot: RiskParams + Signal → RiskDecision.
Pure math, no external dependencies.
"""

from ..types import RiskDecision, RiskParams, Signal, Trade


def evaluate_risk(
    signal: Signal,
    current_positions: list[Trade],
    params: RiskParams,
) -> RiskDecision:
    """Evaluate whether a signal should be traded given risk parameters.

    Checks (in order):
    1. Edge >= minimum edge threshold
    2. Confidence >= minimum confidence threshold
    3. Exposure per symbol <= max
    4. Kelly-style conservative sizing

    Returns a RiskDecision with approval status and adjusted amount.
    """
    # Check 1: Edge threshold
    if signal.edge < params.min_edge_threshold:
        return RiskDecision(
            approved=False,
            adjusted_amount=0.0,
            reason=f"Edge {signal.edge:.4f} below threshold {params.min_edge_threshold}",
        )

    # Check 2: Confidence threshold
    if signal.confidence < params.min_confidence_threshold:
        return RiskDecision(
            approved=False,
            adjusted_amount=0.0,
            reason=f"Confidence {signal.confidence:.2f} below threshold {params.min_confidence_threshold}",
        )

    # Check 3: Exposure per symbol
    symbol_exposure = sum(
        t.amount for t in current_positions if t.signal.symbol == signal.symbol
    )
    remaining = params.max_exposure_per_symbol - symbol_exposure
    if remaining <= 0:
        return RiskDecision(
            approved=False,
            adjusted_amount=0.0,
            reason=f"Max exposure reached for {signal.symbol}: ${symbol_exposure:.2f}",
        )

    # Check 4: Kelly-style conservative sizing
    # For crypto: edge represents expected excess return (e.g., 0.05 = 5% alpha).
    # Kelly criterion: f = edge (the edge IS the expected return).
    # Quarter-Kelly for safety: f = edge * kelly_fraction
    # Position = max_trade * edge * kelly_fraction * confidence
    kelly_adjusted = signal.edge * params.kelly_fraction
    raw_amount = params.max_trade_amount * kelly_adjusted * signal.confidence

    # Cap at remaining exposure and max trade amount
    adjusted_amount = min(raw_amount, remaining, params.max_trade_amount)

    if adjusted_amount <= 0.01:
        return RiskDecision(
            approved=False,
            adjusted_amount=0.0,
            reason="Amount too small after risk adjustment (< $0.01)",
        )

    return RiskDecision(
        approved=True,
        adjusted_amount=round(adjusted_amount, 2),
        reason=(
            f"Approved: ${adjusted_amount:.2f} on {signal.symbol} "
            f"(edge={signal.edge:.4f}, conf={signal.confidence:.2f}, "
            f"kelly={kelly_adjusted:.4f}, exposure=${symbol_exposure:.2f})"
        ),
    )
