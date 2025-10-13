import csv
from dataclasses import dataclass
from io import StringIO
from typing import List, Literal, Optional

import sh


@dataclass
class CyclicCounter:
    """An integer counter which is wrapped between min and max."""

    max: int
    value: int = 1
    min: int = 1

    def increment(self):
        if self.value == self.max:
            self.value = self.min - 1
        self.value = self.value % self.max + 1


@dataclass
class HLedgerPeriod:
    """An HLedger period based on a fixed unit (e.g., '1 month ago').

    Args:
        unit: The time unit used in the period
        offset: How many time units in the past (negative ints) or in the future (positive ints)
    """

    @dataclass
    class CyclicString:
        """Cycle through a list of strings with an internal counter."""

        strings: List[str]
        index: int = 0

        def next(self):
            self.index = (self.index + 1) % len(self.strings)

        @property
        def value(self):
            return self.strings[self.index]

    unit: CyclicString = CyclicString(  # Default to 'months'
        strings=["weeks", "months", "quarters", "years"], index=1
    )
    offset: int = -1  # Default to '1 unit ago'

    def before(self):
        self.offset -= 1

    def after(self):
        self.offset += 1

    def to_string(self) -> str:
        direction: Literal["ago", "ahead"] = "ago" if self.offset <= 0 else "ahead"
        # Drop the 's' from the unit if it's 1 - not necessary for HLedger, just for aesthetics
        pretty_unit = self.unit.value[:-1] if abs(self.offset) <= 1 else self.unit.value
        if self.offset == 0:
            return f"this {pretty_unit}"
        return f"{abs(self.offset)} {pretty_unit} {direction}"


@dataclass
class AccountBalance:
    account: str
    balance: str

    @property
    def commodity(self) -> str:
        """Return the commodity from the given balance."""
        return self.balance.split()[0]

    @property
    def balance_float(self) -> float:
        return float(self.balance.split()[-1])


class HLedgerApi:
    """Interact with HLedger to extract data from a Ledger file."""

    @staticmethod
    def balance(
        *, queries: List[str], depth: int, period: HLedgerPeriod, **kwargs
    ) -> List[AccountBalance]:
        # Get the balances from HLedger
        balances: List[AccountBalance] = []
        raw_balances = sh.hledger.balance(  # pyright: ignore
            queries,
            depth=depth,
            period=period.to_string(),
            no_total=True,
            market=True,  # Unify to one currency for simplicity
            output_format="csv",
            **kwargs,
        )
        csv_reader = csv.reader(StringIO(raw_balances))
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            balances.append(AccountBalance(*row))
        return sorted(balances, key=lambda b: b.account)

    # @staticmethod
    # def balance_sheet(*, query: str)

    @staticmethod
    def account_depth(account_query: Optional[str]) -> CyclicCounter:
        """Return the maximum account depth."""
        accounts = sh.hledger.accounts(account_query)  # pyright: ignore
        max_depth = max(len(account.split(":")) for account in accounts) + 1
        return CyclicCounter(max=max_depth, value=2)

    @staticmethod
    def print() -> str:
        return sh.hledger.print(explicit=True, round="soft")  # pyright: ignore
