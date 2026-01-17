"""Data models for HLedger TUI application."""

from dataclasses import dataclass
from typing import ClassVar, List, Optional

from hledger_tui.core.parser import CommodityParser


@dataclass
class CategoricalBalance:
    """Balance data point with a category name and amount including currency."""

    DEFAULT_COMMODITY: ClassVar[Optional[str]] = None

    name: str
    _balance: str

    @property
    def balance(self) -> str:
        return self._balance

    @property
    def commodity(self) -> str:
        """Extract currency/commodity symbol from balance string.

        Supports multiple formats including:
        - Symbol first: € 12, $ 100.50, ₺1.904,22
        - Symbol last: 12 EUR, 100.50 USD, 1.000,00 EUR
        - Various separators: 1,000.00 (US), 1.000,00 (EU), 1 000 000,00 (spaces)
        """
        try:
            parsed = CommodityParser.parse(self.balance)
            return parsed.commodity if parsed.commodity else ""
        except ValueError:
            # Fallback to default if parsing fails
            return ""

    @property
    def balance_float(self) -> float:
        """Extract numeric value from balance string.

        Handles various commodity and number formats correctly.
        """
        try:
            parsed = CommodityParser.parse(self.balance)
            return parsed.numeric_value
        except ValueError:
            # If parsing fails, return 0
            return 0.0


@dataclass
class AccountHistoricalBalance:
    """Historical balance data for a single account across multiple periods."""

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
