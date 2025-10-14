import csv
from dataclasses import dataclass
from io import StringIO
from typing import ClassVar, Dict, Final, List, Literal, Optional, TypeAlias, TypeVar

import sh


@dataclass
class CategoricalBalance:
    """A data point containing a name (e.g., account, time period, etc.) and a numerical balance.

    Note: the balance must include the currency.
    """

    DEFAULT_COMMODITY: ClassVar[str] = "€"

    name: str
    _balance: str

    @property
    def balance(self) -> str:
        if self._balance == "0":
            return f"{self.DEFAULT_COMMODITY} 0"
        return self._balance

    @property
    def commodity(self) -> str:
        """Return the commodity from the given balance."""
        return self.balance.split()[0]

    @property
    def balance_float(self) -> float:
        return float(self.balance.split()[-1])


@dataclass
class HLedgerDepth:
    """An integer counter which is wrapped between min and max."""

    max: int
    value: int = 1
    min: int = 1

    def increment(self):
        if self.value == self.max:
            self.value = self.min - 1
        self.value = self.value % self.max + 1


class HLedgerPeriod:
    """An HLedger period based on a fixed unit (e.g., '1 month ago').

    Args:
        unit: The time unit used in the period
        offset: How many time units in the past (negative ints) or in the future (positive ints)
    """

    # Define period units and subdivisions in order, so that one index identifies
    # one period and its related subdivisions
    PeriodUnit: TypeAlias = Literal["weeks", "months", "quarters", "years"]
    PERIOD_UNITS: Final[List[PeriodUnit]] = ["weeks", "months", "quarters", "years"]
    PeriodSubdivision: TypeAlias = Literal["daily", "weekly", "monthly", "quarterly"]
    PERIOD_SUBDIVISIONS: Final[List[List[PeriodSubdivision]]] = [
        ["daily"],
        ["weekly", "daily"],
        ["weekly", "monthly"],
        ["monthly", "weekly"],
    ]

    _unit: PeriodUnit
    _offset: int

    def __init__(
        self,
        unit: PeriodUnit = "months",
        subdivision: PeriodSubdivision = "weekly",
        offset: int = 0,
    ):
        self._unit = unit
        self._subdivision = subdivision
        self._offset = offset

        self.subdivision_offset: int = 0

    @property
    def _unit_index(self) -> int:
        """Index of self._unit in PERIOD_UNITS."""
        return self.PERIOD_UNITS.index(self._unit)

    @property
    def subdivision(self) -> str:
        """Get the appropriate subdivision for the selected period unit."""
        allowed_subdivisions: List = self.PERIOD_SUBDIVISIONS[self._unit_index]
        return allowed_subdivisions[self.subdivision_offset % len(allowed_subdivisions)]

    @property
    def singular_unit(self) -> str:
        """The current unit used by the HLedgerPeriod, but in singular form."""
        return self._unit[:-1]

    @property
    def value(self) -> str:
        """HLedger-compatible period string."""
        direction: Literal["ago", "ahead"] = "ago" if self._offset <= 0 else "ahead"
        # Drop the 's' from the unit if it's 1 - not necessary for HLedger, just for aesthetics
        pretty_unit = self._unit[:-1] if abs(self._offset) <= 1 else self._unit
        if self._offset == 0:
            return f"this {pretty_unit}"
        return f"{abs(self._offset)} {pretty_unit} {direction}"

    def cycle_unit(self) -> None:
        """Cyclically move to the next period unit."""
        # If the end of the list is reached, cycle back
        if self._unit_index + 1 >= len(self.PERIOD_UNITS):
            self._unit = self.PERIOD_UNITS[0]
            return

        # Otherwise, move to the next time unit
        self._unit = self.PERIOD_UNITS[self._unit_index + 1]

    def previous_period(self):
        """Decrease the period offset by one."""
        self._offset -= 1

    def next_period(self):
        """Increase the period offset by one."""
        self._offset += 1


class HLedger:
    """Interact with HLedger to extract data from a Ledger file."""

    DEFAULT_DEPTH: Final[int] = 2
    DEFAULT_PERIOD: Final[HLedgerPeriod] = HLedgerPeriod()

    queries: List[str]  # Series of HLedger queries
    depth: HLedgerDepth  # The --depth to use in HLedger commands
    period: HLedgerPeriod

    def __init__(self, queries: List[str]):
        self.queries = queries
        self.depth = HLedgerDepth(max=self._account_depth(), value=self.DEFAULT_DEPTH)
        self.period = HLedgerPeriod()

    def balance(self, **kwargs) -> List[CategoricalBalance]:
        """Run 'hledger balance'.

        Returns:

        """
        # Get the balances from HLedger
        balances: List[CategoricalBalance] = []
        raw_balances = sh.hledger.balance(  # pyright: ignore
            self.queries,
            depth=self.depth.value,
            period=self.period.value,
            no_total=True,
            market=True,  # Unify to one currency for simplicity
            output_format="csv",
            _tty_out=False,
            **kwargs,
        )
        csv_reader = csv.reader(StringIO(raw_balances))
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            balances.append(CategoricalBalance(*row))
        return sorted(balances, key=lambda b: b.name)

    def balance_over_time(self, account: str, **kwargs) -> List[CategoricalBalance]:
        """Return the result from 'heldger balance', but spread over a time subdivision.

        For example, if the reference period is 'year', return the monthly balance.
        """
        balance_over_time: List[CategoricalBalance] = []
        raw_balances = sh.hledger.balance(  # pyright: ignore
            account,
            depth=self.depth.value,
            period=self.period.value,
            no_total=True,
            market=True,  # Unify to one currency for simplicity
            output_format="csv",
            daily=self.period.subdivision == "daily",
            weekly=self.period.subdivision == "weekly",
            monthly=self.period.subdivision == "monthly",
            quarterly=self.period.subdivision == "quarterly",
            yearly=self.period.subdivision == "yearly",
            _tty_out=False,
            **kwargs,
        )
        csv_reader = csv.reader(StringIO(raw_balances))
        header_row: bool = True
        buckets: List[str] = []  # Time buckets for each subdivision in the period
        balances: List[str] = []
        for row in csv_reader:
            # Get the subdivision buckets from the header row
            if header_row:
                buckets.extend(row[1:])
                header_row = False
            else:
                balances.extend(row[1:])
        if not balances:
            return balance_over_time

        for i in range(len(buckets)):
            balance_over_time.append(CategoricalBalance(buckets[i], balances[i]))

        # return sorted(balance_over_time, key=lambda b: b.name)
        return balance_over_time

    # @staticmethod
    # def balance_sheet(*, query: str)

    def _account_depth(self) -> int:
        """Return the maximum account depth for the configured query."""
        accounts = sh.hledger.accounts(self.queries)  # pyright: ignore
        max_depth = max(len(account.split(":")) for account in accounts) + 1
        return max_depth

    # @staticmethod
    # def print() -> str:
    #     return sh.hledger.print(explicit=True, round="soft")  # pyright: ignore

    def cycle_depth(self) -> None:
        """Cyclically increase the query depth, wrapping back to 1 after reaching the max."""
        self.depth.increment()
