"""Tests for signal generation strategies."""

import math
from datetime import datetime

import pytest

from mantle_agent.types import Direction, MarketData, SignalType
from mantle_agent.strategy.signals import (
    generate_all_signals,
    mean_reversion_signal,
    momentum_signal,
)


def _make_market_data(**overrides) -> MarketData:
    """Helper: create MarketData with sensible defaults."""
    defaults = {
        "symbol": "TEST-USD",
        "price": 100.0,
        "timestamp": datetime(2026, 6, 1, 12, 0, 0),
        "sma_short": 105.0,
        "sma_long": 100.0,
        "bb_upper": 110.0,
        "bb_middle": 100.0,
        "bb_lower": 90.0,
        "volume_ma": 10000.0,
        "current_volume": 20000.0,
        "funding_rate": 0.0001,
        "volatility": 0.5,
    }
    defaults.update(overrides)
    return MarketData(**defaults)


class TestMomentumSignal:
    """Momentum signal: SMA crossover with volume confirmation."""

    def test_triggers_buy_on_uptrend(self):
        """Momentum signal should trigger BUY when SMA_short > SMA_long with volume."""
        data = _make_market_data(sma_short=110.0, sma_long=100.0, current_volume=20000.0)
        signal = momentum_signal(data, min_edge=0.02)

        assert signal is not None
        assert signal.type == SignalType.MOMENTUM
        assert signal.direction == Direction.BUY
        assert signal.edge > 0.02
        assert signal.symbol == "TEST-USD"

    def test_triggers_sell_on_downtrend(self):
        """Momentum signal should trigger SELL when SMA_short < SMA_long with volume."""
        data = _make_market_data(sma_short=90.0, sma_long=100.0, current_volume=20000.0)
        signal = momentum_signal(data, min_edge=0.02)

        assert signal is not None
        assert signal.type == SignalType.MOMENTUM
        assert signal.direction == Direction.SELL
        assert signal.edge > 0.02

    def test_no_signal_below_edge_threshold(self):
        """Momentum signal should not trigger when edge is too small."""
        data = _make_market_data(sma_short=101.0, sma_long=100.0)
        signal = momentum_signal(data, min_edge=0.05)

        assert signal is None

    def test_no_signal_with_zero_sma(self):
        """Momentum signal requires valid SMA values."""
        data = _make_market_data(sma_short=0.0, sma_long=0.0)
        signal = momentum_signal(data)

        assert signal is None

    def test_confidence_bounded(self):
        """Confidence should stay within [0, 1]."""
        data = _make_market_data(sma_short=150.0, sma_long=100.0, current_volume=50000.0)
        signal = momentum_signal(data)

        assert signal is not None
        assert 0 <= signal.confidence <= 1.0

    def test_estimated_probability_bounded(self):
        """Estimated probability should stay within [0.05, 0.95]."""
        data = _make_market_data(sma_short=200.0, sma_long=100.0, current_volume=30000.0)
        signal = momentum_signal(data)

        assert signal is not None
        assert 0.05 <= signal.estimated_probability <= 0.95


class TestMeanReversionSignal:
    """Mean reversion signal: Bollinger Band deviation."""

    def test_triggers_buy_below_middle(self):
        """Should trigger BUY when price is below BB middle (oversold)."""
        data = _make_market_data(price=92.0, bb_upper=110.0, bb_middle=100.0, bb_lower=90.0)
        signal = mean_reversion_signal(data, min_edge=0.02)

        assert signal is not None
        assert signal.type == SignalType.MEAN_REVERSION
        assert signal.direction == Direction.BUY

    def test_triggers_sell_above_middle(self):
        """Should trigger SELL when price is above BB middle (overbought)."""
        data = _make_market_data(price=108.0, bb_upper=110.0, bb_middle=100.0, bb_lower=90.0)
        signal = mean_reversion_signal(data, min_edge=0.02)

        assert signal is not None
        assert signal.type == SignalType.MEAN_REVERSION
        assert signal.direction == Direction.SELL

    def test_triggers_at_lower_band(self):
        """Should trigger strong BUY at lower band extreme."""
        data = _make_market_data(price=90.5, bb_upper=110.0, bb_middle=100.0, bb_lower=90.0)
        signal = mean_reversion_signal(data, min_edge=0.01)

        assert signal is not None
        assert signal.direction == Direction.BUY
        assert signal.edge > 0.05

    def test_triggers_at_upper_band(self):
        """Should trigger strong SELL at upper band extreme."""
        data = _make_market_data(price=109.5, bb_upper=110.0, bb_middle=100.0, bb_lower=90.0)
        signal = mean_reversion_signal(data, min_edge=0.01)

        assert signal is not None
        assert signal.direction == Direction.SELL
        assert signal.edge > 0.05

    def test_no_signal_at_middle(self):
        """Should not trigger when price is at BB middle (no deviation)."""
        data = _make_market_data(price=100.0, bb_upper=110.0, bb_middle=100.0, bb_lower=90.0)
        signal = mean_reversion_signal(data, min_edge=0.05)

        assert signal is None

    def test_no_signal_with_zero_bands(self):
        """Requires valid Bollinger Band values."""
        data = _make_market_data(bb_upper=0.0, bb_middle=0.0, bb_lower=0.0)
        signal = mean_reversion_signal(data)

        assert signal is None

    def test_confidence_bounded(self):
        """Confidence should stay within [0, 1]."""
        data = _make_market_data(price=90.2, bb_upper=110.0, bb_middle=100.0, bb_lower=90.0)
        signal = mean_reversion_signal(data)

        assert signal is not None
        assert 0 <= signal.confidence <= 1.0


class TestGenerateAllSignals:
    """Integration: all signal generators run together."""

    def test_returns_list_sorted_by_edge(self):
        """generate_all_signals returns signals sorted by edge (descending)."""
        data = _make_market_data(
            price=92.0,
            sma_short=108.0, sma_long=100.0,
            bb_upper=110.0, bb_middle=100.0, bb_lower=90.0,
            current_volume=25000.0,
        )

        signals = generate_all_signals(data, min_edge=0.01)
        assert len(signals) > 0

        for i in range(len(signals) - 1):
            assert signals[i].edge >= signals[i + 1].edge

    def test_returns_empty_for_weak_data(self):
        """Should return empty list when no signals meet threshold."""
        data = _make_market_data(
            price=100.0,
            sma_short=100.5, sma_long=100.0,
            bb_upper=110.0, bb_middle=100.0, bb_lower=90.0,
            current_volume=1000.0, volume_ma=10000.0,
            volatility=0.1,
        )
        signals = generate_all_signals(data, min_edge=0.50)
        assert signals == []


class TestSignalImmutability:
    """Signals should be frozen (immutable) dataclasses."""

    def test_signal_is_frozen(self):
        """Signal dataclass should be immutable."""
        data = _make_market_data()
        signal = momentum_signal(data)

        assert signal is not None
        with pytest.raises(Exception):
            signal.edge = 0.99
