"""Signal generation strategies.

Each signal is a pure function: MarketData + config → optional Signal.
Deterministic, testable, and explainable — the AI layer summarizes, it doesn't decide.
"""

import math
from datetime import datetime

from ..config import VOLUME_EXPANSION_THRESHOLD
from ..types import Direction, MarketData, Signal, SignalType


def momentum_signal(data: MarketData, min_edge: float = 0.02) -> Signal | None:
    """Generate a momentum signal based on SMA crossover.

    BUY when: SMA_short crosses ABOVE SMA_long AND volume expands
    SELL when: SMA_short crosses BELOW SMA_long AND volume expands

    Edge is proportional to the crossover strength.
    Confidence scales with volume confirmation.
    """
    if data.sma_short == 0 or data.sma_long == 0:
        return None

    crossover_pct = (data.sma_short - data.sma_long) / data.sma_long
    edge = abs(crossover_pct)

    if edge < min_edge:
        return None

    # Volume confirmation: signal stronger when volume > average
    volume_ratio = data.current_volume / data.volume_ma if data.volume_ma > 0 else 1.0
    volume_confirm = volume_ratio >= VOLUME_EXPANSION_THRESHOLD

    direction = Direction.BUY if crossover_pct > 0 else Direction.SELL

    # Confidence: crossover strength + volume expansion
    confidence = min(edge * 15 + (0.1 if volume_confirm else 0), 0.95)

    # Estimated probability: price deviation from long SMA
    if direction == Direction.BUY:
        estimated_prob = 0.5 + edge
    else:
        estimated_prob = 0.5 - edge
    estimated_prob = max(0.05, min(0.95, estimated_prob))

    return Signal(
        type=SignalType.MOMENTUM,
        symbol=data.symbol,
        direction=direction,
        estimated_probability=round(estimated_prob, 4),
        market_price=data.price,
        edge=round(edge, 4),
        confidence=round(confidence, 4),
        reason=(
            f"Momentum: SMA_short({data.sma_short:.2f}) {direction.value} "
            f"vs SMA_long({data.sma_long:.2f}), "
            f"crossover={crossover_pct:+.2%}, "
            f"volume_ratio={volume_ratio:.1f}x"
        ),
        timestamp=data.timestamp,
    )


def mean_reversion_signal(data: MarketData, min_edge: float = 0.02) -> Signal | None:
    """Generate a mean reversion signal based on Bollinger Band deviation.

    BUY when: price is near/below lower band (oversold → expect reversion up)
    SELL when: price is near/above upper band (overbought → expect reversion down)

    Edge is proportional to the distance from the band.
    Confidence scales with deviation extremity.
    """
    if data.bb_middle == 0 or math.isnan(data.bb_middle):
        return None

    # Compute z-score relative to Bollinger Bands
    bb_range = data.bb_upper - data.bb_lower
    if bb_range <= 0:
        return None

    # Position within bands: 0 = at lower, 1 = at upper
    band_position = (data.price - data.bb_lower) / bb_range

    # Edge: how far from middle (0.5 = center)
    deviation = abs(band_position - 0.5)
    edge = deviation * 2  # scale to 0-1 range

    if edge < min_edge:
        return None

    if band_position < 0.5:
        direction = Direction.BUY   # below middle → buy for reversion up
    else:
        direction = Direction.SELL  # above middle → sell for reversion down

    # Confidence: stronger at extremes
    confidence = min(edge * 2, 0.90)

    # Estimated probability: reversion toward middle
    estimated_prob = 0.5 + (0.5 - band_position)
    estimated_prob = max(0.05, min(0.95, estimated_prob))

    # Enhance reason with band information
    if band_position <= 0.05:
        band_desc = "below lower band"
    elif band_position >= 0.95:
        band_desc = "above upper band"
    elif band_position < 0.5:
        band_desc = f"near lower band ({band_position:.1%})"
    else:
        band_desc = f"near upper band ({band_position:.1%})"

    return Signal(
        type=SignalType.MEAN_REVERSION,
        symbol=data.symbol,
        direction=direction,
        estimated_probability=round(estimated_prob, 4),
        market_price=data.price,
        edge=round(edge, 4),
        confidence=round(confidence, 4),
        reason=(
            f"MeanReversion: price={data.price:.2f} {band_desc}, "
            f"BB=[{data.bb_lower:.2f}, {data.bb_upper:.2f}], "
            f"deviation={deviation:.2%}"
        ),
        timestamp=data.timestamp,
    )


def volatility_breakout_signal(data: MarketData, min_edge: float = 0.02) -> Signal | None:
    """Optional: volatility breakout signal.

    Triggers when realized volatility exceeds a threshold with volume confirmation.
    """
    # Threshold: 80% annualized vol is notable for crypto
    if data.volatility < 0.8:
        return None

    if data.volume_ma <= 0:
        return None

    volume_ratio = data.current_volume / data.volume_ma

    # Only trigger on volume expansion
    if volume_ratio < 1.2:
        return None

    # Direction: follow the short-term trend
    direction = Direction.BUY if data.sma_short > data.sma_long else Direction.SELL

    edge = min(data.volatility - 0.8, 0.15)

    return Signal(
        type=SignalType.VOLATILITY_BREAKOUT,
        symbol=data.symbol,
        direction=direction,
        estimated_probability=0.55,
        market_price=data.price,
        edge=round(edge, 4),
        confidence=min(data.volatility * 0.2, 0.85),
        reason=(
            f"VolBreakout: vol={data.volatility:.1%}, "
            f"volume_ratio={volume_ratio:.1f}x, "
            f"direction follows short-term trend"
        ),
        timestamp=data.timestamp,
    )


def generate_all_signals(
    data: MarketData,
    min_edge: float = 0.02,
) -> list[Signal]:
    """Run all signal generators on market data.

    Returns a list of signals sorted by edge (strongest first).
    """
    generators = [
        momentum_signal,
        mean_reversion_signal,
        volatility_breakout_signal,
    ]

    signals: list[Signal] = []
    for gen in generators:
        signal = gen(data, min_edge)
        if signal is not None:
            signals.append(signal)

    # Sort by edge descending
    signals.sort(key=lambda s: s.edge, reverse=True)
    return signals
