"""Service layer for HLedger operations with backend abstraction."""

import csv
import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from io import StringIO
from typing import ClassVar, Final, List, Optional

import sh

from hledger_tui.config import config
from hledger_tui.core.models import (
    AccountHistoricalBalance,
    CategoricalBalance,
    Posting,
    Transaction,
)
from hledger_tui.core.period import HLedgerPeriod


class HLedgerBackend(ABC):
    """Abstract interface for HLedger command execution.

    Enables multiple implementations: shell commands, API calls, or mocks for testing.
    """

    @abstractmethod
    def balance(self, queries: List[str], **kwargs) -> str:
        """Execute 'hledger balance' and return raw output."""
        pass

    @abstractmethod
    def register(self, queries: List[str], **kwargs) -> str:
        """Execute 'hledger register' and return raw output."""
        pass

    @abstractmethod
    def stats(self) -> str:
        """Execute 'hledger stats' and return raw output."""
        pass

    @abstractmethod
    def files(self) -> str:
        """Execute 'hledger files' and return raw output."""
        pass

    @abstractmethod
    def accounts(self, queries: List[str]) -> str:
        """Execute 'hledger accounts' and return raw output."""
        pass

    @abstractmethod
    def tags(self, **kwargs) -> str:
        """Execute 'hledger tags' and return raw output."""
        pass

    @abstractmethod
    def commodities(self, **kwargs) -> str:
        """Execute 'hledger commodities' and return raw output."""
        pass


class ShellHLedgerBackend(HLedgerBackend):
    """HLedger backend implementation using shell command execution via sh library."""

    def balance(self, queries: List[str], **kwargs) -> str:
        return sh.hledger.balance(queries, **kwargs)  # pyright: ignore

    def register(self, queries: List[str], **kwargs) -> str:
        return sh.hledger.register(queries, **kwargs)  # pyright: ignore

    def stats(self) -> str:
        return sh.hledger.stats(_tty_out=False).strip()  # pyright: ignore

    def files(self) -> str:
        return sh.hledger.files(_tty_out=False).strip()  # pyright: ignore

    def accounts(self, queries: List[str]) -> str:
        return sh.hledger.accounts(queries)  # pyright: ignore

    def tags(self, **kwargs) -> str:
        return sh.hledger.tags(**kwargs)  # pyright: ignore

    def commodities(self, **kwargs) -> str:
        return sh.hledger.commodities(_tty_out=False, **kwargs).strip()  # pyright: ignore


