"""Tests for configuration management."""

from hledger_tui.config import HLedgerConfig


class TestHLedgerConfigFromEnv:
    """Test loading configuration from environment variables."""

    def test_config_from_env_with_custom_queries(self, monkeypatch):
        """Test that from_env() loads custom queries from environment variables."""
        monkeypatch.setenv("HLEDGER_TUI_EXPENSE_QUERIES", "acct:custom,not:acct:skip")

        config = HLedgerConfig.from_env()

        assert config.default_expenses_queries == ["acct:custom", "not:acct:skip"]

    def test_config_from_env_with_custom_depth(self, monkeypatch):
        """Test that from_env() loads custom depth from environment variables."""
        monkeypatch.setenv("HLEDGER_TUI_DEPTH", "5")

        config = HLedgerConfig.from_env()

        assert config.default_depth == 5

    def test_config_from_env_with_invalid_depth(self, monkeypatch):
        """Test that from_env() ignores invalid depth values."""
        monkeypatch.setenv("HLEDGER_TUI_DEPTH", "not_a_number")

        config = HLedgerConfig.from_env()

        # Should fall back to default
        assert config.default_depth == 2

    def test_config_from_env_with_custom_commodity(self, monkeypatch):
        """Test that from_env() loads custom commodity from environment variables."""
        monkeypatch.setenv("HLEDGER_TUI_COMMODITY", "$")

        config = HLedgerConfig.from_env()

        assert config.default_commodity == "$"

    def test_config_from_env_with_no_env_vars(self, monkeypatch):
        """Test that from_env() uses defaults when no environment variables are set."""
        # Clear any relevant env vars
        monkeypatch.delenv("HLEDGER_TUI_EXPENSE_QUERIES", raising=False)
        monkeypatch.delenv("HLEDGER_TUI_DEPTH", raising=False)
        monkeypatch.delenv("HLEDGER_TUI_COMMODITY", raising=False)

        config = HLedgerConfig.from_env()

        # Should use defaults
        assert "acct:expenses" in config.default_expenses_queries
        assert config.default_depth == 2
        assert config.default_commodity == ""

    def test_config_from_env_strips_whitespace_from_queries(self, monkeypatch):
        """Test that query strings are properly stripped of whitespace."""
        monkeypatch.setenv(
            "HLEDGER_TUI_EXPENSE_QUERIES", "acct:expenses , not:acct:test , acct:other"
        )

        config = HLedgerConfig.from_env()

        # All queries should be stripped
        assert config.default_expenses_queries == ["acct:expenses", "not:acct:test", "acct:other"]

    def test_config_queries_are_mutable_list(self):
        """Test that queries lists are mutable."""
        config = HLedgerConfig()
        original_length = len(config.default_expenses_queries)
        config.default_expenses_queries.append("acct:new")
        assert len(config.default_expenses_queries) == original_length + 1

    def test_config_default_factory(self):
        """Test that field defaults use factory functions."""
        config1 = HLedgerConfig()
        config2 = HLedgerConfig()

        # Lists should be separate instances
        config1.default_expenses_queries.append("test")
        assert len(config1.default_expenses_queries) != len(config2.default_expenses_queries)

    def test_config_from_env_with_extra_balance_options(self, monkeypatch):
        """Test that from_env() loads extra balance options from environment variables."""
        monkeypatch.setenv("HLEDGER_TUI_EXTRA_OPTIONS_BALANCE", "--cost --depth 5")

        config = HLedgerConfig.from_env()

        assert config.extra_balance_options == ["--cost", "--depth", "5"]

    def test_config_from_env_with_extra_register_options(self, monkeypatch):
        """Test that from_env() loads extra register options from environment variables."""
        monkeypatch.setenv("HLEDGER_TUI_EXTRA_OPTIONS_REGISTER", "--related --cost")

        config = HLedgerConfig.from_env()

        assert config.extra_register_options == ["--related", "--cost"]

    def test_config_from_env_with_quoted_extra_options(self, monkeypatch):
        """Test that extra options handle quoted strings with spaces correctly."""
        monkeypatch.setenv(
            "HLEDGER_TUI_EXTRA_OPTIONS_BALANCE", '--cost --format "%(account) %(amount)"'
        )

        config = HLedgerConfig.from_env()

        assert config.extra_balance_options == ["--cost", "--format", "%(account) %(amount)"]

    def test_config_from_env_extra_options_defaults_to_empty(self, monkeypatch):
        """Test that extra options default to empty list when not set."""
        monkeypatch.delenv("HLEDGER_TUI_EXTRA_OPTIONS_BALANCE", raising=False)
        monkeypatch.delenv("HLEDGER_TUI_EXTRA_OPTIONS_REGISTER", raising=False)

        config = HLedgerConfig.from_env()

        assert config.extra_balance_options == []
        assert config.extra_register_options == []
