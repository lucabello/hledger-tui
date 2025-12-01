import csv
from dataclasses import dataclass
from io import StringIO
from typing import ClassVar, Final, List, Literal, Optional, TypeAlias

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
class AccountHistoricalBalance:
    name: str  # Name of the account
    balances: List[CategoricalBalance]  # List of period + balance


class HLedgerPeriod:
    """An HLedger period based on a fixed unit (e.g., '1 month ago').

    Args:
        unit: The time unit used in the period
        offset: How many time units in the past (negative ints) or in the future (positive ints)
    """

    # Define period units and subdivisions in order, so that one index identifies
    # one period and its related subdivisions
    PeriodUnit: TypeAlias = Literal["weeks", "months", "quarters", "years"]
    PeriodSubdivision: TypeAlias = Literal["daily", "weekly", "monthly", "quarterly"]

    unit: PeriodUnit
    _offset: int

    def __init__(
        self,
        unit: PeriodUnit = "months",
        subdivision: PeriodSubdivision = "weekly",
        offset: int = 0,
    ):
        self.unit = unit
        self.subdivision = subdivision
        self._offset = offset

        self.subdivision_offset: int = 0

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, HLedgerPeriod)
            and self.unit == other.unit
            and self._offset == other._offset
        )

    @property
    def singular_unit(self) -> str:
        """The current unit used by the HLedgerPeriod, but in singular form."""
        return self.unit[:-1]

    @property
    def value(self) -> str:
        """HLedger-compatible period string."""
        direction: Literal["ago", "ahead"] = "ago" if self._offset <= 0 else "ahead"
        # Drop the 's' from the unit if it's 1 - not necessary for HLedger, just for aesthetics
        pretty_unit = self.unit[:-1] if abs(self._offset) <= 1 else self.unit
        if self._offset == 0:
            return f"this {pretty_unit}"
        return f"{abs(self._offset)} {pretty_unit} {direction}"

    def previous_period(self):
        """Decrease the period offset by one."""
        self._offset -= 1

    def next_period(self):
        """Increase the period offset by one."""
        self._offset += 1


class HLedger:
    """Interact with HLedger to extract data from a Ledger file."""

    DEFAULT_DEPTH_MIN: Final[int] = 1
    DEFAULT_DEPTH: Final[int] = 2
    DEFAULT_DEPTH_MAX: Final[int] = 4
    DEFAULT_PERIOD: Final[HLedgerPeriod] = HLedgerPeriod()
    DEFAULT_HLEDGER_QUERIES: ClassVar[List[str]] = [
        "acct:expenses",
        "not:acct:financial",
        "not:acct:home:rent",
        "not:acct:home:utilities",
    ]
    DEFAULT_HLEDGER_TAG_QUERIES: ClassVar[List[str]] = [
        "acct:expenses",
    ]
    DEFAULT_HLEDGER_ASSETS_QUERIES: ClassVar[List[str]] = [
        "acct:assets",
        "acct:liabilities",
        "acct:budget",
    ]

    queries: List[str]  # Series of HLedger queries
    depth: int  # The --depth to use in HLedger commands
    period: HLedgerPeriod

    def __init__(self, queries: Optional[List[str]] = None):
        self.queries = queries if queries is not None else self.DEFAULT_HLEDGER_QUERIES
        self.depth = self.DEFAULT_DEPTH
        self.period = HLedgerPeriod()

    def assets(
        self, queries: Optional[List[str]] = None, **kwargs
    ) -> List[AccountHistoricalBalance]:
        raw_balances = sh.hledger.balance(  # pyright: ignore
            queries or self.queries,
            depth=self.depth,
            period=self.period.value,
            no_total=True,
            market=True,  # Unify to one currency for simplicity
            historical=True,
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
        # Process the header row
        header_row: bool = True
        periods: List[str] = []
        balances: List[AccountHistoricalBalance] = []
        for row in csv_reader:
            # Get the subdivision buckets from the header row
            if header_row:
                periods.extend(row[1:])
                header_row = False
            else:
                balances.append(
                    AccountHistoricalBalance(
                        name=row[0],
                        balances=[
                            CategoricalBalance(
                                p,
                                row[1 + index],
                            )
                            for index, p in enumerate(periods)
                        ],
                    )
                )

        return sorted(balances, key=lambda b: b.name)

    def balance(self, queries: Optional[List[str]] = None, **kwargs) -> List[CategoricalBalance]:
        """Run 'hledger balance'.

        Returns:

        """
        # Get the balances from HLedger
        balances: List[CategoricalBalance] = []
        raw_balances = sh.hledger.balance(  # pyright: ignore
            queries or self.queries,
            depth=self.depth,
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

    def tag_balance(self, tag: str, **kwargs) -> List[CategoricalBalance]:
        """Run 'hledger balance'.

        Returns:

        """
        # Get the balances from HLedger
        balances: List[CategoricalBalance] = []
        raw_balances = sh.hledger.balance(  # pyright: ignore
            [*self.DEFAULT_HLEDGER_TAG_QUERIES, tag],
            depth=self.depth,
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
            depth=self.depth,
            period=self.period.value,
            no_total=True,
            market=True,  # Unify to one currency for simplicity
            historical=True,
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

    def _account_depth(self) -> int:
        """Return the maximum account depth for the configured query."""
        accounts = sh.hledger.accounts(self.queries).split("\n")  # pyright: ignore
        max_depth = max(len(account.split(":")) for account in accounts) + 1
        print(max_depth)
        return max_depth

    @staticmethod
    def accounts_depth(accounts: List[str]) -> int:
        """Return the maximum account depth using the given accounts as query."""
        raw_accounts = sh.hledger.accounts(accounts).split("\n")  # pyright: ignore
        max_depth = max(len(acc.split(":")) for acc in raw_accounts) + 1
        return max_depth

    @staticmethod
    def tags() -> List[str]:
        """Return the existing HLedger tags."""
        raw_tags: List[str] = sh.hledger.tags(declared=True).split("\n")  # pyright: ignore
        tags = [t for t in raw_tags if t]
        return tags

    # @staticmethod
    # def print() -> str:
    #     return sh.hledger.print(explicit=True, round="soft")  # pyright: ignore

    def cycle_depth(self) -> None:
        """Cyclically increase the query depth, wrapping back to 1 after reaching the max."""
        if self.depth + 1 > self.DEFAULT_DEPTH_MAX:
            self.depth = self.DEFAULT_DEPTH_MIN
            return
        self.depth += 1
