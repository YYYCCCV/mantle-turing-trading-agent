"""Configuration for the Mantle Alpha Trading Agent.

Loads config from environment variables with sensible defaults.
No live trading keys required for MVP.
"""

import os
from .types import RiskParams


def load_risk_params() -> RiskParams:
    """Load risk parameters from environment or defaults."""
    return RiskParams(
        max_trade_amount=float(os.getenv("MAX_TRADE_AMOUNT", "1000")),
        min_edge_threshold=float(os.getenv("MIN_EDGE_THRESHOLD", "0.02")),
        min_confidence_threshold=float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.3")),
        max_exposure_per_symbol=float(os.getenv("MAX_EXPOSURE_PER_SYMBOL", "5000")),
        kelly_fraction=float(os.getenv("KELLY_FRACTION", "0.25")),
        dry_run=os.getenv("DRY_RUN", "true").lower() != "false",
    )


# Strategy parameters
MOMENTUM_SHORT_WINDOW: int = 10
MOMENTUM_LONG_WINDOW: int = 30
MEAN_REVERSION_WINDOW: int = 20
BB_STD_MULTIPLIER: float = 2.0
VOLUME_EXPANSION_THRESHOLD: float = 1.5
VOLATILITY_WINDOW: int = 20

# Demo symbols
DEMO_SYMBOLS: list[str] = ["BTC-USD", "ETH-USD", "SOL-USD"]
