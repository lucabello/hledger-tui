"""Tests for HLedger service with mocked backend."""

from hledger_tui.core.models import CategoricalBalance, Transaction
from hledger_tui.core.service import HLedger


class TestHLedgerBalance:
    """Test HLedger balance queries."""

    def test_balance_query_basic(self, hledger_with_mock, mock_backend):
        """Test basic balance query."""
        hledger = hledger_with_mock

        balances = hledger.balance()

        assert len(balances) == 3
        assert isinstance(balances[0], CategoricalBalance)
        # Sorted by name
        assert balances[0].name == "expenses:entertainment"
        assert balances[1].name == "expenses:food"
        assert balances[2].name == "expenses:transport"

    def test_balance_query_with_custom_queries(self, hledger_with_mock, mock_backend):
        """Test balance query with custom queries."""
        hledger = hledger_with_mock

        hledger.balance(queries=["acct:food"])

        assert len(mock_backend.balance_calls) == 1
        queries, kwargs = mock_backend.balance_calls[0]
        assert queries == ["acct:food"]

    def test_balance_query_respects_depth(self, hledger_with_mock, mock_backend):
        """Test that balance query includes depth parameter."""
        hledger = hledger_with_mock
        hledger.depth = 3

        hledger.balance()

        queries, kwargs = mock_backend.balance_calls[0]
        assert kwargs["depth"] == 3

    def test_balance_query_respects_period(self, hledger_with_mock, mock_backend):
        """Test that balance query includes period parameter."""
        hledger = hledger_with_mock
        hledger.period.previous_period()

        hledger.balance()

        queries, kwargs = mock_backend.balance_calls[0]
        assert "period" in kwargs
        assert kwargs["period"] == "1 month ago"

    def test_balance_query_all_time_no_period(self, hledger_with_mock, mock_backend):
        """Test that all-time period doesn't include period parameter."""
        hledger = hledger_with_mock
        hledger.period.unit = None

        hledger.balance()

        queries, kwargs = mock_backend.balance_calls[0]
        assert "period" not in kwargs


class TestHLedgerRegister:
    """Test HLedger register queries."""

    def test_register_query_basic(self, hledger_with_mock, mock_backend):
        """Test basic register query."""
        hledger = hledger_with_mock

        transactions = hledger.register(account="expenses:food")

        assert len(transactions) == 1
        assert isinstance(transactions[0], Transaction)
        assert transactions[0].description == "Grocery Store"
        assert len(transactions[0].postings) == 2

    def test_register_query_with_tag(self, hledger_with_mock, mock_backend):
        """Test register query with tag filter."""
        hledger = hledger_with_mock

        hledger.register(account="expenses:food", tag="project:vacation")

        queries, kwargs = mock_backend.register_calls[0]
        assert "expenses:food" in queries
        assert "project:vacation" in queries

    def test_register_query_with_period(self, hledger_with_mock, mock_backend):
        """Test register query with explicit period."""
        hledger = hledger_with_mock

        hledger.register(account="expenses:food", period="2024-01")

        queries, kwargs = mock_backend.register_calls[0]
        assert kwargs["period"] == "2024-01"

    def test_register_query_empty_period_skips_filter(self, hledger_with_mock, mock_backend):
        """Test register query with empty period string."""
        hledger = hledger_with_mock

        hledger.register(account="expenses:food", period="")

        queries, kwargs = mock_backend.register_calls[0]
        assert "period" not in kwargs


class TestHLedgerDepth:
    """Test HLedger depth management."""

    def test_default_depth(self, hledger_with_mock):
        """Test default depth value."""
        hledger = hledger_with_mock
        assert hledger.depth == 2

    def test_cycle_depth_increments(self, hledger_with_mock):
        """Test depth cycling increments correctly."""
        hledger = hledger_with_mock

        hledger.cycle_depth()
        assert hledger.depth == 3

        hledger.cycle_depth()
        assert hledger.depth == 4

    def test_cycle_depth_wraps_at_max(self, hledger_with_mock):
        """Test depth cycling wraps to minimum at max."""
        hledger = hledger_with_mock
        hledger.depth = 4  # Set to max

        hledger.cycle_depth()
        assert hledger.depth == 1  # Wraps to min