class HLedger:
    """High-level service for querying and parsing HLedger data.

    Provides methods to extract balances, transactions, accounts, and statistics
    with support for periods, depth filtering, and multiple query types.
    """

    DEFAULT_DEPTH_MIN: Final[int] = 1
    DEFAULT_DEPTH: Final[int] = config.depth
    DEFAULT_DEPTH_MAX: Final[int] = 4
    DEFAULT_PERIOD: Final[HLedgerPeriod] = HLedgerPeriod()
    DEFAULT_HLEDGER_QUERIES: ClassVar[List[str]] = config.queries.expenses
    DEFAULT_HLEDGER_TAG_QUERIES: ClassVar[List[str]] = config.queries.tags
    DEFAULT_HLEDGER_ASSETS_QUERIES: ClassVar[List[str]] = config.queries.assets

    queries: List[str]  # Series of HLedger queries
    depth: int  # The --depth to use in HLedger commands
    period: HLedgerPeriod
    backend: HLedgerBackend

    def __init__(
        self,
        queries: Optional[List[str]] = None,
        backend: Optional[HLedgerBackend] = None,
    ):
        """Initialize HLedger service.

        Args:
            queries: List of HLedger query strings. Defaults to DEFAULT_HLEDGER_QUERIES.
            backend: Backend implementation for executing HLedger commands.
                    Defaults to ShellHLedgerBackend.
        """
        self.queries = queries if queries is not None else self.DEFAULT_HLEDGER_QUERIES
        self.depth = self.DEFAULT_DEPTH
        self.period = HLedgerPeriod()
        self.backend = backend or ShellHLedgerBackend()
        self._declared_commodities: Optional[List[str]] = None

    @staticmethod
    def _parse_extra_options(options: List[str]) -> dict:
        """Parse extra command-line options into sh library kwargs format.

        Converts command-line style arguments like '--cost' or '--depth 3' into
        keyword arguments compatible with the sh library. Follows sh conventions:
        - Replace dashes with underscores: '--no-total' becomes 'no_total'
        - Boolean flags (no value): set to True
        - Key-value pairs: extract value

        Supports multiple input formats:
        - Separate elements: ['--depth', '3']
        - Combined with equals: ['--depth=3']
        - Combined with space: ['--depth 3']

        Args:
            options: List of command-line arguments (e.g., ['--cost', '--depth', '3'])

        Returns:
            Dictionary of keyword arguments for sh library

        Examples:
            ['--cost'] -> {'cost': True}
            ['--depth', '3'] -> {'depth': '3'}
            ['--depth=3'] -> {'depth': '3'}
            ['--depth 3'] -> {'depth': '3'}
            ['--no-total'] -> {'no_total': True}
        """
        kwargs = {}
        i = 0
        while i < len(options):
            arg = options[i]

            # Handle options starting with -- or -
            if arg.startswith("--") or arg.startswith("-"):
                # Check if the option contains an equals sign (e.g., --depth=5)
                if "=" in arg:
                    prefix_len = 2 if arg.startswith("--") else 1
                    key_value = arg[prefix_len:]
                    key, value = key_value.split("=", 1)
                    key = key.replace("-", "_")
                    kwargs[key] = value
                    i += 1
                # Check if the option contains a space (e.g., "--depth 5" as single string)
                elif " " in arg:
                    prefix_len = 2 if arg.startswith("--") else 1
                    key_value = arg[prefix_len:]
                    parts = key_value.split(" ", 1)
                    key = parts[0].replace("-", "_")
                    value = parts[1] if len(parts) > 1 else True
                    kwargs[key] = value
                    i += 1
                else:
                    # Standard format: option possibly followed by value in next element
                    prefix_len = 2 if arg.startswith("--") else 1
                    key = arg[prefix_len:].replace("-", "_")

                    # Check if next item is a value (doesn't start with - or --)
                    if i + 1 < len(options) and not options[i + 1].startswith("-"):
                        kwargs[key] = options[i + 1]
                        i += 2
                    else:
                        # Boolean flag
                        kwargs[key] = True
                        i += 1
            else:
                # Skip non-option arguments
                i += 1
        return kwargs

    def _get_currency_conversion_kwargs(self) -> dict:
        """Get currency conversion kwargs based on HLEDGER_TUI_COMMODITY setting.

        Returns:
            Dictionary with either 'market': True (if commodity empty)
            or 'exchange': commodity_value (if commodity set and valid)

        Raises:
            ValueError: If configured commodity is not declared in journal
        """
        commodity = config.commodity
        if not commodity:
            # Use market conversion when no commodity specified
            return {"market": True}

        # Validate commodity is declared in journal
        if self._declared_commodities is None:
            raw_commodities = self.backend.commodities(declared=True)
            self._declared_commodities = [
                c.strip() for c in raw_commodities.split("\n") if c.strip()
            ]

        if commodity not in self._declared_commodities:
            raise ValueError(
                f"Commodity '{commodity}' not declared in journal. "
                f"Available commodities: {', '.join(self._declared_commodities)}"
            )

        return {"exchange": commodity}

    def assets(
        self, queries: Optional[List[str]] = None, **kwargs
    ) -> List[AccountHistoricalBalance]:
        """Get historical balance data for assets/liabilities accounts.

        Args:
            queries: Optional list of query filters. Uses self.queries if not provided.
            **kwargs: Additional arguments passed to the backend.

        Returns:
            List of AccountHistoricalBalance objects with time-series data.
        """
        # Build hledger command arguments
        hledger_args = {
            "depth": self.depth,
            "no_total": True,
            "historical": True,
            "output_format": "csv",
            "daily": self.period.subdivision == "daily",
            "weekly": self.period.subdivision == "weekly",
            "monthly": self.period.subdivision == "monthly",
            "quarterly": self.period.subdivision == "quarterly",
            "yearly": self.period.subdivision == "yearly",
            "_tty_out": False,
            **self._get_currency_conversion_kwargs(),
        }
        # Only add period if it's not None (all time)
        if self.period.value is not None:
            hledger_args["period"] = self.period.value

        # Apply extra options (these can override defaults per "last wins" behavior)
        extra_kwargs = self._parse_extra_options(config.extra_options.balance)
        hledger_args.update(extra_kwargs)

        raw_balances = self.backend.balance(queries or self.queries, **hledger_args, **kwargs)
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
        """Get current balance for accounts.

        Args:
            queries: Optional list of query filters. Uses self.queries if not provided.
            **kwargs: Additional arguments passed to the backend.

        Returns:
            List of CategoricalBalance objects with current balance data.
        """
        # Get the balances from HLedger
        balances: List[CategoricalBalance] = []
        # Build hledger command arguments
        hledger_args = {
            "depth": self.depth,
            "no_total": True,
            "output_format": "csv",
            "_tty_out": False,
            **self._get_currency_conversion_kwargs(),
        }
        # Only add period if it's not None (all time)
        if self.period.value is not None:
            hledger_args["period"] = self.period.value

        # Apply extra options (these can override defaults per "last wins" behavior)
        extra_kwargs = self._parse_extra_options(config.extra_options.balance)
        hledger_args.update(extra_kwargs)

        raw_balances = self.backend.balance(queries or self.queries, **hledger_args, **kwargs)
        csv_reader = csv.reader(StringIO(raw_balances))
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            balances.append(CategoricalBalance(*row))
        return sorted(balances, key=lambda b: b.name)

    def tag_balance(self, tag: str, **kwargs) -> List[CategoricalBalance]:
        """Get balance data filtered by tag.

        Args:
            tag: Tag filter string (e.g., "tag:project=myproject")
            **kwargs: Additional arguments passed to the backend.

        Returns:
            List of CategoricalBalance objects for the tag filter.
        """
        balances: List[CategoricalBalance] = []
        # Build hledger command arguments
        hledger_args = {
            "depth": self.depth,
            "no_total": True,
            "output_format": "csv",
            "_tty_out": False,
            **self._get_currency_conversion_kwargs(),
        }
        # Apply extra options (these can override defaults per "last wins" behavior)
        extra_kwargs = self._parse_extra_options(config.extra_options.balance)
        hledger_args.update(extra_kwargs)

        raw_balances = self.backend.balance(
            [*self.DEFAULT_HLEDGER_TAG_QUERIES, tag],
            **hledger_args,
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
        """Get balance data for an account spread over time subdivisions.

        Args:
            account: The account to query
            historical: If True, shows cumulative historical balance at each point in time.
                       If False, shows balance changes within the period (non-cumulative).
            **kwargs: Additional arguments passed to the backend.

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
            "historical": historical,
            "output_format": "csv",
            "daily": self.period.subdivision == "daily",
            "weekly": self.period.subdivision == "weekly",
            "monthly": self.period.subdivision == "monthly",
            "quarterly": self.period.subdivision == "quarterly",
            "yearly": self.period.subdivision == "yearly",
            "_tty_out": False,
            **self._get_currency_conversion_kwargs(),
        }
        # Only add period if it's not None (all time)
        if self.period.value is not None:
            hledger_args["period"] = self.period.value

        # Apply extra options (these can override defaults per "last wins" behavior)
        extra_kwargs = self._parse_extra_options(config.extra_options.balance)
        hledger_args.update(extra_kwargs)

        raw_balances = self.backend.balance([account], **hledger_args, **kwargs)
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

        return balance_over_time

    def _account_depth(self) -> int:
        """Calculate maximum account depth from current query results."""
        accounts = self.backend.accounts(self.queries).split("\n")
        max_depth = max(len(account.split(":")) for account in accounts) + 1
        return max_depth

    @staticmethod
    def accounts_depth(accounts: List[str]) -> int:
        """Calculate maximum account depth for specified account queries."""
        backend = ShellHLedgerBackend()
        raw_accounts = backend.accounts(accounts).split("\n")
        max_depth = max(len(acc.split(":")) for acc in raw_accounts) + 1
        return max_depth

    @staticmethod
    def tags() -> List[str]:
        """Get all declared tags from HLedger journal."""
        backend = ShellHLedgerBackend()
        raw_tags: List[str] = backend.tags(declared=True).split("\n")
        tags = [t for t in raw_tags if t]
        return tags

    @staticmethod
    def stats() -> str:
        """Get statistics output from 'hledger stats' command."""
        backend = ShellHLedgerBackend()
        return backend.stats()

    @staticmethod
    def files() -> List[str]:
        """Get list of journal files used by HLedger."""
        backend = ShellHLedgerBackend()
        raw_files: str = backend.files()
        return [f for f in raw_files.split("\n") if f]

    @staticmethod
    def all_accounts() -> List[str]:
        """Get all account names from HLedger journal."""
        backend = ShellHLedgerBackend()
        raw_accounts: str = backend.accounts([]).strip()
        return [a for a in raw_accounts.split("\n") if a]

    @staticmethod
    def commodities(declared: bool = False) -> List[str]:
        """Get list of commodities/currencies used in journal.

        Args:
            declared: If True, only show commodities declared with 'commodity' directive

        Returns:
            List of commodity symbols/codes
        """
        backend = ShellHLedgerBackend()
        kwargs = {"declared": True} if declared else {}
        raw_commodities: str = backend.commodities(**kwargs)
        return [c for c in raw_commodities.split("\n") if c]

    def register(
        self, account: str, tag: Optional[str] = None, period: Optional[str] = None, **kwargs
    ) -> List[Transaction]:
        """Run 'hledger register' for the given account and optional tag filter.

        Args:
            account: The account to show transactions for
            tag: Optional tag filter in the format "tag:key=value"
            period: Optional specific period to use instead of self.period.
                   Pass empty string "" to explicitly skip period filter.
            **kwargs: Additional arguments passed to the backend.

        Returns:
            List of Transaction objects with structured data
        """
        # Build hledger command arguments
        hledger_args = {
            "_tty_out": False,
            "output_format": "csv",
            **self._get_currency_conversion_kwargs(),
        }
        # Use provided period or fallback to self.period
        # period="" means explicitly no period filter
        if period is not None:
            period_to_use = period
        else:
            period_to_use = self.period.value

        if period_to_use:  # Only add if not empty string
            # Convert ISO week format (YYYY-WNN) to date range if needed
            period_to_use = self._convert_week_period(period_to_use)
            hledger_args["period"] = period_to_use

        # Apply extra options (these can override defaults per "last wins" behavior)
        extra_kwargs = self._parse_extra_options(config.extra_options.register)
        hledger_args.update(extra_kwargs)

        # Build query list
        queries = [account]
        if tag:
            queries.append(tag)

        raw_register = self.backend.register(queries, **hledger_args, **kwargs)

        # Parse CSV output into structured data
        return self._parse_register_csv(raw_register)

    @staticmethod
    def _convert_week_period(period: str) -> str:
        """Convert ISO week format (YYYY-WNN) to date range format.

        Args:
            period: Period string, possibly in ISO week format (e.g., "2024-W04")

        Returns:
            Converted period string, or original if not in week format
        """
        # Check if period matches ISO week format (YYYY-WNN)
        week_match = re.match(r"^(\d{4})-W(\d{2})$", period)
        if not week_match:
            return period

        year = int(week_match.group(1))
        week = int(week_match.group(2))

        # Parse the Monday of that ISO week
        # %G is ISO year, %V is ISO week number, %u is day of week (1=Monday)
        monday = datetime.strptime(f"{year}-W{week:02d}-1", "%G-W%V-%u")

        # Calculate Sunday (last day of the week)
        sunday = monday + timedelta(days=6)

        # Return as date range
        return f"{monday.strftime('%Y-%m-%d')}..{sunday.strftime('%Y-%m-%d')}"

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
        """Increment depth cyclically, wrapping to minimum after reaching maximum."""
        if self.depth + 1 > self.DEFAULT_DEPTH_MAX:
            self.depth = self.DEFAULT_DEPTH_MIN
            return
        self.depth += 1
