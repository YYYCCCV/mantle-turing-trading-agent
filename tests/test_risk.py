"""Tests for risk policy."""

from datetime import datetime

import pytest

from mantle_agent.types import (
    Direction,
    RiskDecision,
    RiskParams,
    Signal,
    SignalType,
    Trade,
    TradeStatus,
)
from mantle_agent.strategy.risk import evaluate_risk


def _make_signal(symbol: str = "BTC-USD", **overrides) -> Signal:
    """Helper: create a Signal with sensible defaults."""
    defaults = {
        "type": SignalType.MOMENTUM,
        "symbol": symbol,
        "direction": Direction.BUY,
        "estimated_probability": 0.65,
        "market_price": 95000.0,
        "edge": 0.05,
        "confidence": 0.70,
        "reason": "Test signal",
        "timestamp": datetime(2026, 6, 1, 12, 0, 0),
    }
    defaults.update(overrides)
    return Signal(**defaults)


def _make_params(**overrides) -> RiskParams:
    """Helper: create RiskParams with sensible defaults."""
    defaults = {
        "max_trade_amount": 1000.0,
        "min_edge_threshold": 0.02,
        "min_confidence_threshold": 0.3,
        "max_exposure_per_symbol": 5000.0,
        "kelly_fraction": 0.25,
        "dry_run": True,
    }
    defaults.update(overrides)
    return RiskParams(**defaults)


class TestEdgeThreshold:
    """Risk should reject signals below edge threshold."""

    def test_rejects_below_edge(self):
        """Signal with edge below min_edge_threshold should be rejected."""
        signal = _make_signal(edge=0.01)
        params = _make_params(min_edge_threshold=0.02)
        decision = evaluate_risk(signal, [], params)

        assert decision.approved is False
        assert decision.adjusted_amount == 0.0
        assert "below threshold" in decision.reason.lower()

    def test_accepts_above_edge(self):
        """Signal with edge above min_edge_threshold should be approved."""
        signal = _make_signal(edge=0.05)
        params = _make_params(min_edge_threshold=0.02)
        decision = evaluate_risk(signal, [], params)

        assert decision.approved is True
        assert decision.adjusted_amount > 0

    def test_accepts_at_edge_boundary(self):
        """Signal with edge exactly at threshold should be approved."""
        signal = _make_signal(edge=0.02)
        params = _make_params(min_edge_threshold=0.02)
        decision = evaluate_risk(signal, [], params)

        assert decision.approved is True


class TestConfidenceThreshold:
    """Risk should reject signals below confidence threshold."""

    def test_rejects_below_confidence(self):
        """Signal with confidence below threshold should be rejected."""
        signal = _make_signal(edge=0.10, confidence=0.15)
        params = _make_params(min_confidence_threshold=0.3)
        decision = evaluate_risk(signal, [], params)

        assert decision.approved is False
        assert "confidence" in decision.reason.lower()

    def test_accepts_above_confidence(self):
        """Signal with confidence above threshold should be approved."""
        signal = _make_signal(confidence=0.80)
        params = _make_params(min_confidence_threshold=0.3)
        decision = evaluate_risk(signal, [], params)

        assert decision.approved is True


class TestExposureCap:
    """Risk should cap exposure per symbol."""

    def test_rejects_when_exposure_exceeded(self):
        """Should reject when existing positions already at max exposure."""
        signal = _make_signal(symbol="BTC-USD")
        params = _make_params(max_exposure_per_symbol=100.0)

        existing = [
            Trade(
                trade_id="t1",
                signal=signal,
                direction=Direction.BUY,
                amount=100.0,
                price=95000.0,
                status=TradeStatus.DRY_RUN,
                timestamp=datetime.now(),
                details="",
            )
        ]
        decision = evaluate_risk(signal, existing, params)

        assert decision.approved is False
        assert "max exposure" in decision.reason.lower()

    def test_caps_within_remaining_exposure(self):
        """Should cap trade amount to remaining exposure."""
        signal = _make_signal(symbol="ETH-USD", edge=0.10, market_price=3200.0)
        params = _make_params(
            max_trade_amount=10000.0,
            max_exposure_per_symbol=200.0,
        )

        existing = [
            Trade(
                trade_id="t1",
                signal=signal,
                direction=Direction.BUY,
                amount=150.0,
                price=3200.0,
                status=TradeStatus.DRY_RUN,
                timestamp=datetime.now(),
                details="",
            )
        ]
        decision = evaluate_risk(signal, existing, params)

        assert decision.approved is True
        assert decision.adjusted_amount <= 50.0


class TestKellySizing:
    """Risk should use conservative Kelly-style sizing."""

    def test_kelly_proportional_to_edge(self):
        """Higher edge should produce larger position size."""
        weak_signal = _make_signal(edge=0.03, market_price=100.0)
        strong_signal = _make_signal(edge=0.10, market_price=100.0)
        params = _make_params(max_trade_amount=10000.0)

        weak_decision = evaluate_risk(weak_signal, [], params)
        strong_decision = evaluate_risk(strong_signal, [], params)

        assert strong_decision.adjusted_amount > weak_decision.adjusted_amount

    def test_kelly_capped_at_max_trade(self):
        """Position size should not exceed max_trade_amount."""
        signal = _make_signal(edge=0.50, market_price=100.0, confidence=1.0)
        params = _make_params(max_trade_amount=1000.0)

        decision = evaluate_risk(signal, [], params)

        assert decision.adjusted_amount <= 1000.0

    def test_kelly_conservative_scaling(self):
        """Quarter-Kelly should be conservative — max ~2.5% of trade limit."""
        signal = _make_signal(edge=0.10, market_price=100.0)
        params = _make_params(max_trade_amount=100000.0, kelly_fraction=0.25)

        decision = evaluate_risk(signal, [], params)

        # edge=0.10, kelly_fraction=0.25 → kelly_adjusted=0.025
        # raw = 100000 * 0.025 * 0.70 = $1,750 = 1.75% of max
        assert decision.adjusted_amount < 2000.0
        assert decision.adjusted_amount > 0


class TestRiskDecisionImmutability:
    """RiskDecision should be frozen."""

    def test_risk_decision_is_frozen(self):
        signal = _make_signal()
        params = _make_params()
        decision = evaluate_risk(signal, [], params)

        with pytest.raises(Exception):
            decision.approved = False