class TestHLedgerBackendCalls:
    """Test HLedger backend method calls."""

    def test_tags_parsed_correctly(self, hledger_with_mock, mock_backend):
        """Test that tags are parsed from backend response."""
        hledger = hledger_with_mock
        # Access the tags through the instance method which uses the mock
        tags = hledger.backend.tags()

        assert mock_backend.tags_calls
        assert "project" in tags
        assert "category" in tags
        assert "client" in tags

    def test_stats_called(self, hledger_with_mock, mock_backend):
        """Test that stats method calls backend."""
        hledger = hledger_with_mock
        stats = hledger.backend.stats()

        assert mock_backend.stats_calls
        assert "Transactions" in stats

    def test_files_parsed_correctly(self, hledger_with_mock, mock_backend):
        """Test that files are parsed from backend response."""
        hledger = hledger_with_mock
        files = hledger.backend.files()

        assert mock_backend.files_calls
        assert "/test/journal.ledger" in files
        assert "/test/included.ledger" in files

    def test_accounts_queried_correctly(self, hledger_with_mock, mock_backend):
        """Test that accounts method passes queries to backend."""
        hledger = hledger_with_mock
        accounts = hledger.backend.accounts(["expenses"])

        assert len(mock_backend.accounts_calls) == 1
        assert mock_backend.accounts_calls[0] == ["expenses"]
        assert "expenses:food" in accounts

    def test_commodities_parsed_correctly(self, hledger_with_mock, mock_backend):
        """Test that commodities are parsed from backend response."""
        hledger = hledger_with_mock
        commodities = hledger.backend.commodities()

        assert mock_backend.commodities_calls
        assert "€" in commodities
        assert "$" in commodities
        assert "£" in commodities


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


