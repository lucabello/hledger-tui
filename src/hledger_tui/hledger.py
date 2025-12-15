import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import StringIO
from typing import ClassVar, Final, List, Literal, Optional

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


@dataclass
class Posting:
    """A single posting within a transaction."""

    account: str
    amount: str
    total: str


@dataclass
class Transaction:
    """A transaction with multiple postings."""

    txnidx: str
    date: str
    description: str
    postings: List[Posting]


class HLedgerPeriod:
    """An HLedger period based on a fixed unit (e.g., '1 month ago').

    Args:
        unit: The time unit used in the period, or None for all time
        offset: How many time units in the past (negative ints) or in the future (positive ints)
    """

    unit: str | None
    _offset: int

    def __init__(
        self,
        unit: str | None = "months",
        subdivision: str = "weekly",
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
        if self.unit is None:
            return "all time"
        return self.unit[:-1]

    @property
    def value(self) -> str | None:
        """HLedger-compatible period string, or None for all time."""
        if self.unit is None:
            return None
        direction: Literal["ago", "ahead"] = "ago" if self._offset <= 0 else "ahead"
        # Drop the 's' from the unit if it's 1 - not necessary for HLedger, just for aesthetics
        pretty_unit = self.unit[:-1] if abs(self._offset) <= 1 else self.unit
        if self._offset == 0:
            return f"this {pretty_unit}"
        return f"{abs(self._offset)} {pretty_unit} {direction}"

    def _get_period_date(self) -> str:
        """Calculate the actual date/period this HLedgerPeriod refers to."""
        if self.unit is None:
            return "All Time"

        today = datetime.now()

        if self.unit == "weeks":
            # Calculate the start of the week (Monday)
            days_since_monday = today.weekday()
            start_of_this_week = today - timedelta(days=days_since_monday)
            # Apply offset (negative offset means past, positive means future)
            target_week_start = start_of_this_week + timedelta(weeks=self._offset)
            return target_week_start.strftime("%Y/%m/%d")

        elif self.unit == "months":
            # Calculate target month
            target_month = today.month + self._offset
            target_year = today.year

            # Handle year overflow/underflow
            while target_month > 12:
                target_month -= 12
                target_year += 1
            while target_month < 1:
                target_month += 12
                target_year -= 1

            return f"{target_year:04d}/{target_month:02d}"

        elif self.unit == "quarters":
            # Calculate target quarter
            current_quarter = (today.month - 1) // 3 + 1
            target_quarter = current_quarter + self._offset
            target_year = today.year

            # Handle year overflow/underflow
            while target_quarter > 4:
                target_quarter -= 4
                target_year += 1
            while target_quarter < 1:
                target_quarter += 4
                target_year -= 1

            return f"{target_year:04d}/Q{target_quarter}"

        elif self.unit == "years":
            target_year = today.year + self._offset
            return f"{target_year:04d}"

        return ""

    @property
    def pretty_value(self) -> str:
        """Human-readable period string with actual date/period information."""
        if self.unit is None:
            return "All Time"

        base_value = self.value or ""
        date_info = self._get_period_date()

        if date_info:
            return f"{base_value} ({date_info})"
        return base_value

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
        # Build hledger command arguments
        hledger_args = {
            "depth": self.depth,
            "no_total": True,
            "market": True,  # Unify to one currency for simplicity
            "historical": True,
            "output_format": "csv",
            "daily": self.period.subdivision == "daily",
            "weekly": self.period.subdivision == "weekly",
            "monthly": self.period.subdivision == "monthly",
            "quarterly": self.period.subdivision == "quarterly",
            "yearly": self.period.subdivision == "yearly",
            "_tty_out": False,
        }
        # Only add period if it's not None (all time)
        if self.period.value is not None:
            hledger_args["period"] = self.period.value

        raw_balances = sh.hledger.balance(  # pyright: ignore
            queries or self.queries,
            **hledger_args,
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
        # Build hledger command arguments
        hledger_args = {
            "depth": self.depth,
            "no_total": True,
            "market": True,  # Unify to one currency for simplicity
            "output_format": "csv",
            "_tty_out": False,
        }
        # Only add period if it's not None (all time)
        if self.period.value is not None:
            hledger_args["period"] = self.period.value

        raw_balances = sh.hledger.balance(  # pyright: ignore
            queries or self.queries,
            **hledger_args,
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

    def balance_over_time(
        self, account: str, historical: bool = False, **kwargs
    ) -> List[CategoricalBalance]:
        """Return the result from 'hledger balance', but spread over a time subdivision.

        Args:
            account: The account to query
            historical: If True, shows cumulative historical balance at each point in time.
                       If False, shows balance changes within the period (non-cumulative).
            **kwargs: Additional arguments to pass to hledger balance

        Returns:
            List of CategoricalBalance with time period and balance data

        Example:
            For a yearly period with monthly subdivision:
            - historical=False: monthly balance changes
            - historical=True: cumulative balance at end of each month
        """
        balance_over_time: List[CategoricalBalance] = []
        # Build hledger command arguments
        hledger_args = {
            "depth": self.depth,
            "no_total": True,
            "market": True,  # Unify to one currency for simplicity
            "historical": historical,
            "output_format": "csv",
            "daily": self.period.subdivision == "daily",
            "weekly": self.period.subdivision == "weekly",
            "monthly": self.period.subdivision == "monthly",
            "quarterly": self.period.subdivision == "quarterly",
            "yearly": self.period.subdivision == "yearly",
            "_tty_out": False,
        }
        # Only add period if it's not None (all time)
        if self.period.value is not None:
            hledger_args["period"] = self.period.value

        raw_balances = sh.hledger.balance(  # pyright: ignore
            account,
            **hledger_args,
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

    @staticmethod
    def stats() -> str:
        """Return the output from 'hledger stats'."""
        return sh.hledger.stats(_tty_out=False).strip()  # pyright: ignore

    @staticmethod
    def files() -> List[str]:
        """Return the list of journal files."""
        raw_files: str = sh.hledger.files(_tty_out=False).strip()  # pyright: ignore
        return [f for f in raw_files.split("\n") if f]

    @staticmethod
    def all_accounts() -> List[str]:
        """Return all accounts in the journal."""
        raw_accounts: str = sh.hledger.accounts(_tty_out=False).strip()  # pyright: ignore
        return [a for a in raw_accounts.split("\n") if a]

    @staticmethod
    def commodities() -> List[str]:
        """Return the list of commodities/currencies used."""
        raw_commodities: str = sh.hledger.commodities(_tty_out=False).strip()  # pyright: ignore
        return [c for c in raw_commodities.split("\n") if c]

    # @staticmethod
    # def print() -> str:
    #     return sh.hledger.print(explicit=True, round="soft")  # pyright: ignore

    def register(
        self, account: str, tag: Optional[str] = None, period: Optional[str] = None, **kwargs
    ) -> List[Transaction]:
        """Run 'hledger register' for the given account and optional tag filter.

        Args:
            account: The account to show transactions for
            tag: Optional tag filter in the format "tag:key=value"
            period: Optional specific period to use instead of self.period.
                   Pass empty string "" to explicitly skip period filter.
            **kwargs: Additional arguments to pass to hledger register

        Returns:
            List of Transaction objects with structured data
        """
        # Build hledger command arguments
        hledger_args = {
            "_tty_out": False,
            "market": True,  # Unify to one currency for simplicity
            "output_format": "csv",
        }
        # Use provided period or fallback to self.period
        # period="" means explicitly no period filter
        if period is not None:
            period_to_use = period
        else:
            period_to_use = self.period.value
            
        if period_to_use:  # Only add if not empty string
            hledger_args["period"] = period_to_use

        # Build query list
        queries = [account]
        if tag:
            queries.append(tag)

        raw_register = sh.hledger.register(  # pyright: ignore
            queries,
            **hledger_args,
            **kwargs,
        )
        
        # Parse CSV output into structured data
        return self._parse_register_csv(raw_register)

    @staticmethod
    def _parse_register_csv(csv_data: str) -> List[Transaction]:
        """Parse CSV output from hledger register into Transaction objects.
        
        Args:
            csv_data: Raw CSV string from hledger register
            
        Returns:
            List of Transaction objects, grouped by txnidx
        """
        csv_reader = csv.DictReader(StringIO(csv_data))
        transactions_dict: dict[str, Transaction] = {}
        
        for row in csv_reader:
            txnidx = row["txnidx"]
            
            # Create posting for this row
            posting = Posting(
                account=row["account"],
                amount=row["amount"],
                total=row["total"],
            )
            
            # If transaction doesn't exist yet, create it
            if txnidx not in transactions_dict:
                transactions_dict[txnidx] = Transaction(
                    txnidx=txnidx,
                    date=row["date"],
                    description=row["description"],
                    postings=[],
                )
            
            # Add posting to transaction
            transactions_dict[txnidx].postings.append(posting)
        
        # Return transactions in order
        return list(transactions_dict.values())

    def cycle_depth(self) -> None:
        """Cyclically increase the query depth, wrapping back to 1 after reaching the max."""
        if self.depth + 1 > self.DEFAULT_DEPTH_MAX:
            self.depth = self.DEFAULT_DEPTH_MIN
            return
        self.depth += 1
