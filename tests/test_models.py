"""Tests for core data models."""

import pytest

from hledger_tui.core.models import (
    AccountHistoricalBalance,
    CategoricalBalance,
    Posting,
    Transaction,
)


class TestCategoricalBalance:
    """Test CategoricalBalance model."""

    def test_balance_with_commodity(self):
        """Test balance formatting with explicit commodity."""
        balance = CategoricalBalance("expenses:food", "€ 150.00")
        assert balance.name == "expenses:food"
        assert balance.balance == "€ 150.00"
        assert balance.commodity == "€"
        assert balance.balance_float == 150.00

    def test_balance_zero_adds_default_commodity(self):
        """Test that zero balance gets default commodity."""
        balance = CategoricalBalance("expenses:food", "0")
        assert balance.balance == "€ 0"
        assert balance.commodity == "€"
        assert balance.balance_float == 0.0

    def test_balance_negative_value(self):
        """Test negative balance parsing."""
        balance = CategoricalBalance("assets:checking", "$ -500.00")
        assert balance.commodity == "$"
        assert balance.balance_float == -500.00

    def test_balance_with_large_number(self):
        """Test balance with thousands separator."""
        balance = CategoricalBalance("assets:investments", "€ 1,250.50")
        # Note: This will raise ValueError if not handled properly
        # Our current implementation doesn't handle commas
        with pytest.raises(ValueError):
            _ = balance.balance_float

    def test_balance_multiple_spaces(self):
        """Test balance with extra spaces."""
        balance = CategoricalBalance("test", "€   100.00")
        assert balance.balance_float == 100.00

    def test_commodity_symbol_first(self):
        """Test commodity extraction with symbol before amount."""
        balance = CategoricalBalance("test", "€ 100.00")
        assert balance.commodity == "€"

    def test_commodity_symbol_last(self):
        """Test commodity extraction with symbol after amount."""
        balance = CategoricalBalance("test", "100.00 EUR")
        assert balance.commodity == "EUR"

    def test_commodity_symbol_last_negative(self):
        """Test commodity extraction with symbol after negative amount."""
        balance = CategoricalBalance("test", "-50.25 USD")
        assert balance.commodity == "USD"

    def test_commodity_symbol_first_negative(self):
        """Test commodity extraction with symbol before negative amount."""
        balance = CategoricalBalance("test", "$ -75.50")
        assert balance.commodity == "$"

    def test_commodity_with_comma_separator(self):
        """Test commodity extraction with comma as thousands separator."""
        balance = CategoricalBalance("test", "1,250.00 GBP")
        assert balance.commodity == "GBP"

    def test_commodity_symbol_first_with_plus(self):
        """Test commodity extraction with plus sign."""
        balance = CategoricalBalance("test", "£ +200.00")
        assert balance.commodity == "£"


class TestPosting:
    """Test Posting model."""

    def test_posting_creation(self):
        """Test creating a posting."""
        posting = Posting(account="expenses:food", amount="€ 50.00", total="€ 50.00")
        assert posting.account == "expenses:food"
        assert posting.amount == "€ 50.00"
        assert posting.total == "€ 50.00"


class TestTransaction:
    """Test Transaction model."""

    def test_transaction_creation(self):
        """Test creating a transaction with postings."""
        postings = [
            Posting("expenses:food", "€ 50.00", "€ 50.00"),
            Posting("assets:checking", "€ -50.00", "€ -50.00"),
        ]
        transaction = Transaction(
            txnidx="1", date="2024-01-01", description="Grocery Store", postings=postings
        )
        assert transaction.txnidx == "1"
        assert transaction.date == "2024-01-01"
        assert transaction.description == "Grocery Store"
        assert len(transaction.postings) == 2

    def test_transaction_empty_postings(self):
        """Test transaction with no postings."""
        transaction = Transaction(txnidx="1", date="2024-01-01", description="Test", postings=[])
        assert len(transaction.postings) == 0


class TestAccountHistoricalBalance:
    """Test AccountHistoricalBalance model."""

    def test_historical_balance_creation(self):
        """Test creating historical balance data."""
        balances = [
            CategoricalBalance("2024-01", "€ 100.00"),
            CategoricalBalance("2024-02", "€ 150.00"),
            CategoricalBalance("2024-03", "€ 200.00"),
        ]
        hist_balance = AccountHistoricalBalance(name="expenses:food", balances=balances)
        assert hist_balance.name == "expenses:food"
        assert len(hist_balance.balances) == 3
        assert hist_balance.balances[0].balance_float == 100.00
        assert hist_balance.balances[-1].balance_float == 200.00

    def test_historical_balance_empty(self):
        """Test historical balance with no data."""
        hist_balance = AccountHistoricalBalance(name="expenses:food", balances=[])
        assert len(hist_balance.balances) == 0
