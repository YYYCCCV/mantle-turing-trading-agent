"""Mock crypto market data generator.

Produces deterministic, reproducible price series for demo and testing.
No network access required — all data is generated locally.

Each symbol has a deliberately crafted personality:
- BTC-USD: strong uptrend (triggers momentum signals)
- ETH-USD: mean-reverting oscillation (triggers mean reversion signals)
- SOL-USD: sharp deviation + recovery (triggers multiple signal types)
"""

import math
from datetime import datetime, timedelta
from typing import Optional

from ..config import (
    BB_STD_MULTIPLIER,
    MOMENTUM_SHORT_WINDOW,
    MOMENTUM_LONG_WINDOW,
    MEAN_REVERSION_WINDOW,
    VOLUME_EXPANSION_THRESHOLD,
)
from ..types import MarketData, OHLCV


def _generate_price_series(
    symbol: str,
    base_price: float,
    trend: float,
    volatility: float,
    num_bars: int = 60,
    *,
    seed: int = 42,
) -> list[OHLCV]:
    """Generate deterministic OHLCV bars using a sine-trend model.

    Uses a fixed seed for reproducibility — same input always produces same output.
    """
    # Deterministic "randomness" via sine-based pseudo-random
    def pseudo_random(i: int, offset: int = 0) -> float:
        x = (i * 2654435761 + seed * 7 + offset * 13 + symbol_seed(symbol)) % (2 ** 31)
        return (math.sin(x * 0.001) + 1) / 2  # 0..1

    base = datetime(2026, 6, 1, 0, 0, 0)
    bars: list[OHLCV] = []

    for i in range(num_bars):
        t = base + timedelta(hours=i)

        # Trend component: linear drift + sine cycle
        trend_component = trend * i / num_bars + math.sin(i * 0.3) * volatility * 2
        noise = (pseudo_random(i) - 0.5) * volatility * 2

        close = base_price * (1 + trend_component + noise)

        # OHLC structure
        bar_range = close * volatility * 0.5
        high = close + bar_range * pseudo_random(i, 1)
        low = close - bar_range * pseudo_random(i, 2)
        open_price = low + (high - low) * pseudo_random(i, 3)

        # Volume: baseline + spikes on trend days
        volume_base = base_price * 100
        volume = volume_base * (1 + abs(trend_component) * 3 + pseudo_random(i, 4))

        bars.append(OHLCV(
            symbol=symbol,
            timestamp=t,
            open=round(open_price, 2),
            high=round(high, 2),
            low=round(low, 2),
            close=round(close, 2),
            volume=round(volume, 2),
        ))

    return bars


def symbol_seed(symbol: str) -> int:
    """Deterministic seed from symbol name."""
    return sum(ord(c) for c in symbol)


def _compute_sma(prices: list[float], window: int) -> list[float]:
    """Compute simple moving average. Returns same length as input, with NaN for insufficient data."""
    result: list[float] = []
    for i in range(len(prices)):
        if i < window - 1:
            result.append(float("nan"))
        else:
            result.append(sum(prices[i - window + 1 : i + 1]) / window)
    return result


def _compute_bollinger(prices: list[float], window: int, std_mult: float) -> tuple[list[float], list[float], list[float]]:
    """Compute Bollinger Bands. Returns (upper, middle, lower) lists."""
    middle = _compute_sma(prices, window)
    upper: list[float] = []
    lower: list[float] = []

    for i in range(len(prices)):
        if i < window - 1:
            upper.append(float("nan"))
            lower.append(float("nan"))
        else:
            window_prices = prices[i - window + 1 : i + 1]
            mean = sum(window_prices) / window
            variance = sum((p - mean) ** 2 for p in window_prices) / window
            std = math.sqrt(variance)
            upper.append(mean + std_mult * std)
            lower.append(mean - std_mult * std)

    return upper, middle, lower


def _compute_volatility(prices: list[float], window: int) -> list[float]:
    """Compute annualized rolling volatility."""
    result: list[float] = []
    for i in range(len(prices)):
        if i < window:
            result.append(float("nan"))
        else:
            returns = [
                math.log(prices[j] / prices[j - 1])
                for j in range(i - window + 1, i + 1)
            ]
            mean_ret = sum(returns) / len(returns)
            variance = sum((r - mean_ret) ** 2 for r in returns) / len(returns)
            # Annualize (assume hourly bars, 365*24 periods per year)
            result.append(math.sqrt(variance * 365 * 24))
    return result


def generate_market_data(symbol: str) -> MarketData:
    """Generate a complete MarketData snapshot for one symbol.

    The data is deterministic — same symbol always produces the same result.
    """
    # Symbol-specific parameters
    params = {
        "BTC-USD": {"base": 95000.0, "trend": 0.08, "volatility": 0.015},
        "ETH-USD": {"base": 3200.0, "trend": -0.01, "volatility": 0.025},
        "SOL-USD": {"base": 180.0, "trend": 0.02, "volatility": 0.04},
    }
    p = params.get(symbol, {"base": 100.0, "trend": 0.0, "volatility": 0.02})

    bars = _generate_price_series(
        symbol, p["base"], p["trend"], p["volatility"], num_bars=60
    )
    closes = [b.close for b in bars]
    volumes = [b.volume for b in bars]

    # Latest bar
    latest = bars[-1]

    # Compute indicators
    sma_short = _compute_sma(closes, MOMENTUM_SHORT_WINDOW)[-1]
    sma_long = _compute_sma(closes, MOMENTUM_LONG_WINDOW)[-1]
    bb_upper, bb_middle, bb_lower = _compute_bollinger(closes, MEAN_REVERSION_WINDOW, BB_STD_MULTIPLIER)
    volume_ma = _compute_sma(volumes, MEAN_REVERSION_WINDOW)[-1]
    vol_series = _compute_volatility(closes, 20)

    return MarketData(
        symbol=symbol,
        price=latest.close,
        timestamp=latest.timestamp,
        sma_short=round(sma_short, 2) if not math.isnan(sma_short) else 0.0,
        sma_long=round(sma_long, 2) if not math.isnan(sma_long) else 0.0,
        bb_upper=round(bb_upper[-1], 2) if not math.isnan(bb_upper[-1]) else 0.0,
        bb_middle=round(bb_middle[-1], 2) if not math.isnan(bb_middle[-1]) else 0.0,
        bb_lower=round(bb_lower[-1], 2) if not math.isnan(bb_lower[-1]) else 0.0,
        volume_ma=round(volume_ma, 2) if not math.isnan(volume_ma) else 0.0,
        current_volume=latest.volume,
        funding_rate=0.0001 * math.sin(symbol_seed(symbol) * 0.1),
        volatility=round(vol_series[-1], 4) if not math.isnan(vol_series[-1]) else 0.5,
    )


def generate_demo_data(symbols: Optional[list[str]] = None) -> dict[str, MarketData]:
    """Generate market data for all demo symbols.

    Returns a dict mapping symbol -> MarketData snapshot.
    """
    if symbols is None:
        from ..config import DEMO_SYMBOLS
        symbols = DEMO_SYMBOLS

    return {s: generate_market_data(s) for s in symbols}
