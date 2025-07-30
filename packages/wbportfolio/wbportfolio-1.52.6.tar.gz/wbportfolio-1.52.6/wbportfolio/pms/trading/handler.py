from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError

from wbportfolio.pms.typing import Portfolio, Trade, TradeBatch


class TradingService:
    """
    This class represents the trading service. It can be instantiated either with the target portfolio and the effective portfolio or given a direct list of trade
    In any case, it will compute all three states
    """

    def __init__(
        self,
        trade_date: date,
        effective_portfolio: Portfolio | None = None,
        target_portfolio: Portfolio | None = None,
        total_target_weight: Decimal = Decimal("1.0"),
    ):
        self.trade_date = trade_date
        if target_portfolio is None:
            target_portfolio = Portfolio(positions=())
        if effective_portfolio is None:
            effective_portfolio = Portfolio(positions=())
        # If effective portfolio and trades batch is provided, we ensure the trade batch contains at least one trade for every position
        self.trades_batch = self.build_trade_batch(effective_portfolio, target_portfolio).normalize(
            total_target_weight
        )

        self._effective_portfolio = effective_portfolio
        self._target_portfolio = target_portfolio

    @property
    def errors(self) -> list[str]:
        """
        Returned the list of errors stored during the validation process. Can only be called after is_valid
        """
        if not hasattr(self, "_errors"):
            msg = "You must call `.is_valid()` before accessing `.errors`."
            raise AssertionError(msg)
        return self._errors

    @property
    def validated_trades(self) -> list[Trade]:
        """
        Returned the list of validated trade stored during the validation process. Can only be called after is_valid
        """
        if not hasattr(self, "_validated_trades"):
            msg = "You must call `.is_valid()` before accessing `.validated_trades`."
            raise AssertionError(msg)
        return self._validated_trades

    def run_validation(self, validated_trades: list[Trade]):
        """
        Test the given value against all the validators on the field,
        and either raise a `ValidationError` or simply return.
        """
        if self._effective_portfolio:
            for trade in validated_trades:
                if (
                    trade.effective_weight
                    and trade.underlying_instrument not in self._effective_portfolio.positions_map
                ):
                    raise ValidationError("All effective position needs to be matched with a validated trade")

    def build_trade_batch(
        self,
        effective_portfolio: Portfolio,
        target_portfolio: Portfolio,
    ) -> TradeBatch:
        """
        Given combination of effective portfolio and either a trades batch or a target portfolio, ensure all theres variables are set

        Args:
            effective_portfolio: The effective portfolio
            target_portfolio: The optional target portfolio
            trades_batch: The optional trades batch

        Returns: The normalized trades batch
        """
        instruments = effective_portfolio.positions_map.copy()
        instruments.update(target_portfolio.positions_map)

        trades: list[Trade] = []
        for instrument_id, pos in instruments.items():
            if not pos.is_cash:
                effective_weight = target_weight = 0
                effective_shares = 0
                instrument_type = currency = None
                if effective_pos := effective_portfolio.positions_map.get(instrument_id, None):
                    effective_weight = effective_pos.weighting
                    effective_shares = effective_pos.shares
                    instrument_type, currency = effective_pos.instrument_type, effective_pos.currency
                if target_pos := target_portfolio.positions_map.get(instrument_id, None):
                    target_weight = target_pos.weighting
                    instrument_type, currency = target_pos.instrument_type, target_pos.currency

                trades.append(
                    Trade(
                        underlying_instrument=instrument_id,
                        effective_weight=effective_weight,
                        target_weight=target_weight,
                        effective_shares=effective_shares,
                        date=self.trade_date,
                        instrument_type=instrument_type,
                        currency=currency,
                    )
                )
        return TradeBatch(tuple(trades))

    def is_valid(self, ignore_error: bool = False) -> bool:
        """
        Validate the trade batch against a set of default rules. Populate the validated_trades and errors property.
        Ignore error by default
        Args:
            ignore_error: If true, will raise the error. False by default

        Returns: True if the trades batch is valid
        """
        if not hasattr(self, "_validated_trades"):
            self._validated_trades = []
            self._errors = []
            # Run validation for every trade. If a trade is not valid, we simply exclude it from the validated trades list
            for _, trade in self.trades_batch.trades_map.items():
                try:
                    trade.validate()
                    self._validated_trades.append(trade)
                except ValidationError as exc:
                    self._errors.append(exc.message)
            try:
                # Check the overall validity of the trade batch. If this fail, we consider all trade invalids
                self.run_validation(self._validated_trades)
            except ValidationError as exc:
                self._validated_trades = []
                self._errors.append(exc.message)

            if self._errors and not ignore_error:
                raise ValidationError(self.errors)

        return not bool(self._errors)
