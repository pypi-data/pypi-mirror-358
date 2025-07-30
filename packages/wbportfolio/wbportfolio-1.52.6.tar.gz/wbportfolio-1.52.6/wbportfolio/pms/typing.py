from dataclasses import asdict, dataclass, field, fields
from datetime import date as date_lib
from decimal import Decimal

import pandas as pd
from django.core.exceptions import ValidationError


@dataclass(frozen=True)
class Valuation:
    instrument: int
    net_value: Decimal
    outstanding_shares: Decimal = Decimal(0)


@dataclass(frozen=True)
class Position:
    underlying_instrument: int
    weighting: Decimal
    date: date_lib

    currency: int | None = None
    instrument_type: int | None = None
    asset_valuation_date: date_lib | None = None
    portfolio_created: int = None
    exchange: int = None
    is_estimated: bool = False
    country: int = None
    shares: Decimal | None = None
    is_cash: bool = False
    primary_classification: int = None
    favorite_classification: int = None
    market_capitalization_usd: float = None
    currency_fx_rate: float = 1
    market_share: float = None
    daily_liquidity: float = None
    volume_usd: float = None
    price: float = None

    def __add__(self, other):
        return Position(
            weighting=self.weighting + other.weighting,
            shares=self.shares + other.shares if (self.shares is not None and other.shares is not None) else None,
            **{f.name: getattr(self, f.name) for f in fields(Position) if f.name not in ["weighting", "shares"]},
        )


@dataclass(frozen=True)
class Portfolio:
    positions: tuple[Position] | tuple
    positions_map: dict[int, Position] = field(init=False, repr=False)

    def __post_init__(self):
        positions_map = {}
        for pos in self.positions:
            if pos.underlying_instrument in positions_map:
                positions_map[pos.underlying_instrument] += pos
            else:
                positions_map[pos.underlying_instrument] = pos
        object.__setattr__(self, "positions_map", positions_map)

    @property
    def total_weight(self):
        return round(sum([pos.weighting for pos in self.positions]), 6)

    @property
    def total_shares(self):
        return sum([pos.target_shares for pos in self.positions if pos.target_shares is not None])

    def to_df(self):
        return pd.DataFrame([asdict(pos) for pos in self.positions])

    def to_dict(self) -> dict[int, Decimal]:
        return {underlying_instrument: pos.weighting for underlying_instrument, pos in self.positions_map.items()}

    def __len__(self):
        return len(self.positions)


@dataclass(frozen=True)
class Trade:
    underlying_instrument: int
    instrument_type: int
    currency: int
    date: date_lib

    effective_weight: Decimal
    target_weight: Decimal
    id: int | None = None
    effective_shares: Decimal = None
    is_cash: bool = False

    def __add__(self, other):
        return Trade(
            underlying_instrument=self.underlying_instrument,
            effective_weight=self.effective_weight + other.effective_weight,
            target_weight=self.target_weight + other.target_weight,
            effective_shares=self.effective_shares + other.effective_shares
            if (self.effective_shares is not None and other.effective_shares is not None)
            else None,
            **{
                f.name: getattr(self, f.name)
                for f in fields(Trade)
                if f.name
                not in [
                    "effective_weight",
                    "target_weight",
                    "effective_shares",
                    "underlying_instrument",
                ]
            },
        )

    @property
    def delta_weight(self) -> Decimal:
        return self.target_weight - self.effective_weight

    def validate(self):
        return True
        # if self.effective_weight < 0 or self.effective_weight > 1.0:
        #     raise ValidationError("Effective Weight needs to be in range [0, 1]")
        # if self.target_weight < 0 or self.target_weight > 1.0:
        #     raise ValidationError("Target Weight needs to be in range [0, 1]")

    def normalize_target(self, factor: Decimal):
        t = Trade(
            target_weight=self.target_weight * factor,
            **{f.name: getattr(self, f.name) for f in fields(Trade) if f.name not in ["target_weight"]},
        )
        return t


@dataclass(frozen=True)
class TradeBatch:
    trades: tuple[Trade]
    trades_map: dict[Trade] = field(init=False, repr=False)

    def __post_init__(self):
        trade_map = {}
        for trade in self.trades:
            if trade.underlying_instrument in trade_map:
                trade_map[trade.underlying_instrument] += trade
            else:
                trade_map[trade.underlying_instrument] = trade
        object.__setattr__(self, "trades_map", trade_map)

    @property
    def total_target_weight(self) -> Decimal:
        return round(sum([trade.target_weight for trade in self.trades], Decimal("0")), 6)

    @property
    def total_effective_weight(self) -> Decimal:
        return round(sum([trade.effective_weight for trade in self.trades], Decimal("0")), 6)

    @property
    def total_abs_delta_weight(self) -> Decimal:
        return sum([abs(trade.delta_weight) for trade in self.trades], Decimal("0"))

    def __add__(self, other):
        return TradeBatch(tuple(self.trades + other.trades))

    def __len__(self):
        return len(self.trades)

    def validate(self):
        if round(float(self.total_target_weight), 4) != 1:  # we do that to remove decimal over precision
            raise ValidationError(f"Total Weight cannot be different than 1 ({float(self.total_target_weight)})")

    def convert_to_portfolio(self, *extra_positions):
        positions = []
        for instrument, trade in self.trades_map.items():
            positions.append(
                Position(
                    underlying_instrument=trade.underlying_instrument,
                    instrument_type=trade.instrument_type,
                    weighting=trade.target_weight,
                    currency=trade.currency,
                    date=trade.date,
                    is_cash=trade.is_cash,
                )
            )
        for position in extra_positions:
            if position.weighting:
                positions.append(position)
        return Portfolio(tuple(positions))

    def normalize(self, total_target_weight: Decimal = Decimal("1.0")):
        """
        Normalize the instantiate trades batch so that the target weight is 100%
        """
        normalization_factor = (
            total_target_weight / self.total_target_weight if self.total_target_weight else Decimal("0.0")
        )
        normalized_trades = []
        for trade in self.trades:
            normalized_trades.append(trade.normalize_target(normalization_factor))
        tb = TradeBatch(normalized_trades)
        return tb