class TestHLedgerCurrencyConversion:
    """Test currency conversion behavior with HLEDGER_TUI_COMMODITY."""

    def test_empty_commodity_uses_market_conversion(self, monkeypatch):
        """Test that empty commodity uses --market flag."""
        monkeypatch.setenv("HLEDGER_TUI_COMMODITY", "")

        # Import and reload modules to pick up new config
        import importlib

        from hledger_tui import config as config_module

        importlib.reload(config_module)
        from hledger_tui.core import models as models_module

        importlib.reload(models_module)
        from hledger_tui.core import service as service_module

        importlib.reload(service_module)

        from conftest import MockHLedgerBackend

        mock_backend = MockHLedgerBackend()
        hledger = service_module.HLedger(backend=mock_backend)

        hledger.balance()

        queries, kwargs = mock_backend.balance_calls[0]
        assert "market" in kwargs
        assert kwargs["market"] is True
        assert "exchange" not in kwargs

    def test_set_commodity_uses_exchange_conversion(self, monkeypatch):
        """Test that set commodity uses --exchange flag."""
        monkeypatch.setenv("HLEDGER_TUI_COMMODITY", "€")

        # Import and reload modules to pick up new config
        import importlib

        from hledger_tui import config as config_module

        importlib.reload(config_module)
        from hledger_tui.core import models as models_module

        importlib.reload(models_module)
        from hledger_tui.core import service as service_module

        importlib.reload(service_module)

        from conftest import MockHLedgerBackend

        mock_backend = MockHLedgerBackend()
        hledger = service_module.HLedger(backend=mock_backend)

        hledger.balance()

        queries, kwargs = mock_backend.balance_calls[0]
        assert "exchange" in kwargs
        assert kwargs["exchange"] == "€"
        assert "market" not in kwargs

    def test_invalid_commodity_raises_error(self, monkeypatch):
        """Test that invalid commodity raises ValueError."""
        import pytest

        monkeypatch.setenv("HLEDGER_TUI_COMMODITY", "INVALID")

        # Import and reload modules to pick up new config
        import importlib

        from hledger_tui import config as config_module

        importlib.reload(config_module)
        from hledger_tui.core import models as models_module

        importlib.reload(models_module)
        from hledger_tui.core import service as service_module

        importlib.reload(service_module)

        from conftest import MockHLedgerBackend

        mock_backend = MockHLedgerBackend()
        hledger = service_module.HLedger(backend=mock_backend)

        with pytest.raises(ValueError, match="not declared in journal"):
            hledger.balance()

    def test_currency_conversion_in_all_balance_methods(self, monkeypatch):
        """Test that currency conversion is applied to all balance methods."""
        monkeypatch.setenv("HLEDGER_TUI_COMMODITY", "$")

        # Import and reload modules to pick up new config
        import importlib

        from hledger_tui import config as config_module

        importlib.reload(config_module)
        from hledger_tui.core import models as models_module

        importlib.reload(models_module)
        from hledger_tui.core import service as service_module

        importlib.reload(service_module)

        from conftest import MockHLedgerBackend

        mock_backend = MockHLedgerBackend()
        hledger = service_module.HLedger(backend=mock_backend)

        # Test balance()
        hledger.balance()
        assert mock_backend.balance_calls[0][1]["exchange"] == "$"

        # Test tag_balance()
        hledger.tag_balance("test")
        assert mock_backend.balance_calls[1][1]["exchange"] == "$"

    def test_currency_conversion_in_register(self, monkeypatch):
        """Test that currency conversion is applied to register method."""
        monkeypatch.setenv("HLEDGER_TUI_COMMODITY", "£")

        # Import and reload modules to pick up new config
        import importlib

        from hledger_tui import config as config_module

        importlib.reload(config_module)
        from hledger_tui.core import models as models_module

        importlib.reload(models_module)
        from hledger_tui.core import service as service_module

        importlib.reload(service_module)

        from conftest import MockHLedgerBackend

        mock_backend = MockHLedgerBackend()
        hledger = service_module.HLedger(backend=mock_backend)

        hledger.register("expenses:food")

        queries, kwargs = mock_backend.register_calls[0]
        assert "exchange" in kwargs
        assert kwargs["exchange"] == "£"

    def test_declared_commodities_cached(self, monkeypatch):
        """Test that declared commodities are cached after first validation."""
        monkeypatch.setenv("HLEDGER_TUI_COMMODITY", "€")

        # Import and reload modules to pick up new config
        import importlib

        from hledger_tui import config as config_module

        importlib.reload(config_module)
        from hledger_tui.core import models as models_module

        importlib.reload(models_module)
        from hledger_tui.core import service as service_module

        importlib.reload(service_module)

        from conftest import MockHLedgerBackend

        mock_backend = MockHLedgerBackend()
        hledger = service_module.HLedger(backend=mock_backend)

        # First call should fetch commodities
        hledger.balance()
        first_commodity_calls = len(
            [c for c in mock_backend.commodities_calls if c.get("declared")]
        )

        # Second call should use cache
        hledger.balance()
        second_commodity_calls = len(
            [c for c in mock_backend.commodities_calls if c.get("declared")]
        )

        # Should only call once
        assert first_commodity_calls == 1
        assert second_commodity_calls == 1  # Still 1, not 2


