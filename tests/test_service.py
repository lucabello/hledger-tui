"""Tests for HLedger service with mocked backend."""

from hledger_tui.core.models import CategoricalBalance, Transaction
from hledger_tui.core.service import HLedger, HLedgerBackend


class MockHLedgerBackend(HLedgerBackend):
    """Mock backend for testing."""

    def __init__(self):
        self.balance_calls = []
        self.register_calls = []

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
1,2024-01-01,Grocery Store,assets:checking,€ -50.00,€ -50.00
2,2024-01-02,Gas Station,expenses:transport,€ 30.00,€ 30.00
2,2024-01-02,Gas Station,assets:checking,€ -30.00,€ -30.00"""

    def stats(self) -> str:
        return "Main file: test.ledger"

    def files(self) -> str:
        return "test.ledger\nincluded.ledger"

    def accounts(self, queries: list[str]) -> str:
        return "expenses:food\nexpenses:transport\nassets:checking"

    def tags(self, **kwargs) -> str:
        return "project\ncategory"

    def commodities(self) -> str:
        return "€\n$"


class TestHLedgerBalance:
    """Test HLedger balance queries."""

    def test_balance_query_basic(self):
        """Test basic balance query."""
        backend = MockHLedgerBackend()
        hledger = HLedger(backend=backend)

        balances = hledger.balance()

        assert len(balances) == 3
        assert isinstance(balances[0], CategoricalBalance)
        # Sorted by name
        assert balances[0].name == "expenses:entertainment"
        assert balances[1].name == "expenses:food"
        assert balances[2].name == "expenses:transport"

    def test_balance_query_with_custom_queries(self):
        """Test balance query with custom queries."""
        backend = MockHLedgerBackend()
        hledger = HLedger(backend=backend)

        balances = hledger.balance(queries=["acct:food"])

        assert len(backend.balance_calls) == 1
        queries, kwargs = backend.balance_calls[0]
        assert queries == ["acct:food"]

    def test_balance_query_respects_depth(self):
        """Test that balance query includes depth parameter."""
        backend = MockHLedgerBackend()
        hledger = HLedger(backend=backend)
        hledger.depth = 3

        hledger.balance()

        queries, kwargs = backend.balance_calls[0]
        assert kwargs["depth"] == 3

    def test_balance_query_respects_period(self):
        """Test that balance query includes period parameter."""
        backend = MockHLedgerBackend()
        hledger = HLedger(backend=backend)
        hledger.period.previous_period()

        hledger.balance()

        queries, kwargs = backend.balance_calls[0]
        assert "period" in kwargs
        assert kwargs["period"] == "1 month ago"

    def test_balance_query_all_time_no_period(self):
        """Test that all-time period doesn't include period parameter."""
        backend = MockHLedgerBackend()
        hledger = HLedger(backend=backend)
        hledger.period.unit = None

        hledger.balance()

        queries, kwargs = backend.balance_calls[0]
        assert "period" not in kwargs


class TestHLedgerRegister:
    """Test HLedger register queries."""

    def test_register_query_basic(self):
        """Test basic register query."""
        backend = MockHLedgerBackend()
        hledger = HLedger(backend=backend)

        transactions = hledger.register(account="expenses:food")

        assert len(transactions) == 2
        assert isinstance(transactions[0], Transaction)
        assert transactions[0].description == "Grocery Store"
        assert len(transactions[0].postings) == 2

    def test_register_query_with_tag(self):
        """Test register query with tag filter."""
        backend = MockHLedgerBackend()
        hledger = HLedger(backend=backend)

        transactions = hledger.register(account="expenses:food", tag="project:vacation")

        queries, kwargs = backend.register_calls[0]
        assert "expenses:food" in queries
        assert "project:vacation" in queries

    def test_register_query_with_period(self):
        """Test register query with explicit period."""
        backend = MockHLedgerBackend()
        hledger = HLedger(backend=backend)

        transactions = hledger.register(account="expenses:food", period="2024-01")

        queries, kwargs = backend.register_calls[0]
        assert kwargs["period"] == "2024-01"

    def test_register_query_empty_period_skips_filter(self):
        """Test register query with empty period string."""
        backend = MockHLedgerBackend()
        hledger = HLedger(backend=backend)

        transactions = hledger.register(account="expenses:food", period="")

        queries, kwargs = backend.register_calls[0]
        assert "period" not in kwargs


