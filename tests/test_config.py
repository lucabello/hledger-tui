"""Tests for configuration management."""

import pytest
from dataconfy import EnvVarError

from hledger_tui.config import HLedgerConfig


class TestHLedgerConfigFromEnv:
    """Test loading configuration from environment variables."""

    def test_config_from_env_with_custom_queries(self, monkeypatch):
        """Test that from_env() loads custom queries from environment variables."""
        monkeypatch.setenv("HLEDGER_TUI_QUERIES_EXPENSES", '["acct:custom", "not:acct:skip"]')

        config = HLedgerConfig.from_env()

        assert config.queries.expenses == ["acct:custom", "not:acct:skip"]

    def test_config_from_env_with_custom_depth(self, monkeypatch):
        """Test that from_env() loads custom depth from environment variables."""
        monkeypatch.setenv("HLEDGER_TUI_DEPTH", "5")

        config = HLedgerConfig.from_env()

        assert config.depth == 5

    def test_config_from_env_with_invalid_depth(self, monkeypatch):
        """Test that from_env() raises error for invalid depth values."""
        monkeypatch.setenv("HLEDGER_TUI_DEPTH", "not_a_number")

        with pytest.raises(EnvVarError):
            HLedgerConfig.from_env()

    def test_config_from_env_with_custom_commodity(self, monkeypatch):
        """Test that from_env() loads custom commodity from environment variables."""
        monkeypatch.setenv("HLEDGER_TUI_COMMODITY", "$")

        config = HLedgerConfig.from_env()

        assert config.commodity == "$"

    def test_config_from_env_with_no_env_vars(self, monkeypatch, tmp_path):
        """Test that from_env() uses defaults when no environment variables are set."""
        # Clear any relevant env vars
        monkeypatch.delenv("HLEDGER_TUI_QUERIES_EXPENSES", raising=False)
        monkeypatch.delenv("HLEDGER_TUI_DEPTH", raising=False)
        monkeypatch.delenv("HLEDGER_TUI_COMMODITY", raising=False)
        
        # Point config to a non-existent directory to prevent loading user's config file
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

        config = HLedgerConfig.from_env()

        # Should use defaults
        assert "acct:expenses" in config.queries.expenses
        assert config.depth == 2
        assert config.commodity is None

    def test_config_from_env_with_multiple_queries(self, monkeypatch):
        """Test that multiple queries are properly loaded from JSON array."""
        monkeypatch.setenv(
            "HLEDGER_TUI_QUERIES_EXPENSES",
            '["acct:expenses", "not:acct:test", "acct:other"]',
        )

        config = HLedgerConfig.from_env()

        assert config.queries.expenses == ["acct:expenses", "not:acct:test", "acct:other"]

    def test_config_queries_are_mutable_list(self):
        """Test that queries lists are mutable."""
        config = HLedgerConfig()
        original_length = len(config.queries.expenses)
        config.queries.expenses.append("acct:new")
        assert len(config.queries.expenses) == original_length + 1

    def test_config_default_factory(self):
        """Test that field defaults use factory functions."""
        config1 = HLedgerConfig()
        config2 = HLedgerConfig()

        # Lists should be separate instances
        config1.queries.expenses.append("test")
        assert len(config1.queries.expenses) != len(config2.queries.expenses)

    def test_config_from_env_with_extra_balance_options(self, monkeypatch):
        """Test that from_env() loads extra balance options from environment variables."""
        monkeypatch.setenv("HLEDGER_TUI_EXTRA_OPTIONS_BALANCE", '["--cost", "--depth", "5"]')

        config = HLedgerConfig.from_env()

        assert config.extra_options.balance == ["--cost", "--depth", "5"]

    def test_config_from_env_with_extra_register_options(self, monkeypatch):
        """Test that from_env() loads extra register options from environment variables."""
        monkeypatch.setenv("HLEDGER_TUI_EXTRA_OPTIONS_REGISTER", '["--related", "--cost"]')

        config = HLedgerConfig.from_env()

        assert config.extra_options.register == ["--related", "--cost"]

    def test_config_from_env_with_complex_extra_options(self, monkeypatch):
        """Test that extra options handle strings with spaces correctly."""
        monkeypatch.setenv(
            "HLEDGER_TUI_EXTRA_OPTIONS_BALANCE",
            '["--cost", "--format", "%(account) %(amount)"]',
        )

        config = HLedgerConfig.from_env()

        assert config.extra_options.balance == ["--cost", "--format", "%(account) %(amount)"]

    def test_config_from_env_extra_options_defaults_to_empty(self, monkeypatch):
        """Test that extra options default to empty list when not set."""
        monkeypatch.delenv("HLEDGER_TUI_EXTRA_OPTIONS_BALANCE", raising=False)
        monkeypatch.delenv("HLEDGER_TUI_EXTRA_OPTIONS_REGISTER", raising=False)

        config = HLedgerConfig.from_env()

        assert config.extra_options.balance == []
        assert config.extra_options.register == []
