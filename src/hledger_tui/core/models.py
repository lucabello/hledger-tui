"""Data models for HLedger TUI application."""

from dataclasses import dataclass
from typing import ClassVar, List

from hledger_tui.config import config


@dataclass
class CategoricalBalance:
    """Balance data point with a category name and amount including currency."""

    DEFAULT_COMMODITY: ClassVar[str] = config.default_commodity

    name: str
    _balance: str

    @property
    def balance(self) -> str:
        if self._balance == "0":
            return f"{self.DEFAULT_COMMODITY} 0"
        return self._balance

    @property
    def commodity(self) -> str:
        """Extract currency/commodity symbol from balance string.

        Handles both formats:
        - Symbol first: € 12, $ 100.50
        - Symbol last: 12 EUR, 100.50 USD
        """
        parts = self.balance.split()
        if len(parts) == 0:
            return self.DEFAULT_COMMODITY

        # Check if first part is numeric (possibly with sign, decimals, commas)
        first_part = parts[0].lstrip("-+").replace(",", "").replace(".", "")
        if first_part.isdigit():
            # Numeric first means commodity is last
            return parts[-1] if len(parts) > 1 else self.DEFAULT_COMMODITY
        else:
            # Non-numeric first means commodity is first
            return parts[0]

    @property
    def balance_float(self) -> float:
        return float(self.balance.split()[-1])


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
