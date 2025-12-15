"""Tests for configuration management."""

import os
import pytest

from hledger_tui.config import HLedgerConfig


class TestHLedgerConfigFromEnv:
    """Test loading configuration from environment variables."""

    def test_config_from_env_with_custom_queries(self, monkeypatch):
        """Test that from_env() loads custom queries from environment variables."""
        monkeypatch.setenv("HLEDGER_TUI_QUERIES", "acct:custom,not:acct:skip")

        config = HLedgerConfig.from_env()

        assert config.default_queries == ["acct:custom", "not:acct:skip"]

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
        monkeypatch.delenv("HLEDGER_TUI_QUERIES", raising=False)
        monkeypatch.delenv("HLEDGER_TUI_DEPTH", raising=False)
        monkeypatch.delenv("HLEDGER_TUI_COMMODITY", raising=False)

        config = HLedgerConfig.from_env()

        # Should use defaults
        assert "acct:expenses" in config.default_queries
        assert config.default_depth == 2
        assert config.default_commodity == "€"

    def test_config_from_env_strips_whitespace_from_queries(self, monkeypatch):
        """Test that query strings are properly stripped of whitespace."""
        monkeypatch.setenv("HLEDGER_TUI_QUERIES", "acct:expenses , not:acct:test , acct:other")

        config = HLedgerConfig.from_env()

        # All queries should be stripped
        assert config.default_queries == ["acct:expenses", "not:acct:test", "acct:other"]

    def test_config_queries_are_mutable_list(self):
        """Test that queries lists are mutable."""
        config = HLedgerConfig()
        original_length = len(config.default_queries)
        config.default_queries.append("acct:new")
        assert len(config.default_queries) == original_length + 1

    def test_config_default_factory(self):
        """Test that field defaults use factory functions."""
        config1 = HLedgerConfig()
        config2 = HLedgerConfig()

        # Lists should be separate instances
        config1.default_queries.append("test")
        assert len(config1.default_queries) != len(config2.default_queries)
