"""Pytest configuration and shared fixtures."""

import pytest

from hledger_tui.core.service import HLedger, HLedgerBackend


class MockHLedgerBackend(HLedgerBackend):
    """Reusable mock backend for testing."""

    def __init__(self):
        self.balance_calls = []
        self.register_calls = []
        self.stats_calls = []
        self.files_calls = []
        self.accounts_calls = []
        self.tags_calls = []
        self.commodities_calls = []

    def balance(self, queries: list[str], **kwargs) -> str:
        self.balance_calls.append((queries, kwargs))
        return """account,balance
expenses:food,€ 150.00
expenses:transport,€ 50.00
expenses:entertainment,€ 75.00"""

    def register(self, queries: list[str], **kwargs) -> str:
        self.register_calls.append((queries, kwargs))
        return """txnidx,date,description,account,amount,total
1,2024-01-01,Grocery Store,expenses:food,€ 50.00,€ 50.00
1,2024-01-01,Grocery Store,assets:checking,€ -50.00,€ -50.00"""

    def stats(self) -> str:
        self.stats_calls.append(True)
        return """Main file: /test/journal.ledger
Included files: 1
Transactions: 100"""

    def files(self) -> str:
        self.files_calls.append(True)
        return """/test/journal.ledger
/test/included.ledger"""

    def accounts(self, queries: list[str]) -> str:
        self.accounts_calls.append(queries)
        return """expenses:food
expenses:transport
assets:checking"""

    def tags(self, **kwargs) -> str:
        self.tags_calls.append(kwargs)
        return """project
category
client"""

    def commodities(self) -> str:
        self.commodities_calls.append(True)
        return """€
$
£"""


@pytest.fixture
def mock_backend():
    """Provide a fresh mock backend for each test."""
    return MockHLedgerBackend()


@pytest.fixture
def hledger_with_mock(mock_backend):
    """Provide an HLedger instance with mock backend."""
    return HLedger(backend=mock_backend)


@pytest.fixture
def sample_balance_csv():
    """Provide sample balance CSV data."""
    return """account,balance
expenses:food,€ 150.00
expenses:transport,€ 50.00
assets:checking,€ 1000.00
liabilities:credit-card,€ -200.00"""


@pytest.fixture
def sample_register_csv():
    """Provide sample register CSV data."""
    return """txnidx,date,description,account,amount,total
1,2024-01-01,Grocery Store,expenses:food,€ 50.00,€ 50.00
1,2024-01-01,Grocery Store,assets:checking,€ -50.00,€ -50.00
2,2024-01-02,Gas Station,expenses:transport,€ 30.00,€ 30.00
2,2024-01-02,Gas Station,assets:checking,€ -30.00,€ -30.00
3,2024-01-03,Restaurant,expenses:food,€ 25.00,€ 75.00
3,2024-01-03,Restaurant,assets:checking,€ -25.00,€ -75.00"""


@pytest.fixture
def sample_historical_balance_csv():
    """Provide sample historical balance CSV data."""
    return """account,2024-01,2024-02,2024-03
expenses:food,€ 100.00,€ 150.00,€ 200.00
expenses:transport,€ 50.00,€ 75.00,€ 100.00"""