class TestHLedgerDepth:
    """Test HLedger depth management."""

    def test_default_depth(self):
        """Test default depth value."""
        backend = MockHLedgerBackend()
        hledger = HLedger(backend=backend)
        assert hledger.depth == 2

    def test_cycle_depth_increments(self):
        """Test depth cycling increments correctly."""
        backend = MockHLedgerBackend()
        hledger = HLedger(backend=backend)

        hledger.cycle_depth()
        assert hledger.depth == 3

        hledger.cycle_depth()
        assert hledger.depth == 4

    def test_cycle_depth_wraps_at_max(self):
        """Test depth cycling wraps to minimum at max."""
        backend = MockHLedgerBackend()
        hledger = HLedger(backend=backend)
        hledger.depth = 4  # Set to max

        hledger.cycle_depth()
        assert hledger.depth == 1  # Wraps to min


class TestHLedgerStaticMethods:
    """Test HLedger static utility methods."""

    def test_tags_static_method(self):
        """Test static tags method."""
        tags = HLedger.tags()
        assert isinstance(tags, list)

    def test_stats_static_method(self):
        """Test static stats method."""
        stats = HLedger.stats()
        assert isinstance(stats, str)

    def test_files_static_method(self):
        """Test static files method."""
        files = HLedger.files()
        assert isinstance(files, list)

    def test_all_accounts_static_method(self):
        """Test static all_accounts method."""
        accounts = HLedger.all_accounts()
        assert isinstance(accounts, list)

    def test_commodities_static_method(self):
        """Test static commodities method."""
        commodities = HLedger.commodities()
        assert isinstance(commodities, list)


class TestHLedgerWeekPeriodConversion:
    """Test ISO week period conversion."""

    def test_convert_week_period_iso_format(self):
        """Test converting ISO week format."""
        result = HLedger._convert_week_period("2024-W01")
        assert ".." in result  # Should be a date range
        assert "2024-01-01" in result

    def test_convert_week_period_non_iso_unchanged(self):
        """Test that non-ISO format is unchanged."""
        result = HLedger._convert_week_period("2024-01")
        assert result == "2024-01"

    def test_convert_week_period_regular_date(self):
        """Test that regular dates are unchanged."""
        result = HLedger._convert_week_period("2024-01-15")
        assert result == "2024-01-15"


class TestHLedgerParseRegisterCSV:
    """Test register CSV parsing."""

    def test_parse_register_csv_single_transaction(self):
        """Test parsing single transaction."""
        csv_data = """txnidx,date,description,account,amount,total
1,2024-01-01,Test,expenses:food,€ 50.00,€ 50.00
1,2024-01-01,Test,assets:checking,€ -50.00,€ -50.00"""

        transactions = HLedger._parse_register_csv(csv_data)

        assert len(transactions) == 1
        assert transactions[0].txnidx == "1"
        assert transactions[0].date == "2024-01-01"
        assert transactions[0].description == "Test"
        assert len(transactions[0].postings) == 2

    def test_parse_register_csv_multiple_transactions(self):
        """Test parsing multiple transactions."""
        csv_data = """txnidx,date,description,account,amount,total
1,2024-01-01,Test1,expenses:food,€ 50.00,€ 50.00
2,2024-01-02,Test2,expenses:transport,€ 30.00,€ 30.00"""

        transactions = HLedger._parse_register_csv(csv_data)

        assert len(transactions) == 2
        assert transactions[0].txnidx == "1"
        assert transactions[1].txnidx == "2"

    def test_parse_register_csv_empty(self):
        """Test parsing empty CSV."""
        csv_data = """txnidx,date,description,account,amount,total"""

        transactions = HLedger._parse_register_csv(csv_data)

        assert len(transactions) == 0
