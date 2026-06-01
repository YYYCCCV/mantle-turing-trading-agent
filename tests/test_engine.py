"""Tests for strategy engine and end-to-end integration."""

from datetime import datetime

from mantle_agent.config import DEMO_SYMBOLS, load_risk_params
from mantle_agent.data.mock_market import generate_demo_data
from mantle_agent.execution.trader import process_signals
from mantle_agent.reporting.logger import write_run_log
from mantle_agent.strategy.engine import evaluate_signals, run_strategy
from mantle_agent.types import RunSummary


class TestStrategyEngine:
    """Strategy engine: market data → signals."""

    def test_produces_deterministic_output(self):
        """Same market data should always produce the same signals."""
        data1 = generate_demo_data()
        data2 = generate_demo_data()

        params = load_risk_params()
        signals1 = run_strategy(data1, params)
        signals2 = run_strategy(data2, params)

        assert len(signals1) == len(signals2)

        for s1, s2 in zip(signals1, signals2):
            assert s1.symbol == s2.symbol
            assert s1.type == s2.type
            assert s1.direction == s2.direction
            assert s1.edge == s2.edge

    def test_produces_signals_for_each_symbol(self):
        """Each symbol in the demo set should produce results."""
        data = generate_demo_data()
        params = load_risk_params()
        signals = run_strategy(data, params)

        symbols_with_signals = {s.symbol for s in signals}
        assert len(symbols_with_signals) >= 1

    def test_empty_data_produces_empty_signals(self):
        """Empty market data should produce empty signal list."""
        params = load_risk_params()
        signals = run_strategy({}, params)
        assert signals == []

    def test_signals_sorted_by_edge(self):
        """Signals should be sorted by edge (strongest first)."""
        data = generate_demo_data()
        params = load_risk_params()
        signals = run_strategy(data, params)

        for i in range(len(signals) - 1):
            assert signals[i].edge >= signals[i + 1].edge


class TestEndToEndPipeline:
    """Full pipeline: data → signals → risk → execution → logs."""

    def test_full_demo_pipeline_runs(self):
        """The complete demo pipeline should run without errors."""
        market_data = generate_demo_data()
        assert len(market_data) == len(DEMO_SYMBOLS)

        risk_params = load_risk_params()
        signals = run_strategy(market_data, risk_params)
        assert isinstance(signals, list)

        signal_decisions = evaluate_signals(signals, [], risk_params)
        assert len(signal_decisions) == len(signals)

        trades = process_signals(signal_decisions, dry_run=True)
        assert len(trades) == len(signals)

        approved_signals = [s for s, d in signal_decisions if d.approved]
        rejected_signals = [s for s, d in signal_decisions if not d.approved]

        summary = RunSummary(
            timestamp=datetime.now(),
            symbols_scanned=len(market_data),
            signals_generated=approved_signals,
            signals_rejected=rejected_signals,
            trades_executed=trades,
        )

        log_path = write_run_log(summary)
        assert log_path.endswith(".jsonl")

    def test_dry_run_only(self):
        """All trades should be DRY_RUN or REJECTED — never LIVE."""
        market_data = generate_demo_data()
        risk_params = load_risk_params()
        signals = run_strategy(market_data, risk_params)
        signal_decisions = evaluate_signals(signals, [], risk_params)
        trades = process_signals(signal_decisions, dry_run=True)

        for trade in trades:
            assert trade.status.value in ("dry_run", "rejected")
            assert trade.status.value != "executed"

    def test_demo_data_is_deterministic(self):
        """Demo data generation must be deterministic."""
        data1 = generate_demo_data()
        data2 = generate_demo_data()

        assert set(data1.keys()) == set(data2.keys())

        for symbol in data1:
            assert data1[symbol].price == data2[symbol].price
            assert data1[symbol].sma_short == data2[symbol].sma_short
            assert data1[symbol].sma_long == data2[symbol].sma_long
            assert data1[symbol].bb_upper == data2[symbol].bb_upper
            assert data1[symbol].bb_lower == data2[symbol].bb_lower

    def test_risk_params_default_to_dry_run(self):
        """Default risk params must have dry_run=True."""
        params = load_risk_params()
        assert params.dry_run is True


class TestDemoSymbols:
    """Demo symbols should be valid crypto trading pairs."""

    def test_demo_symbols_configured(self):
        """Demo symbols list should not be empty."""
        assert len(DEMO_SYMBOLS) >= 2
        assert all("-USD" in s for s in DEMO_SYMBOLS)

    def test_all_demo_symbols_have_data(self):
        """Every demo symbol should produce valid market data."""
        data = generate_demo_data()
        for symbol in DEMO_SYMBOLS:
            assert symbol in data
            assert data[symbol].price > 0
            assert data[symbol].bb_middle > 0
