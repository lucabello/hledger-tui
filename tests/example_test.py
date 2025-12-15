"""Example test demonstrating the testable architecture.

This file shows how the new backend abstraction enables easy testing
without requiring actual hledger installation or journal files.
"""

from hledger_tui.core import HLedger
from hledger_tui.core.service import HLedgerBackend


class MockHLedgerBackend(HLedgerBackend):
    """Mock backend for testing without actual hledger."""

    def balance(self, queries: list[str], **kwargs) -> str:
        """Return mock balance CSV data."""
        return """account,balance
expenses:food,€ 150.00
expenses:transport,€ 50.00
expenses:entertainment,€ 75.00"""

    def register(self, queries: list[str], **kwargs) -> str:
        """Return mock register CSV data."""
        return """txnidx,date,description,account,amount,total
1,2024-01-01,Grocery Store,expenses:food,€ 50.00,€ 50.00
1,2024-01-01,Grocery Store,assets:checking,€ -50.00,€ -50.00"""

    def stats(self) -> str:
        """Return mock stats output."""
        return """Main file: /mock/journal.ledger
Included files: 1
Transactions: 100
Accounts: 25"""

    def files(self) -> str:
        """Return mock files list."""
        return """/mock/journal.ledger
/mock/included.ledger"""

    def accounts(self, queries: list[str]) -> str:
        """Return mock accounts list."""
        return """expenses:food
expenses:transport
expenses:entertainment"""

    def tags(self, **kwargs) -> str:
        """Return mock tags list."""
        return """project
category
client"""

    def commodities(self) -> str:
        """Return mock commodities list."""
        return """€
$
£"""


def test_balance_query():
    """Test that balance queries work with mock backend."""
    # Create HLedger instance with mock backend
    backend = MockHLedgerBackend()
    hledger = HLedger(backend=backend)

    # Query balances
    balances = hledger.balance()

    # Verify results
    assert len(balances) == 3
    assert balances[0].name == "expenses:entertainment"
    assert balances[0].balance == "€ 75.00"
    assert balances[0].balance_float == 75.00
    print("✓ Balance query test passed")


def test_register_query():
    """Test that register queries work with mock backend."""
    backend = MockHLedgerBackend()
    hledger = HLedger(backend=backend)

    # Query transactions
    transactions = hledger.register(account="expenses:food")

    # Verify results
    assert len(transactions) == 1
    assert transactions[0].description == "Grocery Store"
    assert len(transactions[0].postings) == 2
    print("✓ Register query test passed")


def test_period_navigation():
    """Test period navigation without actual queries."""
    backend = MockHLedgerBackend()
    hledger = HLedger(backend=backend)

    # Test period navigation
    original_value = hledger.period.value
    hledger.period.next_period()
    assert hledger.period._offset == 1

    hledger.period.previous_period()
    assert hledger.period._offset == 0
    assert hledger.period.value == original_value
    print("✓ Period navigation test passed")


def test_depth_cycling():
    """Test depth cycling logic."""
    backend = MockHLedgerBackend()
    hledger = HLedger(backend=backend)

    # Test depth cycling
    assert hledger.depth == 2  # Default

    hledger.cycle_depth()
    assert hledger.depth == 3

    hledger.cycle_depth()
    assert hledger.depth == 4  # Max

    hledger.cycle_depth()
    assert hledger.depth == 1  # Wraps back to min
    print("✓ Depth cycling test passed")


if __name__ == "__main__":
    print("Running example tests with mock backend...\n")
    test_balance_query()
    test_register_query()
    test_period_navigation()
    test_depth_cycling()
    print("\n✅ All tests passed!")
    print("\nThis demonstrates how the refactored architecture enables testing")
    print("without requiring actual hledger installation or journal files.")