class TestHLedgerExtraOptions:
    """Test extra options functionality."""

    def test_parse_extra_options_boolean_flags(self):
        """Test parsing boolean flags like --cost."""
        options = ["--cost", "--no-total"]

        result = HLedger._parse_extra_options(options)

        assert result == {"cost": True, "no_total": True}

    def test_parse_extra_options_key_value_pairs(self):
        """Test parsing key-value pairs like --depth 3."""
        options = ["--depth", "3", "--exchange", "USD"]

        result = HLedger._parse_extra_options(options)

        assert result == {"depth": "3", "exchange": "USD"}

    def test_parse_extra_options_mixed(self):
        """Test parsing mix of flags and key-value pairs."""
        options = ["--cost", "--depth", "4", "--no-total"]

        result = HLedger._parse_extra_options(options)

        assert result == {"cost": True, "depth": "4", "no_total": True}

    def test_parse_extra_options_short_flags(self):
        """Test parsing short flags like -V."""
        options = ["-V", "-b", "2024-01-01"]

        result = HLedger._parse_extra_options(options)

        assert result == {"V": True, "b": "2024-01-01"}

    def test_parse_extra_options_empty_list(self):
        """Test parsing empty options list."""
        options = []

        result = HLedger._parse_extra_options(options)

        assert result == {}

    def test_balance_with_extra_options(self, hledger_with_mock, mock_backend, monkeypatch):
        """Test that extra balance options are passed to backend."""
        monkeypatch.setenv("HLEDGER_TUI_EXTRA_OPTIONS_BALANCE", "--cost --depth 5")

        # Reload config to pick up env var
        import importlib

        from hledger_tui import config as config_module

        importlib.reload(config_module)
        from hledger_tui.core import service as service_module

        importlib.reload(service_module)

        from conftest import MockHLedgerBackend

        mock_backend = MockHLedgerBackend()
        hledger = service_module.HLedger(backend=mock_backend)

        hledger.balance()

        queries, kwargs = mock_backend.balance_calls[0]
        assert kwargs["cost"] is True
        assert kwargs["depth"] == "5"

    def test_register_with_extra_options(self, hledger_with_mock, mock_backend, monkeypatch):
        """Test that extra register options are passed to backend."""
        monkeypatch.setenv("HLEDGER_TUI_EXTRA_OPTIONS_REGISTER", "--related --cost")

        # Reload config to pick up env var
        import importlib

        from hledger_tui import config as config_module

        importlib.reload(config_module)
        from hledger_tui.core import service as service_module

        importlib.reload(service_module)

        from conftest import MockHLedgerBackend

        mock_backend = MockHLedgerBackend()
        hledger = service_module.HLedger(backend=mock_backend)

        hledger.register("expenses:food")

        queries, kwargs = mock_backend.register_calls[0]
        assert kwargs["related"] is True
        assert kwargs["cost"] is True

    def test_extra_options_override_defaults(self, hledger_with_mock, mock_backend, monkeypatch):
        """Test that extra options can override default settings."""
        monkeypatch.setenv("HLEDGER_TUI_EXTRA_OPTIONS_BALANCE", "--depth 10")

        # Reload config to pick up env var
        import importlib

        from hledger_tui import config as config_module

        importlib.reload(config_module)
        from hledger_tui.core import service as service_module

        importlib.reload(service_module)

        from conftest import MockHLedgerBackend

        mock_backend = MockHLedgerBackend()
        hledger = service_module.HLedger(backend=mock_backend)
        hledger.depth = 2  # Set a default depth

        hledger.balance()

        queries, kwargs = mock_backend.balance_calls[0]
        # Extra option should override
        assert kwargs["depth"] == "10"

    def test_assets_with_extra_options(self, hledger_with_mock, mock_backend, monkeypatch):
        """Test that extra balance options are applied to assets method."""
        monkeypatch.setenv("HLEDGER_TUI_EXTRA_OPTIONS_BALANCE", "--cost")

        # Reload config to pick up env var
        import importlib

        from hledger_tui import config as config_module

        importlib.reload(config_module)
        from hledger_tui.core import service as service_module

        importlib.reload(service_module)

        from conftest import MockHLedgerBackend

        mock_backend = MockHLedgerBackend()
        hledger = service_module.HLedger(backend=mock_backend)

        hledger.assets()

        queries, kwargs = mock_backend.balance_calls[0]
        assert kwargs["cost"] is True

    def test_balance_over_time_with_extra_options(
        self, hledger_with_mock, mock_backend, monkeypatch
    ):
        """Test that extra balance options are applied to balance_over_time method."""
        monkeypatch.setenv("HLEDGER_TUI_EXTRA_OPTIONS_BALANCE", "--cost")

        # Reload config to pick up env var
        import importlib

        from hledger_tui import config as config_module

        importlib.reload(config_module)
        from hledger_tui.core import service as service_module

        importlib.reload(service_module)

        from conftest import MockHLedgerBackend

        mock_backend = MockHLedgerBackend()
        hledger = service_module.HLedger(backend=mock_backend)

        hledger.balance_over_time("expenses:food")

        queries, kwargs = mock_backend.balance_calls[0]
        assert kwargs["cost"] is True
